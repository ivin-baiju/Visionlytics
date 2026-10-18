import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { ShieldCheck } from "lucide-react";

export const metadata: Metadata = {
  title: "Privacy Policy — Visionlytics Crowd Intelligence",
  description:
    "Comprehensive Privacy Policy detailing strict data minimization, edge processing, zero face recognition, and GDPR/CCPA compliance.",
};

export default function PrivacyPolicyPage() {
  return (
    <div className="vl-container" style={{ maxWidth: "900px" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", color: "var(--accent-teal)", fontWeight: 700, fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" }}>
          <ShieldCheck size={18} aria-hidden="true" />
          Data Governance & Privacy
        </div>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "2.25rem", fontWeight: 800, color: "var(--text-primary)" }}>
          Privacy Policy
        </h1>
        <p style={{ color: "var(--text-tertiary)", fontSize: "0.95rem", marginTop: "6px" }}>
          Effective Date: October 18, 2026 • Version 2.0 (Supabase & Microservices)
        </p>
      </header>

      <div className="vl-card" style={{ display: "flex", flexDirection: "column", gap: "2rem", lineHeight: 1.7, fontSize: "0.95rem" }}>
        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            1. Core Principle: Zero Facial Recognition & Data Minimization
          </h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
            Visionlytics is built from the ground up on the principle of <strong>strict data minimization</strong>.
            Our computer vision pipelines evaluate aggregate geometric spatial distributions (e.g. bounding box coordinates,
            Voronoi interpersonal distances, and crowd density counts).
          </p>
          <p style={{ color: "var(--text-secondary)" }}>
            <strong>We do NOT collect, extract, or store biometric identifiers, facial embeddings, or individual identity profiles.</strong>{" "}
            All person detections are anonymous COCO class 0 instances transformed into aggregate statistical feature vectors.
          </p>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            2. What Data We Process
          </h2>
          <ul style={{ paddingLeft: "1.25rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "8px" }}>
            <li>
              <strong>Temporary Inference Media:</strong> Image frames or video uploads submitted to the Image Inspector or Video Surveillance are processed in-memory. Uploaded media is discarded immediately after vector computation and is not retained on disk or cloud storage.
            </li>
            <li>
              <strong>Aggregate Density Metrics:</strong> Time-series crowd counts (e.g., 5 persons, Medium Density), frame occupancy ratios, and region distributions stored in our encrypted Supabase database.
            </li>
            <li>
              <strong>Authentication Data:</strong> Analyst usernames, emails, and cryptographically hashed passwords (using salted bcrypt) for authorized access.
            </li>
            <li>
              <strong>Technical Telemetry:</strong> Anonymized HTTP response status and request timestamps to monitor system health and prevent denial-of-service.
            </li>
          </ul>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            3. Camera & Video Privacy
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            When using the <strong>Live Camera</strong> feature:
          </p>
          <ul style={{ paddingLeft: "1.25rem", color: "var(--text-secondary)", marginTop: "8px", display: "flex", flexDirection: "column", gap: "8px" }}>
            <li>The video stream is captured directly from your local browser hardware via the native <code>navigator.mediaDevices.getUserMedia</code> API.</li>
            <li>No persistent video feeds are uploaded or broadcast to third parties.</li>
            <li>You can revoke camera permissions at any time through your browser settings or by pressing &quot;Disconnect Live Stream&quot;.</li>
          </ul>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            4. Third-Party Embeds & Tracking
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            <strong>Visionlytics contains zero third-party behavioral trackers</strong>, social media tracking pixels, or cross-site ad networks.
            Our infrastructure uses Supabase (PostgreSQL with Row Level Security) and local FastAPI microservices configured with hardened CORS headers.
          </p>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            5. Your Rights (GDPR & CCPA Compliance)
          </h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "0.75rem" }}>
            Depending on your jurisdiction, you retain the right to:
          </p>
          <ul style={{ paddingLeft: "1.25rem", color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: "8px" }}>
            <li>Request a copy of your stored analytical reports and session logs.</li>
            <li>Request permanent deletion of your account and related telemetry.</li>
            <li>Opt out of any non-essential analytics via our Cookies Preferences.</li>
          </ul>
        </section>

        <section style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: "1.5rem" }}>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.2rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.5rem" }}>
            6. Business & Compliance Office
          </h2>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>
            <strong>Entity:</strong> Visionlytics Core Intelligence Operations<br />
            <strong>Contact:</strong> Direct administrative dashboard message desk<br />
            <strong>Compliance Officer:</strong> Authorized Data Controller & System Security Operations
          </p>
        </section>
      </div>

      <div style={{ marginTop: "2rem", display: "flex", gap: "14px" }}>
        <Link href="/" className="vl-btn vl-btn-secondary">
          Return to Dashboard
        </Link>
        <Link href="/terms-and-conditions" className="vl-btn vl-btn-primary">
          View Terms & Conditions
        </Link>
      </div>
    </div>
  );
}
