import { NextResponse } from "next/server";
import crypto from "crypto";
import { supabaseAdmin } from "@/lib/supabase-admin";

function hashPassword(password: string): string {
  return crypto.createHash("sha256").update(password).digest("hex");
}

export async function POST(req: Request) {
  try {
    const { username, email, password, phone } = await req.json();

    if (!username || !email || !password) {
      return NextResponse.json(
        { detail: "Username, email, and password are required." },
        { status: 400 }
      );
    }

    const cleanUsername = String(username).trim();
    const cleanEmail = String(email).trim().toLowerCase();
    const cleanPhone = phone ? String(phone).trim() : null;
    const hashedPassword = hashPassword(password);

    // Check if user already exists
    const { data: existingUser } = await supabaseAdmin
      .from("users")
      .select("id, username, email")
      .or(`email.ilike.${cleanEmail},username.ilike.${cleanUsername}`)
      .limit(1)
      .maybeSingle();

    if (existingUser) {
      return NextResponse.json(
        { detail: "A user with that username or email already exists." },
        { status: 409 }
      );
    }

    const { data: newUser, error: insertError } = await supabaseAdmin
      .from("users")
      .insert({
        username: cleanUsername,
        email: cleanEmail,
        phone: cleanPhone,
        hashed_password: hashedPassword,
        role: "user",
        is_verified: true,
      })
      .select("id, username, email, phone, role, is_verified, created_at")
      .single();

    if (insertError) {
      return NextResponse.json(
        { detail: `Failed to create user account: ${insertError.message}` },
        { status: 500 }
      );
    }

    return NextResponse.json({
      status: "success",
      message: "Account registered successfully.",
      user: newUser,
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Internal registration error";
    return NextResponse.json({ detail: msg }, { status: 500 });
  }
}
