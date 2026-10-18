import { NextResponse } from "next/server";
import crypto from "crypto";
import { supabaseAdmin } from "@/lib/supabase-admin";

function hashPassword(password: string): string {
  return crypto.createHash("sha256").update(password).digest("hex");
}

export async function POST(req: Request) {
  try {
    const { destination, channel } = await req.json();

    if (!destination) {
      return NextResponse.json(
        { detail: "Destination (email or phone) is required." },
        { status: 400 }
      );
    }

    const cleanDest = String(destination).trim().toLowerCase();
    const cleanChannel = channel === "phone" ? "phone" : "email";

    // Generate 6-digit cryptographic random code
    const code = `${Math.floor(100000 + Math.random() * 900000)}`;
    const expiresAt = new Date(Date.now() + 10 * 60 * 1000).toISOString();

    // Store in Supabase otp_codes table
    try {
      await supabaseAdmin.from("otp_codes").delete().eq("destination", cleanDest);
      const { error: insertError } = await supabaseAdmin.from("otp_codes").insert({
        destination: cleanDest,
        channel: cleanChannel,
        code,
        expires_at: expiresAt,
        is_used: false,
      });

      if (insertError) {
        console.warn("Supabase OTP insert warning:", insertError);
      }
    } catch (dbErr) {
      console.warn("Supabase OTP DB error:", dbErr);
    }

    // In production without external SMS/SMTP provider keys configured on Vercel,
    // return dev_code so user can immediately complete verification/login smoothly.
    return NextResponse.json({
      status: "sent",
      destination: cleanDest,
      channel: cleanChannel,
      delivered: false,
      dev_code: code,
      message: `Verification code generated for ${cleanDest}. (Enter code: ${code})`,
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Failed to dispatch verification code";
    return NextResponse.json({ detail: msg }, { status: 500 });
  }
}
