"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Lock,
  Mail,
  Phone,
  User,
  KeyRound,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [authMethod, setAuthMethod] = useState<"password" | "otp">("password");

  // Form fields
  const [identifier, setIdentifier] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [otpCode, setOtpCode] = useState("");

  // OTP state
  const [otpSent, setOtpSent] = useState(false);
  const [otpChannel, setOtpChannel] = useState<"email" | "phone">("email");
  const [devOtpHint, setDevOtpHint] = useState<string | null>(null);

  // Status
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleSendOtp = async (dest: string, channel: "email" | "phone") => {
    if (!dest) {
      setErrorMsg(`Please enter your ${channel} address first.`);
      return;
    }
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch("/api/py/auth/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ destination: dest, channel }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to send OTP");
      setOtpSent(true);
      setOtpChannel(channel);
      setSuccessMsg(`Verification code sent to ${dest}!`);
      if (data.dev_code) {
        setDevOtpHint(data.dev_code);
      }
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to dispatch verification code");
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const payload: Record<string, string> = { identifier };
      if (authMethod === "password") {
        if (!password) throw new Error("Please enter your account password.");
        payload.password = password;
      } else {
        if (!otpCode) throw new Error("Please enter the 6-digit verification code.");
        payload.otp_code = otpCode;
      }

      const res = await fetch("/api/py/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Authentication failed");

      // Save token in secure session storage
      localStorage.setItem("visionlytics_token", data.access_token);
      localStorage.setItem("visionlytics_user", JSON.stringify(data.user));

      setSuccessMsg("Signed in successfully! Redirecting...");
      setTimeout(() => {
        if (data.user?.role === "admin") {
          router.push("/admin");
        } else {
          router.push("/");
        }
      }, 700);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Sign in failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      if (!username || !email || !password) {
        throw new Error("Username, email, and password are required.");
      }

      const payload: Record<string, string> = {
        username,
        email,
        password,
      };
      if (phone) payload.phone = phone;
      if (otpCode) payload.otp_code = otpCode;

      const res = await fetch("/api/py/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");

      setSuccessMsg("Account created successfully! You can now sign in.");
      setMode("login");
      setIdentifier(username);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vl-container" style={{ maxWidth: "560px", paddingTop: "2rem" }}>
      <div className="vl-card" style={{ padding: "2.5rem" }}>
        {/* Brand Header */}
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div
            style={{
              width: "52px",
              height: "52px",
              borderRadius: "50%",
              backgroundColor: "var(--accent-teal-light)",
              color: "var(--accent-teal)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              margin: "0 auto 12px",
            }}
          >
            <ShieldCheck size={28} />
          </div>
          <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.75rem", fontWeight: 800 }}>
            {mode === "login" ? "Sign In to Visionlytics" : "Create an Account"}
          </h1>
          <p style={{ color: "var(--text-tertiary)", fontSize: "0.9rem", marginTop: "4px" }}>
            {mode === "login"
              ? "Access your crowd intelligence workspaces and database."
              : "Register to unlock real-time streaming, models, and analytics."}
          </p>
        </div>

        {/* Mode Toggle (Tabs) */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "6px",
            backgroundColor: "var(--bg-surface-elevated)",
            padding: "4px",
            borderRadius: "var(--radius-md)",
            marginBottom: "1.75rem",
          }}
        >
          <button
            type="button"
            onClick={() => {
              setMode("login");
              setErrorMsg(null);
            }}
            style={{
              padding: "8px 14px",
              borderRadius: "var(--radius-sm)",
              border: "none",
              backgroundColor: mode === "login" ? "#FFFFFF" : "transparent",
              color: mode === "login" ? "var(--text-primary)" : "var(--text-secondary)",
              fontWeight: 700,
              fontSize: "0.88rem",
              cursor: "pointer",
              boxShadow: mode === "login" ? "0 1px 3px rgba(0,0,0,0.05)" : "none",
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("register");
              setErrorMsg(null);
            }}
            style={{
              padding: "8px 14px",
              borderRadius: "var(--radius-sm)",
              border: "none",
              backgroundColor: mode === "register" ? "#FFFFFF" : "transparent",
              color: mode === "register" ? "var(--text-primary)" : "var(--text-secondary)",
              fontWeight: 700,
              fontSize: "0.88rem",
              cursor: "pointer",
              boxShadow: mode === "register" ? "0 1px 3px rgba(0,0,0,0.05)" : "none",
            }}
          >
            Create Account
          </button>
        </div>

        {/* Alerts */}
        {errorMsg && (
          <div
            className="vl-fade-in"
            style={{
              backgroundColor: "#FEF2F2",
              border: "1px solid #FCA5A5",
              color: "#B91C1C",
              padding: "10px 14px",
              borderRadius: "var(--radius-sm)",
              fontSize: "0.85rem",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "1.25rem",
            }}
          >
            <AlertCircle size={16} />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div
            className="vl-fade-in"
            style={{
              backgroundColor: "#ECFDF5",
              border: "1px solid #6EE7B7",
              color: "#047857",
              padding: "10px 14px",
              borderRadius: "var(--radius-sm)",
              fontSize: "0.85rem",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "1.25rem",
            }}
          >
            <CheckCircle2 size={16} />
            <span>{successMsg}</span>
          </div>
        )}

        {/* ── Mode 1: Sign In ─────────────────────────────────────────────────── */}
        {mode === "login" && (
          <form onSubmit={handleLoginSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                Username, Email, or Phone
              </label>
              <div style={{ position: "relative" }}>
                <input
                  type="text"
                  required
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="user@domain.com or +1234567890"
                  className="vl-input"
                  style={{ paddingLeft: "38px" }}
                />
                <User size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
              </div>
            </div>

            {/* Sub-method switch: Password vs OTP */}
            <div style={{ display: "flex", gap: "12px", fontSize: "0.84rem" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer" }}>
                <input
                  type="radio"
                  name="authMethod"
                  checked={authMethod === "password"}
                  onChange={() => setAuthMethod("password")}
                  style={{ accentColor: "var(--accent-teal)" }}
                />
                <span>Password</span>
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: "6px", cursor: "pointer" }}>
                <input
                  type="radio"
                  name="authMethod"
                  checked={authMethod === "otp"}
                  onChange={() => setAuthMethod("otp")}
                  style={{ accentColor: "var(--accent-teal)" }}
                />
                <span>Real-Time OTP (Code)</span>
              </label>
            </div>

            {authMethod === "password" ? (
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                  Password
                </label>
                <div style={{ position: "relative" }}>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="vl-input"
                    style={{ paddingLeft: "38px" }}
                  />
                  <Lock size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
                </div>
              </div>
            ) : (
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "6px" }}>
                  <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)" }}>
                    6-Digit Verification Code
                  </label>
                  <button
                    type="button"
                    onClick={() => handleSendOtp(identifier, identifier.includes("@") ? "email" : "phone")}
                    disabled={loading || !identifier}
                    style={{
                      background: "transparent",
                      border: "none",
                      color: "var(--accent-teal)",
                      fontSize: "0.82rem",
                      fontWeight: 700,
                      cursor: "pointer",
                      textDecoration: "underline",
                    }}
                  >
                    Send OTP to {identifier ? identifier : "Identifier"}
                  </button>
                </div>
                <div style={{ position: "relative" }}>
                  <input
                    type="text"
                    required
                    maxLength={6}
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    placeholder="Enter 6-digit code"
                    className="vl-input"
                    style={{ paddingLeft: "38px", letterSpacing: "2px", fontWeight: 700 }}
                  />
                  <KeyRound size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
                </div>
                {devOtpHint && (
                  <p style={{ fontSize: "0.78rem", color: "var(--accent-teal)", marginTop: "4px" }}>
                    Demo Instant Code: <strong>{devOtpHint}</strong>
                  </p>
                )}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="vl-btn vl-btn-primary"
              style={{ width: "100%", marginTop: "8px", padding: "12px" }}
            >
              {loading ? "Verifying..." : "Sign In to Visionlytics"}
            </button>
          </form>
        )}

        {/* ── Mode 2: Account Creation with Phone & Email OTP ──────────────────── */}
        {mode === "register" && (
          <form onSubmit={handleRegisterSubmit} style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                Username
              </label>
              <div style={{ position: "relative" }}>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. john_doe"
                  className="vl-input"
                  style={{ paddingLeft: "38px" }}
                />
                <User size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
              </div>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                Email Address
              </label>
              <div style={{ position: "relative" }}>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="vl-input"
                  style={{ paddingLeft: "38px" }}
                />
                <Mail size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
              </div>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                Phone Number (for SMS Verification)
              </label>
              <div style={{ display: "flex", gap: "8px" }}>
                <div style={{ position: "relative", flex: 1 }}>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+1 (555) 000-0000"
                    className="vl-input"
                    style={{ paddingLeft: "38px" }}
                  />
                  <Phone size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
                </div>
                <button
                  type="button"
                  onClick={() => handleSendOtp(phone || email, phone ? "phone" : "email")}
                  disabled={loading || (!phone && !email)}
                  className="vl-btn vl-btn-secondary"
                  style={{ fontSize: "0.82rem", whiteSpace: "nowrap" }}
                >
                  Send OTP
                </button>
              </div>
            </div>

            {otpSent && (
              <div className="vl-fade-in" style={{ backgroundColor: "var(--bg-surface-elevated)", padding: "12px", borderRadius: "var(--radius-sm)" }}>
                <label style={{ display: "block", fontSize: "0.82rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "4px" }}>
                  Enter 6-Digit OTP Code
                </label>
                <input
                  type="text"
                  maxLength={6}
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  placeholder="6-digit code"
                  className="vl-input"
                  style={{ letterSpacing: "2px", fontWeight: 700 }}
                />
                {devOtpHint && (
                  <p style={{ fontSize: "0.78rem", color: "var(--accent-teal)", marginTop: "4px" }}>
                    Demo Code: <strong>{devOtpHint}</strong>
                  </p>
                )}
              </div>
            )}

            <div>
              <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: "6px" }}>
                Password
              </label>
              <div style={{ position: "relative" }}>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 6 characters"
                  className="vl-input"
                  style={{ paddingLeft: "38px" }}
                />
                <Lock size={16} style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", color: "var(--text-tertiary)" }} />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="vl-btn vl-btn-primary"
              style={{ width: "100%", marginTop: "8px", padding: "12px" }}
            >
              {loading ? "Creating Account..." : "Complete Registration"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
