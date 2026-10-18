"use client";

import React from "react";

interface SkeletonLoaderProps {
  /** Number of skeleton rows to show */
  rows?: number;
  /** Optional title for the skeleton section */
  title?: string;
}

/**
 * Animated skeleton placeholder that replaces empty content during loading.
 */
export default function SkeletonLoader({ rows = 4, title }: SkeletonLoaderProps) {
  return (
    <div className="vl-card" style={{ overflow: "hidden" }}>
      {title && (
        <div className="vl-card-header">
          <span className="vl-card-label">{title}</span>
        </div>
      )}
      <div style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
        {Array.from({ length: rows }).map((_, i) => {
          const widths = [75, 88, 65, 82, 70, 90];
          const width = widths[i % widths.length];
          return (
            <div key={i} className="vl-skeleton-row">
              <div
                className="vl-skeleton-bar"
                style={{ width: `${width}%` }}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
