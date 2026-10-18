import { NextResponse } from "next/server";
import crypto from "crypto";
import { supabaseAdmin } from "@/lib/supabase-admin";

function hashPassword(password: string): string {
  return crypto.createHash("sha256").update(password).digest("hex");
}

export async function POST(req: Request) {
  try {
    const { identifier, password, otp_code } = await req.json();

    if (!identifier) {
      return NextResponse.json({ detail: "Identifier is required" }, { status: 400 });
    }

    const trimmedId = String(identifier).trim().toLowerCase();

    // ── 1. If OTP Code is provided for passwordless OTP login ─────────────────
    if (otp_code) {
      const cleanCode = String(otp_code).trim();
      const { data: record, error: otpErr } = await supabaseAdmin
        .from("otp_codes")
        .select("id, code, expires_at, destination")
        .eq("destination", trimmedId)
        .eq("code", cleanCode)
        .order("id", { ascending: false })
        .limit(1)
        .maybeSingle();

      if (otpErr || !record || new Date(record.expires_at).getTime() < Date.now()) {
        return NextResponse.json(
          { detail: "Invalid or expired verification code." },
          { status: 401 }
        );
      }

      // Cleanup OTP
      await supabaseAdmin.from("otp_codes").delete().eq("destination", trimmedId);

      // Check if user exists in DB
      let user: any = null;
      const { data: dbUser } = await supabaseAdmin
        .from("users")
        .select("id, username, email, phone, role, is_verified")
        .or(`email.ilike.${trimmedId},phone.ilike.${trimmedId},username.ilike.${trimmedId}`)
        .limit(1)
        .maybeSingle();

      if (dbUser) {
        user = dbUser;
      } else {
        // Auto-provision verified user for this verified destination
        const tempUsername = trimmedId.includes("@")
          ? trimmedId.split("@")[0].replace(/[^a-zA-Z0-9_]/g, "")
          : `user_${trimmedId.slice(-4)}`;

        const { data: created } = await supabaseAdmin
          .from("users")
          .insert({
            username: tempUsername || `user_${Date.now().toString().slice(-5)}`,
            email: trimmedId.includes("@") ? trimmedId : `${trimmedId}@visionlytics.local`,
            phone: trimmedId.includes("@") ? null : trimmedId,
            hashed_password: hashPassword("Visionlytics@OTP!2026"),
            role: "user",
            is_verified: true,
          })
          .select("id, username, email, phone, role, is_verified")
          .single();

        user = created || {
          id: Date.now(),
          username: tempUsername,
          email: trimmedId,
          role: "user",
          is_verified: true,
        };
      }

      return NextResponse.json({
        access_token: `token_${Buffer.from(JSON.stringify(user)).toString("base64")}`,
        token_type: "bearer",
        user,
      });
    }

    // ── 2. Password-based Login ──────────────────────────────────────────────
    if (!password) {
      return NextResponse.json({ detail: "Password is required" }, { status: 400 });
    }

    const hashed = hashPassword(password);

    // Direct check for admin credentials fallback
    if (
      (trimmedId === "lightningspeed.flh@gmail.com" || trimmedId === "admin") &&
      password === "sydney@2026"
    ) {
      const user = {
        id: 1,
        username: "admin",
        email: "lightningspeed.flh@gmail.com",
        role: "admin",
        is_verified: true,
      };
      return NextResponse.json({
        access_token: `admin_token_${Buffer.from(JSON.stringify(user)).toString("base64")}`,
        token_type: "bearer",
        user,
      });
    }

    // Try Supabase users table
    try {
      const { data: dbUser, error } = await supabaseAdmin
        .from("users")
        .select("*")
        .or(`email.ilike.${trimmedId},username.ilike.${trimmedId},phone.ilike.${trimmedId}`)
        .limit(1)
        .maybeSingle();

      if (!error && dbUser) {
        if (dbUser.hashed_password !== hashed) {
          return NextResponse.json({ detail: "Invalid credentials" }, { status: 401 });
        }

        const safeUser = {
          id: dbUser.id,
          username: dbUser.username,
          email: dbUser.email,
          phone: dbUser.phone,
          role: dbUser.role || "user",
          is_verified: Boolean(dbUser.is_verified),
        };

        return NextResponse.json({
          access_token: `token_${Buffer.from(JSON.stringify(safeUser)).toString("base64")}`,
          token_type: "bearer",
          user: safeUser,
        });
      }
    } catch {
      // Supabase table query fallback
    }

    return NextResponse.json({ detail: "Invalid email/username or password" }, { status: 401 });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Internal authentication error";
    return NextResponse.json({ detail: msg }, { status: 500 });
  }
}
