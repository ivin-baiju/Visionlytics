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
  const [userLabel, setUserLabel] = useState("Sign In");

  useEffect(() => {
    try {
      const savedUser = localStorage.getItem("visionlytics_user");
      if (savedUser) {
        const parsed = JSON.parse(savedUser);
        if (parsed?.role === "admin") {
          setIsAdmin(true);
          setUserLabel("Portal");
        } else if (parsed?.username) {
          setUserLabel(parsed.username);
        }
      }
    } catch {
      // Keep defaults
    }
  }, [pathname]);

  const navLinks = isAdmin
    ? [...PUBLIC_NAV_LINKS, { href: "/admin", label: "System Console" }]
    : PUBLIC_NAV_LINKS;

  return (
    <header className="vl-header" role="banner">
      <div className="vl-header-inner">
        {/* Clean brand */}
        <Link href="/" className="vl-brand-link">
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

        {/* Right User Status */}
        <div className="vl-header-actions">
          <Link
            href={isAdmin ? "/admin" : "/login"}
            className="vl-user-profile-badge"
            title={isAdmin ? "System Management" : "Account Access"}
            style={{ textDecoration: "none", color: "inherit" }}
          >
            <div className="vl-avatar-circle">
              <User size={16} />
            </div>
            <span style={{ paddingRight: "6px" }}>{userLabel}</span>
          </Link>

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
