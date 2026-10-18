import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { RefreshCcw } from "lucide-react";

export const metadata: Metadata = {
  title: "Refund Policy — Visionlytics Platform",
  description:
    "Refund, subscription cancellation, and commercial licensing policies for Visionlytics.",
};

export default function RefundPolicyPage() {
  return (
    <div className="vl-container" style={{ maxWidth: "900px" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", color: "var(--accent-teal)", fontWeight: 700, fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" }}>
          <RefreshCcw size={18} aria-hidden="true" />
          Commercial Transparency
        </div>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "2.25rem", fontWeight: 800, color: "var(--text-primary)" }}>
          Refund Policy
        </h1>
        <p style={{ color: "var(--text-tertiary)", fontSize: "0.95rem", marginTop: "6px" }}>
          Last Updated: October 18, 2026
        </p>
      </header>

      <div className="vl-card" style={{ display: "flex", flexDirection: "column", gap: "2rem", lineHeight: 1.7, fontSize: "0.95rem" }}>
        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            1. Open-Source vs Commercial Tiers
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            The community edition of Visionlytics is 100% free and open-source under permissible licenses. For enterprise support agreements, dedicated cloud GPU inference clusters, and high-throughput streaming tiers, billing and refund terms apply as detailed below.
          </p>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            2. 14-Day Money-Back Guarantee
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            If you subscribe to an enterprise self-hosted or managed cloud cluster plan, you are entitled to a full refund within 14 calendar days of your initial purchase if our platform does not meet your hardware or latency requirements.
          </p>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            3. How to Request a Refund
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            Submit a request directly through your account dashboard or administrative support desk with:
          </p>
          <ul style={{ paddingLeft: "1.25rem", color: "var(--text-secondary)", marginTop: "8px", display: "flex", flexDirection: "column", gap: "8px" }}>
            <li>Your account email address and transaction reference number.</li>
            <li>A brief summary of the technical or operational bottleneck encountered.</li>
          </ul>
          <p style={{ color: "var(--text-secondary)", marginTop: "8px" }}>
            Approved refunds will be processed to the original payment method within 5 to 7 business days.
          </p>
        </section>
      </div>

      <div style={{ marginTop: "2rem", display: "flex", gap: "14px" }}>
        <Link href="/" className="vl-btn vl-btn-secondary">
          Return to Dashboard
        </Link>
        <Link href="/terms-and-conditions" className="vl-btn vl-btn-primary">
          Terms & Conditions
        </Link>
      </div>
    </div>
  );
}
