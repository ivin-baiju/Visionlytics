import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { FileText } from "lucide-react";

export const metadata: Metadata = {
  title: "Terms and Conditions — Visionlytics Crowd Intelligence",
  description:
    "Terms of service, acceptable use policies, intellectual property rights, and liability limitations for the Visionlytics platform.",
};

export default function TermsAndConditionsPage() {
  return (
    <div className="vl-container" style={{ maxWidth: "900px" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", color: "var(--accent-teal)", fontWeight: 700, fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" }}>
          <FileText size={18} aria-hidden="true" />
          Legal Agreement
        </div>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "2.25rem", fontWeight: 800, color: "var(--text-primary)" }}>
          Terms & Conditions
        </h1>
        <p style={{ color: "var(--text-tertiary)", fontSize: "0.95rem", marginTop: "6px" }}>
          Last Updated: October 18, 2026
        </p>
      </header>

      <div className="vl-card" style={{ display: "flex", flexDirection: "column", gap: "2rem", lineHeight: 1.7, fontSize: "0.95rem" }}>
        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            1. Acceptance of Terms
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            By accessing or using the Visionlytics application, dashboard, APIs, or computer vision models, you agree to be bound by these Terms and Conditions. If you do not agree, do not access or use our services.
          </p>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            2. Acceptable Use & Ethical AI Guidelines
          </h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
            Visionlytics is intended for venue safety, crowd flow optimization, spatial capacity planning, and academic research. You strictly agree NOT to:
          </p>
          <ul style={{ paddingLeft: "1.25rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "8px" }}>
            <li>Attempt to use Visionlytics for unauthorized biometric surveillance, tracking individuals across locations without consent, or facial recognition.</li>
            <li>Deploy the system in violation of local surveillance laws, wiretapping statutes, or municipal video recording ordinances.</li>
            <li>Interfere with, circumvent rate limiting, probe vulnerabilities, or reverse engineer proprietary model weights without authorization.</li>
          </ul>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            3. Intellectual Property & Open Source Licenses
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            The Visionlytics software core, spatial feature extractors, and UI components are proprietary and/or governed by the MIT License as designated in repository manifests. YOLOv8 model weights are governed by Ultralytics AGPL-3.0 / commercial licenses. All custom SVG branding, logos, and platform design systems are copyright © 2026 Visionlytics Labs.
          </p>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            4. Limitation of Liability & Heuristic Nature
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            Computer vision outputs (people counts, heatmaps, density classifications) are statistical estimations based on visual data. While models achieve benchmarked accuracies, environmental factors such as severe occlusion, extreme low-light, or camera distortion can affect counts. Visionlytics is provided &quot;as-is&quot; without guarantees of 100% operational infallibility.
          </p>
        </section>

        <section style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "1.5rem" }}>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.2rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.5rem" }}>
            5. Governing Law
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            These Terms are governed by and construed in accordance with the laws of India and applicable international cyber security regulations. Disputes shall be resolved under the jurisdiction of competent courts in Kerala, India.
          </p>
        </section>
      </div>

      <div style={{ marginTop: "2rem", display: "flex", gap: "14px" }}>
        <Link href="/" className="vl-btn vl-btn-secondary">
          Return to Dashboard
        </Link>
        <Link href="/privacy-policy" className="vl-btn vl-btn-primary">
          Privacy Policy
        </Link>
      </div>
    </div>
  );
}
