"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { User, Menu, X } from "lucide-react";

interface NavLink {
  href: string;
  label: string;
}

const PUBLIC_NAV_LINKS: NavLink[] = [
  { href: "/", label: "Dashboard" },
  { href: "/image-analysis", label: "Image Inspector" },
  { href: "/video-analysis", label: "Video Surveillance" },
  { href: "/live-camera", label: "Live Camera" },
  { href: "/ml-models", label: "ML Suite" },
  { href: "/dataset", label: "Dataset" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [currentUser, setCurrentUser] = useState<{ username?: string; role?: string } | null>(null);

  useEffect(() => {
    try {
      const savedUser = localStorage.getItem("visionlytics_user");
      if (savedUser) {
        const parsed = JSON.parse(savedUser);
        setCurrentUser(parsed);
        setIsAdmin(parsed?.role === "admin");
      } else {
        setCurrentUser(null);
        setIsAdmin(false);
      }
    } catch {
      // Keep defaults
    }
  }, [pathname]);

  const handleSignOut = () => {
    localStorage.removeItem("visionlytics_token");
    localStorage.removeItem("visionlytics_user");
    setCurrentUser(null);
    setIsAdmin(false);
    window.location.href = "/login";
  };

  // For Admin: ONLY show System Console as requested.
  // For standard users / guests: show regular public navigation links.
  const navLinks = isAdmin
    ? [{ href: "/admin", label: "System Console" }]
    : PUBLIC_NAV_LINKS;

  return (
    <header className="vl-header" role="banner">
      <div className="vl-header-inner">
        {/* Clean brand */}
        <Link href={isAdmin ? "/admin" : "/"} className="vl-brand-link">
          <div className="vl-brand-logo">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo.svg" alt="Visionlytics Logo" width={30} height={30} />
          </div>
          <span className="vl-brand-title">visionlytics</span>
        </Link>

        {/* Top Navigation Links */}
        <nav
          className={`vl-nav-links ${mobileOpen ? "open" : ""}`}
          aria-label="Main Navigation"
        >
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`vl-nav-link ${isActive ? "active" : ""}`}
                aria-current={isActive ? "page" : undefined}
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        {/* Right User Status & 1-Click Sign Out */}
        <div className="vl-header-actions" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          {currentUser ? (
            <>
              <Link
                href={isAdmin ? "/admin" : "/"}
                className="vl-user-profile-badge"
                title={isAdmin ? "System Administrator" : "Current Account"}
                style={{ textDecoration: "none", color: "inherit" }}
              >
                <div className="vl-avatar-circle" style={isAdmin ? { backgroundColor: "#0D9488", color: "#FFFFFF" } : {}}>
                  <User size={16} />
                </div>
                <span style={{ paddingRight: "6px", fontWeight: 600 }}>
                  {currentUser.username || (isAdmin ? "Admin" : "User")}
                </span>
              </Link>

              <button
                type="button"
                onClick={handleSignOut}
                title="Sign Out"
                className="vl-btn-outline"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "4px",
                  padding: "5px 10px",
                  fontSize: "0.82rem",
                  color: "#EF4444",
                  borderColor: "#FCA5A5",
                  backgroundColor: "#FEF2F2",
                  borderRadius: "var(--radius-full)",
                  cursor: "pointer",
                }}
              >
                <span>Sign Out</span>
              </button>
            </>
          ) : (
            <Link
              href="/login"
              className="vl-user-profile-badge"
              title="Account Access"
              style={{ textDecoration: "none", color: "inherit" }}
            >
              <div className="vl-avatar-circle">
                <User size={16} />
              </div>
              <span style={{ paddingRight: "6px" }}>Sign In</span>
            </Link>
          )}

          <button
            type="button"
            className="vl-mobile-toggle"
            onClick={() => setMobileOpen((prev) => !prev)}
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
          >
            {mobileOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
        </div>
      </div>
    </header>
  );
}
