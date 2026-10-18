import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import ScrollToTop from "@/components/ScrollToTop";
import ErrorBoundary from "@/components/ErrorBoundary";

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

        {/* Clean, authentic footer */}
        <footer className="vl-footer">
          <div className="vl-footer-inner">
            <span>© {new Date().getFullYear()} Visionlytics Platform. All rights reserved.</span>
            <span className="vl-footer-author">
              Visionlytics Open Source Research
            </span>
          </div>
        </footer>
      </body>
    </html>
  );
}
