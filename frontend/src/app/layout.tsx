import type { Metadata } from "next";
import "./globals.css";
import BackgroundVideo from "@/components/BackgroundVideo";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "VISIONLYTICS — Intelligent Visual Crowd Analytics",
  description:
    "Production-grade computer vision and statistical machine learning platform for real-time crowd dynamics, spatial density estimation, and safety monitoring.",
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
        {/* Top Glowing Ambient Bar */}
        <div className="vl-top-bar" />

        {/* Looping ambient background video with overlay */}
        <BackgroundVideo />

        {/* Floating Pill Top Navbar */}
        <Navbar />

        {/* Main Content Area */}
        <main>{children}</main>
      </body>
    </html>
  );
}
