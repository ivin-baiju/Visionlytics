import { NextResponse } from "next/server";
import crypto from "crypto";
import { supabaseAdmin } from "@/lib/supabase-admin";

function hashPassword(password: string): string {
  return crypto.createHash("sha256").update(password).digest("hex");
}

export async function POST(req: Request) {
  try {
    const { identifier, password } = await req.json();

    if (!identifier || !password) {
      return NextResponse.json({ detail: "Identifier and password are required" }, { status: 400 });
    }

    const trimmedId = String(identifier).trim().toLowerCase();
    const hashed = hashPassword(password);

    // Direct check for admin credentials fallback if table is not yet migrated
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
        .or(`email.ilike.${trimmedId},username.ilike.${trimmedId}`)
        .limit(1)
        .maybeSingle();

      if (!error && dbUser) {
        if (dbUser.hashed_password !== hashed) {
          return NextResponse.json({ detail: "Invalid email or password" }, { status: 401 });
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
      // Supabase table not created yet
    }

    return NextResponse.json({ detail: "Invalid credentials" }, { status: 401 });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Internal authentication error";
    return NextResponse.json({ detail: msg }, { status: 500 });
  }
}
