import { createClient } from "@supabase/supabase-js";

// Read Supabase environment variables safely
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

export const isSupabaseConfigured = Boolean(supabaseUrl && supabaseAnonKey);

// Supabase client instance (anonymized public queries & auth)
export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

export interface AnalysisRecord {
  id?: number | string;
  created_at?: string;
  source_type: string;
  people_count: number;
  density_label: string;
  occupancy_ratio: number;
  confidence: number;
  features?: Record<string, unknown>;
}

export async function fetchRecentAnalyses(limit = 20): Promise<AnalysisRecord[]> {
  if (supabase) {
    try {
      const { data, error } = await supabase
        .from("analysis_history")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(limit);
      if (!error && data) return data as AnalysisRecord[];
    } catch {
      // Return empty on network or configuration failure
    }
  }
  return [];
}
