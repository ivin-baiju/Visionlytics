"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { User, Menu, X } from "lucide-react";

interface NavLink {
  href: string;
  label: string;
}

const NAV_LINKS: NavLink[] = [
  { href: "/", label: "Dashboard" },
  { href: "/image-analysis", label: "Image Analysis" },
  { href: "/video-analysis", label: "Video Analysis" },
  { href: "/live-camera", label: "Live Camera" },
  { href: "/ml-models", label: "ML Suite" },
  { href: "/dataset", label: "Dataset" },
  { href: "/about", label: "Docs & Architecture" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <header className="vl-header" role="banner">
      <div className="vl-header-inner">
        {/* Lordicon style clean brand */}
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
          {NAV_LINKS.map((link) => {
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
          <div className="vl-user-profile-badge" title="Active Analyst Account">
            <div className="vl-avatar-circle">
              <User size={16} />
            </div>
            <span style={{ paddingRight: "6px" }}>Analyst</span>
          </div>

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
