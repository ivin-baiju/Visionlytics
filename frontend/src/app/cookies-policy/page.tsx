import React from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { Cookie } from "lucide-react";

export const metadata: Metadata = {
  title: "Cookies Policy — Visionlytics Crowd Intelligence",
  description:
    "Explanation of cookie categories, local storage use, security tokens, and consent controls in Visionlytics.",
};

export default function CookiesPolicyPage() {
  return (
    <div className="vl-container" style={{ maxWidth: "900px" }}>
      <header style={{ marginBottom: "2.5rem" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: "8px", color: "var(--accent-teal)", fontWeight: 700, fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" }}>
          <Cookie size={18} aria-hidden="true" />
          Transparency & Storage
        </div>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "2.25rem", fontWeight: 800, color: "var(--text-primary)" }}>
          Cookies & Storage Policy
        </h1>
        <p style={{ color: "var(--text-tertiary)", fontSize: "0.95rem", marginTop: "6px" }}>
          Last Updated: October 18, 2026
        </p>
      </header>

      <div className="vl-card" style={{ display: "flex", flexDirection: "column", gap: "2rem", lineHeight: 1.7, fontSize: "0.95rem" }}>
        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            1. What Are Cookies and Local Storage?
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            Cookies and browser Local Storage are small text files or key-value stores placed on your device to keep you securely signed in, remember system preferences, and optimize interface responsiveness.
          </p>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            2. Categories of Storage We Use
          </h2>

          <div style={{ display: "flex", flexDirection: "column", gap: "16px", marginTop: "12px" }}>
            <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", padding: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <strong style={{ color: "var(--text-primary)" }}>1. Strictly Necessary Storage</strong>
                <span style={{ fontSize: "0.75rem", background: "#E2E8F0", padding: "2px 8px", borderRadius: "4px", fontWeight: 700 }}>
                  Mandatory
                </span>
              </div>
              <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)" }}>
                Stores authentication tokens (JWT session), cryptographic CSRF tokens, and your cookie consent preference. Without this, you cannot log in or submit image analysis jobs.
              </p>
            </div>

            <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", padding: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <strong style={{ color: "var(--text-primary)" }}>2. Functional & Performance Storage</strong>
                <span style={{ fontSize: "0.75rem", background: "var(--accent-teal-light)", color: "var(--accent-teal)", padding: "2px 8px", borderRadius: "4px", fontWeight: 700 }}>
                  User Controlled
                </span>
              </div>
              <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)" }}>
                Remembers your confidence threshold slider settings (e.g. 0.35 filter) and heatmap toggle states between page reloads so you do not have to reconfigure each time.
              </p>
            </div>

            <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", padding: "16px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                <strong style={{ color: "var(--text-primary)" }}>3. Advertising & Tracking Cookies</strong>
                <span style={{ fontSize: "0.75rem", background: "#FEE2E2", color: "#DC2626", padding: "2px 8px", borderRadius: "4px", fontWeight: 700 }}>
                  None / Never Used
                </span>
              </div>
              <p style={{ fontSize: "0.88rem", color: "var(--text-secondary)" }}>
                We do not allow Google AdSense, Meta Pixel, or third-party behavioral trackers. Your browsing habits remain private.
              </p>
            </div>
          </div>
        </section>

        <section>
          <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.35rem", fontWeight: 700, color: "var(--text-primary)", marginBottom: "0.75rem" }}>
            3. How to Clear or Change Cookie Consent
          </h2>
          <p style={{ color: "var(--text-secondary)" }}>
            You can revoke your consent at any time by clearing your browser cache or clicking our Cookie Consent Banner at the bottom of the screen.
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
