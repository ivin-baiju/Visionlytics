import { NextResponse } from "next/server";
import { supabaseAdmin } from "@/lib/supabase-admin";

function verifyAdmin(req: Request) {
  const authHeader = req.headers.get("authorization") || "";
  if (!authHeader.startsWith("Bearer ")) return false;
  const token = authHeader.replace("Bearer ", "");
  try {
    if (token.startsWith("admin_token_") || token.startsWith("token_")) {
      const b64 = token.replace(/^(admin_token_|token_)/, "");
      const user = JSON.parse(Buffer.from(b64, "base64").toString("utf-8"));
      return user.role === "admin";
    }
  } catch {
    return false;
  }
  return false;
}

export async function GET(req: Request) {
  if (!verifyAdmin(req)) {
    return NextResponse.json({ detail: "Unauthorized admin access" }, { status: 403 });
  }

  try {
    const { data, error } = await supabaseAdmin
      .from("analysis_history")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(100);

    if (!error && data) {
      return NextResponse.json({ analyses: data });
    }
  } catch {
    // If not created yet
  }

  return NextResponse.json({ analyses: [] });
}
