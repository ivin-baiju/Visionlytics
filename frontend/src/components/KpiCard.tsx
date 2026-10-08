import React, { ReactNode } from "react";

interface KpiCardProps {
  label: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  trend?: string;
}

export default function KpiCard({ label, value, subtitle, icon, trend }: KpiCardProps) {
  return (
    <div className="vl-card">
      <div className="vl-card-header">
        <span className="vl-card-label">{label}</span>
        <div className="vl-card-icon">{icon}</div>
      </div>
      <div className="vl-kpi-value">{value}</div>
      {subtitle && (
        <div className="vl-kpi-subtitle">
          {trend && <span style={{ color: "var(--accent-emerald)", fontWeight: 600 }}>{trend}</span>}
          <span>{subtitle}</span>
        </div>
      )}
    </div>
  );
}
