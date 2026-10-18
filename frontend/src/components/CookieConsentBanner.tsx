"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Cookie, Check } from "lucide-react";

export default function CookieConsentBanner() {
  const [mounted, setMounted] = useState(false);
  const [showBanner, setShowBanner] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [analyticsAllowed, setAnalyticsAllowed] = useState(false);

  useEffect(() => {
    const frameId = requestAnimationFrame(() => {
      setMounted(true);
      const saved = localStorage.getItem("visionlytics_cookie_consent");
      if (!saved) {
        setShowBanner(true);
      }
    });
    return () => cancelAnimationFrame(frameId);
  }, []);

  const saveConsent = async (analytics: boolean) => {
    localStorage.setItem(
      "visionlytics_cookie_consent",
      JSON.stringify({
        necessary: true,
        analytics,
        timestamp: new Date().toISOString(),
      })
    );
    setShowBanner(false);
    setShowPreferences(false);

    // Anonymously notify backend compliance endpoint
    try {
      await fetch("/api/py/consent/record", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          consent_type: "cookie_banner",
          analytics_allowed: analytics,
        }),
      });
    } catch {
      // Non-blocking
    }
  };

  if (!mounted || !showBanner) return null;

  return (
    <div
      role="region"
      aria-label="Cookie consent banner"
      style={{
        position: "fixed",
        bottom: "20px",
        left: "50%",
        transform: "translateX(-50%)",
        width: "calc(100% - 40px)",
        maxWidth: "880px",
        backgroundColor: "#FFFFFF",
        border: "1px solid var(--border-highlight)",
        borderRadius: "var(--radius-lg)",
        padding: "1.25rem 1.5rem",
        boxShadow: "0 20px 40px -10px rgba(0, 0, 0, 0.15)",
        zIndex: 99999,
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: "1rem" }}>
        <div
          style={{
            width: "42px",
            height: "42px",
            borderRadius: "50%",
            backgroundColor: "var(--accent-teal-light)",
            color: "var(--accent-teal)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          <Cookie size={22} aria-hidden="true" />
        </div>

        <div style={{ flex: 1 }}>
          <h3
            style={{
              fontFamily: "var(--font-heading)",
              fontSize: "1.05rem",
              fontWeight: 700,
              color: "var(--text-primary)",
              marginBottom: "4px",
            }}
          >
            We respect your privacy and data autonomy
          </h3>
          <p
            style={{
              fontSize: "0.86rem",
              color: "var(--text-secondary)",
              lineHeight: 1.5,
              marginBottom: "12px",
            }}
          >
            Visionlytics uses strictly necessary session storage for authentication and
            core system performance. We do not use third-party trackers or cross-site advertising.
            Learn more in our{" "}
            <Link
              href="/cookies-policy"
              style={{ color: "var(--accent-teal)", fontWeight: 600, textDecoration: "underline" }}
            >
              Cookies Policy
            </Link>{" "}
            and{" "}
            <Link
              href="/privacy-policy"
              style={{ color: "var(--accent-teal)", fontWeight: 600, textDecoration: "underline" }}
            >
              Privacy Policy
            </Link>
            .
          </p>

          {showPreferences && (
            <div
              style={{
                backgroundColor: "var(--bg-surface-elevated)",
                padding: "12px 16px",
                borderRadius: "var(--radius-sm)",
                marginBottom: "14px",
                fontSize: "0.85rem",
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "8px",
                }}
              >
                <div>
                  <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>Strictly Necessary</span>
                  <p style={{ fontSize: "0.78rem", color: "var(--text-tertiary)" }}>
                    Required for core inference, auth token caching, and security checks.
                  </p>
                </div>
                <span
                  style={{
                    fontSize: "0.75rem",
                    fontWeight: 700,
                    padding: "3px 8px",
                    borderRadius: "4px",
                    background: "#E2E8F0",
                    color: "#475569",
                  }}
                >
                  Always Active
                </span>
              </div>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  paddingTop: "8px",
                  borderTop: "1px solid var(--border-subtle)",
                }}
              >
                <div>
                  <span style={{ fontWeight: 600, color: "var(--text-primary)" }}>Anonymous Performance Analytics</span>
                  <p style={{ fontSize: "0.78rem", color: "var(--text-tertiary)" }}>
                    Aggregated query latency metrics without IP or identifying information.
                  </p>
                </div>
                <label style={{ display: "flex", alignItems: "center", cursor: "pointer", gap: "6px" }}>
                  <input
                    type="checkbox"
                    checked={analyticsAllowed}
                    onChange={(e) => setAnalyticsAllowed(e.target.checked)}
                    aria-label="Allow anonymous analytics"
                    style={{ width: "18px", height: "18px", accentColor: "var(--accent-teal)" }}
                  />
                  <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                    {analyticsAllowed ? "Enabled" : "Disabled"}
                  </span>
                </label>
              </div>
            </div>
          )}

          <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", alignItems: "center" }}>
            <button
              type="button"
              className="vl-btn vl-btn-primary"
              onClick={() => saveConsent(true)}
              style={{ fontSize: "0.85rem", padding: "8px 16px" }}
            >
              <Check size={16} aria-hidden="true" /> Accept Necessary & Analytics
            </button>
            <button
              type="button"
              className="vl-btn vl-btn-secondary"
              onClick={() => saveConsent(false)}
              style={{ fontSize: "0.85rem", padding: "8px 16px" }}
            >
              Only Necessary
            </button>
            <button
              type="button"
              onClick={() => setShowPreferences((prev) => !prev)}
              style={{
                background: "transparent",
                border: "none",
                color: "var(--text-secondary)",
                fontSize: "0.85rem",
                cursor: "pointer",
                textDecoration: "underline",
                padding: "8px 10px",
              }}
            >
              {showPreferences ? "Hide Preferences" : "Customize Preferences"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
