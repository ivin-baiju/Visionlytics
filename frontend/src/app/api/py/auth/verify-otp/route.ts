import { NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase-admin";

export async function POST(req: Request) {
  try {
    const { destination, code } = await req.json();

    if (!destination || !code) {
      return NextResponse.json(
        { detail: "Destination and verification code are required." },
        { status: 400 }
      );
    }

    const cleanDest = String(destination).trim().toLowerCase();
    const cleanCode = String(code).trim();

    const { data: record, error } = await supabaseAdmin
      .from("otp_codes")
      .select("id, code, expires_at, is_used")
      .eq("destination", cleanDest)
      .eq("code", cleanCode)
      .order("id", { ascending: false })
      .limit(1)
      .maybeSingle();

    if (error || !record) {
      return NextResponse.json(
        { detail: "Invalid or expired verification code." },
        { status: 400 }
      );
    }

    if (new Date(record.expires_at).getTime() < Date.now()) {
      await supabaseAdmin.from("otp_codes").delete().eq("destination", cleanDest);
      return NextResponse.json(
        { detail: "Verification code has expired. Please request a new one." },
        { status: 400 }
      );
    }

    // Invalidate code upon successful verification
    await supabaseAdmin.from("otp_codes").delete().eq("destination", cleanDest);

    return NextResponse.json({
      status: "verified",
      destination: cleanDest,
      message: "Code successfully verified.",
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Failed to verify code";
    return NextResponse.json({ detail: msg }, { status: 500 });
  }
}
