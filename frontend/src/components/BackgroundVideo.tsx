"use client";

import React from "react";

export default function BackgroundVideo() {
  return (
    <>
      {/* Looping ambient background video behind all content */}
      <div className="vl-bg-wrap">
        <video autoPlay muted loop playsInline>
          <source src="/bg_video.mp4" type="video/mp4" />
        </video>
      </div>

      {/* Colour overlay + frost */}
      <div className="vl-bg-overlay" />

      {/* Floating animated orbs / particles */}
      <div className="vl-particles" aria-hidden="true">
        <span className="vl-orb vl-orb-1" />
        <span className="vl-orb vl-orb-2" />
        <span className="vl-orb vl-orb-3" />
        <span className="vl-orb vl-orb-4" />
        <span className="vl-orb vl-orb-5" />
        <span className="vl-orb vl-orb-6" />
      </div>
    </>
  );
}
