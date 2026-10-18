import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import Navbar from "@/components/Navbar";
import ScrollToTop from "@/components/ScrollToTop";
import ErrorBoundary from "@/components/ErrorBoundary";
import CookieConsentBanner from "@/components/CookieConsentBanner";

export const metadata: Metadata = {
  title: "Visionlytics — Computer Vision & Crowd Intelligence",
  description:
    "Enterprise crowd analysis platform with spatial feature extraction, YOLO perception, and statistical ML classifiers.",
  icons: {
    icon: "/logo.svg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <a href="#main-content" className="vl-skip-link">
          Skip to main content
        </a>

        {/* Top Clean Navbar */}
        <Navbar />

        {/* Main Content Area */}
        <main id="main-content">
          <ErrorBoundary>
            <ScrollToTop />
            {children}
          </ErrorBoundary>
        </main>

        {/* Compliant Footer with Legal Links & Business Info */}
        <footer className="vl-footer" role="contentinfo">
          <div className="vl-footer-inner" style={{ flexDirection: "column", gap: "14px", alignItems: "center" }}>
            <div style={{ display: "flex", gap: "18px", flexWrap: "wrap", justifyContent: "center", fontSize: "0.85rem" }}>
              <Link href="/privacy-policy" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>
                Privacy Policy
              </Link>
              <span aria-hidden="true" style={{ color: "var(--border-subtle)" }}>•</span>
              <Link href="/terms-and-conditions" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>
                Terms & Conditions
              </Link>
              <span aria-hidden="true" style={{ color: "var(--border-subtle)" }}>•</span>
              <Link href="/cookies-policy" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>
                Cookies Policy
              </Link>
              <span aria-hidden="true" style={{ color: "var(--border-subtle)" }}>•</span>
              <Link href="/refund-policy" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>
                Refund Policy
              </Link>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", width: "100%", flexWrap: "wrap", gap: "10px", borderTop: "1px solid var(--border-subtle)", paddingTop: "12px", fontSize: "0.82rem", color: "var(--text-tertiary)" }}>
              <span>© {new Date().getFullYear()} Visionlytics Labs. Open Source Research. All rights reserved.</span>
              <span>Contact: compliance@visionlytics.ai • Kerala, India</span>
            </div>
          </div>
        </footer>

        {/* Cookie & Consent Banner */}
        <CookieConsentBanner />
      </body>
    </html>
  );
}
