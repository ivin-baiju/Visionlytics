"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sliders, Bell, User } from "lucide-react";

interface NavItem {
  href: string;
  label: string;
  sub?: string;
}

const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Dashboard" },
  { href: "/image-analysis", label: "Image", sub: "Analysis" },
  { href: "/video-analysis", label: "Video", sub: "Analysis" },
  { href: "/live-camera", label: "Live", sub: "Camera" },
  { href: "/ml-models", label: "ML", sub: "Models" },
  { href: "/dataset", label: "Dataset" },
  { href: "/about", label: "About" },
];

interface NavbarProps {
  onOpenSettings?: () => void;
}

export default function Navbar({ onOpenSettings }: NavbarProps) {
  const pathname = usePathname();

  return (
    <header className="vl-navbar">
      {/* Brand Pill */}
      <Link href="/" className="vl-brand-pill" title="Visionlytics Home">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/logo.svg"
          alt="Visionlytics Logo"
          className="vl-logo-svg"
          width={36}
          height={36}
        />
        <div className="vl-brand-text">
          <span className="vl-brand-title">VISIONLYTICS</span>
          <span className="vl-brand-sub">Crowd Analytics</span>
        </div>
      </Link>

      {/* Navigation Links Pill */}
      <nav className="vl-nav-pill">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`vl-nav-item ${isActive ? "active" : ""}`}
            >
              {item.sub ? (
                <>
                  <span className="vl-nav-top">{item.label}</span>
                  <span className="vl-nav-sub">{item.sub}</span>
                </>
              ) : (
                <span>{item.label}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Right Controls Pill */}
      <div className="vl-controls-pill">
        <button
          type="button"
          className="vl-icon-btn"
          title="System Settings"
          onClick={onOpenSettings}
        >
          <Sliders size={17} />
        </button>
        <button
          type="button"
          className="vl-icon-btn"
          title="System Notifications"
        >
          <Bell size={17} />
        </button>
        <div className="vl-avatar-btn" title="Logged in as Analyst">
          <User size={16} />
        </div>
      </div>
    </header>
  );
}
