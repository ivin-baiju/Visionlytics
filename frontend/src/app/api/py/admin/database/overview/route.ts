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

  let total_users = 1;
  let total_analyses = 0;
  let total_uploads = 0;
  let total_people_detected = 0;

  try {
    const [uRes, aRes, upRes] = await Promise.all([
      supabaseAdmin.from("users").select("id", { count: "exact", head: true }),
      supabaseAdmin.from("analysis_history").select("people_count"),
      supabaseAdmin.from("user_uploads").select("id", { count: "exact", head: true }),
    ]);

    if (uRes.count !== null && uRes.count !== undefined) total_users = uRes.count;
    if (upRes.count !== null && upRes.count !== undefined) total_uploads = upRes.count;
    if (aRes.data) {
      total_analyses = aRes.data.length;
      total_people_detected = aRes.data.reduce((acc, curr) => acc + (Number(curr.people_count) || 0), 0);
    }
  } catch {
    // If tables don't exist yet, return healthy default structure
  }

  return NextResponse.json({
    total_users,
    total_analyses,
    total_uploads,
    total_people_detected,
    database_engine: "Supabase PostgreSQL",
  });
}
