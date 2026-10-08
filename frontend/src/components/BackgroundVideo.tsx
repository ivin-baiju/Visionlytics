"use client";

import React from "react";

export default function BackgroundVideo() {
  return (
    <>
      <div className="vl-bg-wrap">
        <video autoPlay muted loop playsInline>
          <source src="/bg_video.mp4" type="video/mp4" />
        </video>
      </div>
      <div className="vl-bg-overlay" />
    </>
  );
}
