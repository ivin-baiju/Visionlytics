import { useEffect, useRef, useState, type ReactNode } from "react";
import { animate, useReducedMotion } from "motion/react";
import { cn } from "../lib/cn";
import { duration, ease } from "../motion";

/**
 * Readout: a large measured value. Digits roll like an odometer when the value
 * changes so a counter ticking 11 -> 12 reads as a measurement, not a re-render.
 */
export function Readout({
  value,
  label,
  unit,
  size = "lg",
  className,
}: {
  value: number;
  label: string;
  unit?: string;
  size?: "md" | "lg" | "xl";
  className?: string;
}) {
  const digits = String(Math.max(0, Math.round(value)));
  return (
    <div className={cn("grid gap-1", className)}>
      <span className="text-sm text-muted">{label}</span>
      <span
        className={cn(
          "tabular flex items-baseline leading-none text-fg",
          size === "md" && "text-2xl",
          size === "lg" && "text-4xl",
          size === "xl" && "text-6xl tracking-tight",
        )}
        aria-label={`${digits}${unit ? ` ${unit}` : ""}`}
        role="text"
      >
        <span aria-hidden className="flex">
          {digits.split("").map((d, i) => (
            <Digit key={digits.length - i} d={Number(d)} />
          ))}
        </span>
        {unit && <span aria-hidden className="ml-1.5 text-[0.4em] text-muted">{unit}</span>}
      </span>
    </div>
  );
}

function Digit({ d }: { d: number }) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLSpanElement>(null);
  const prev = useRef(d);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (reduce) {
      el.style.transform = `translateY(${-d * 10}%)`;
      return;
    }
    const controls = animate(prev.current, d, {
      duration: duration.slow,
      ease: ease.out,
      onUpdate: (v) => (el.style.transform = `translateY(${-v * 10}%)`),
    });
    prev.current = d;
    return () => controls.stop();
  }, [d, reduce]);
  return (
    <span className="relative inline-block h-[1em] overflow-hidden">
      <span ref={ref} className="flex flex-col" style={{ transform: `translateY(${-d * 10}%)` }}>
        {Array.from({ length: 10 }, (_, n) => (
          <span key={n} className="h-[1em] leading-none">{n}</span>
        ))}
      </span>
    </span>
  );
}

/**
 * Confidence: calibrated score plus an explicit "uncertain" state. The state is
 * carried by text and a glyph shape, never by colour alone.
 */
export function Confidence({ score, threshold = 0.5 }: { score: number; threshold?: number }) {
  const uncertain = score < threshold;
  return (
    <span
      className={cn(
        "tabular inline-flex items-center gap-1.5 rounded-[var(--radius-hair)] border px-1.5 py-0.5 text-2xs",
        uncertain ? "border-dashed border-warn/60 text-warn" : "border-hairline-strong text-fg",
      )}
    >
      <svg viewBox="0 0 8 8" className="size-2" aria-hidden>
        {uncertain ? (
          <circle cx="4" cy="4" r="3" fill="none" stroke="currentColor" strokeDasharray="1.5 1.5" />
        ) : (
          <circle cx="4" cy="4" r="3" fill="currentColor" />
        )}
      </svg>
      {uncertain ? `uncertain ${score.toFixed(2)}` : score.toFixed(2)}
    </span>
  );
}

/** Framed region with corner crop-marks. The bezel of every instrument panel. */
export function Panel({
  title,
  meta,
  children,
  className,
}: {
  title?: string;
  meta?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("crop-marks bg-surface/60 p-5", className)}>
      {(title || meta) && (
        <header className="mb-4 flex items-baseline justify-between gap-4 border-b border-hairline pb-3">
          {title && <h3 className="font-display text-lg font-semibold tracking-tight text-fg">{title}</h3>}
          {meta && <div className="text-sm text-muted">{meta}</div>}
        </header>
      )}
      {children}
    </section>
  );
}

/** A named colour chip: swatch + human name + share. Name is always visible text. */
export function ColourChip({ name, hex, share }: { name: string; hex: string; share?: number }) {
  return (
    <span className="inline-flex items-center gap-2 text-sm text-fg">
      <span className="size-3 rounded-[2px] ring-1 ring-hairline-strong" style={{ background: hex }} aria-hidden />
      <span>{name}</span>
      {share !== undefined && <span className="tabular text-2xs text-muted">{Math.round(share * 100)}%</span>}
    </span>
  );
}

export function useTicker(values: number[], ms: number) {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((n) => (n + 1) % values.length), ms);
    return () => clearInterval(t);
  }, [values.length, ms]);
  return values[i] ?? 0;
}
