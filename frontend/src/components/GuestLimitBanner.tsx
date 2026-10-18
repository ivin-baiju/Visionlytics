"use client";

import React from "react";
import Link from "next/link";
import { AlertCircle, Lock, ArrowRight, Sparkles } from "lucide-react";

interface GuestLimitBannerProps {
  remaining: number;
  limit: number;
  isLimitReached: boolean;
  featureName?: string;
}

export default function GuestLimitBanner({
  remaining,
  limit,
  isLimitReached,
  featureName = "uploads and real-time vision processing",
}: GuestLimitBannerProps) {
  if (isLimitReached) {
    return (
      <div
        role="alert"
        style={{
          backgroundColor: "#FEF2F2",
          border: "1px solid #FCA5A5",
          borderRadius: "var(--radius-md)",
          padding: "16px 20px",
          marginBottom: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "#B91C1C" }}>
          <Lock size={20} />
          <h2 style={{ fontSize: "1rem", fontWeight: 700, margin: 0 }}>
            Guest Limit Reached ({limit}/{limit} used)
          </h2>
        </div>
        <p style={{ color: "#7F1D1D", fontSize: "0.88rem", margin: 0, lineHeight: 1.5 }}>
          You have utilized all <strong>{limit} free guest upload & analysis quota</strong>. To get unlimited access to {featureName}, live video streams, and full model telemetry, please sign in or create a free account with your email or phone number.
        </p>
        <div style={{ display: "flex", gap: "12px", marginTop: "4px" }}>
          <Link
            href="/login"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "6px",
              backgroundColor: "var(--accent-teal)",
              color: "#FFFFFF",
              padding: "8px 16px",
              borderRadius: "var(--radius-sm)",
              fontWeight: 600,
              fontSize: "0.85rem",
              textDecoration: "none",
            }}
          >
            Sign In or Register for Unlimited Access <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        backgroundColor: "var(--accent-teal-light)",
        border: "1px solid var(--accent-teal-border)",
        borderRadius: "var(--radius-md)",
        padding: "12px 18px",
        marginBottom: "20px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "10px",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
        <Sparkles size={18} style={{ color: "var(--accent-teal)" }} />
        <span style={{ fontSize: "0.88rem", color: "var(--text-secondary)" }}>
          <strong>Guest Mode:</strong> You have <strong>{remaining} of {limit} free uploads/scans</strong> remaining.
        </span>
      </div>
      <Link
        href="/login"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "4px",
          color: "var(--accent-teal)",
          fontWeight: 600,
          fontSize: "0.84rem",
          textDecoration: "none",
        }}
      >
        Sign in for Unlimited Access <ArrowRight size={14} />
      </Link>
    </div>
  );
}
