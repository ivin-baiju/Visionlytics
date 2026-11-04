import { forwardRef, useRef, type ButtonHTMLAttributes, type ReactNode } from "react";
import {
  AnimatePresence,
  motion,
  type MotionStyle,
  useMotionValue,
  useReducedMotion,
  useSpring,
} from "motion/react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../lib/cn";
import { duration, ease, shake, spring } from "../motion";

export type ButtonStatus = "idle" | "loading" | "success" | "error";

const button = cva(
  [
    "group/btn relative isolate inline-flex select-none items-center justify-center gap-2 overflow-hidden",
    "rounded-[var(--radius-key)] font-sans font-medium whitespace-nowrap",
    "transition-[background-color,border-color,color] duration-[var(--duration-quick)]",
    "disabled:cursor-not-allowed disabled:opacity-40 aria-busy:cursor-progress aria-busy:opacity-100",
    "data-[status=error]:border-err data-[status=error]:bg-err data-[status=error]:text-bg",
    "data-[status=success]:border-ok data-[status=success]:bg-ok data-[status=success]:text-bg",
    "focus-visible:outline-1 focus-visible:outline-offset-3 focus-visible:outline-signal",
  ],
  {
    variants: {
      variant: {
        primary: "bg-signal text-signal-ink hover:brightness-[1.06]",
        secondary:
          "border border-hairline-strong bg-raised text-fg hover:border-fg/50",
        ghost: "text-muted hover:bg-raised hover:text-fg",
        danger: "border border-err/50 text-err hover:bg-err/10",
      },
      size: {
        sm: "h-8 px-3 text-sm",
        md: "h-10 px-4 text-base",
        lg: "h-12 px-6 text-lg",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  },
);

export interface ButtonProps
  extends Omit<
      ButtonHTMLAttributes<HTMLButtonElement>,
      "onAnimationStart" | "onDrag" | "onDragStart" | "onDragEnd" | "style"
    >,
    VariantProps<typeof button> {
  status?: ButtonStatus;
  /** 0..1 shows a determinate ring while loading; omit for indeterminate. */
  progress?: number;
  /** Magnetic hover pull. Defaults on for primary/lg. */
  magnetic?: boolean;
  /** Accessible text announced while loading. */
  loadingLabel?: string;
  icon?: ReactNode;
  style?: MotionStyle;
}

const RING = 2 * Math.PI * 7;

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    className,
    variant,
    size,
    status = "idle",
    progress,
    magnetic,
    loadingLabel = "Working",
    icon,
    children,
    disabled,
    onPointerMove,
    onPointerLeave,
    style,
    ...props
  },
  ref,
) {
  const reduce = useReducedMotion();
  const local = useRef<HTMLButtonElement | null>(null);
  const isMagnetic = (magnetic ?? (variant ?? "primary") === "primary") && !reduce;
  const mx = useSpring(useMotionValue(0), spring.magnet);
  const my = useSpring(useMotionValue(0), spring.magnet);
  const busy = status === "loading";

  return (
    <motion.button
      ref={(node) => {
        local.current = node;
        if (typeof ref === "function") ref(node);
        else if (ref) ref.current = node;
      }}
      className={cn(button({ variant, size }), className)}
      style={{ ...style, x: mx, y: my }}
      disabled={disabled || busy}
      aria-busy={busy || undefined}
      data-status={status}
      whileTap={disabled || busy || reduce ? {} : { scale: 0.965 }}
      transition={spring.key}
      animate={status === "error" && !reduce ? shake : { x: 0 }}
      onPointerMove={(e) => {
        onPointerMove?.(e);
        if (!isMagnetic || !local.current) return;
        const r = local.current.getBoundingClientRect();
        mx.set((e.clientX - (r.left + r.width / 2)) * 0.18);
        my.set((e.clientY - (r.top + r.height / 2)) * 0.28);
      }}
      onPointerLeave={(e) => {
        onPointerLeave?.(e);
        mx.set(0);
        my.set(0);
      }}
      {...props}
    >
      {/* Light sweep: a narrow specular band crossing on hover, like glass catching a lamp. */}
      {variant !== "ghost" && (
        <span
          aria-hidden
          className="pointer-events-none absolute inset-y-0 -left-1/2 w-1/3 -skew-x-12 bg-gradient-to-r from-transparent via-white/25 to-transparent opacity-0 transition-[transform,opacity] duration-[var(--duration-slow)] ease-[var(--ease-out)] group-hover/btn:translate-x-[640%] group-hover/btn:opacity-100 motion-reduce:hidden"
        />
      )}
      <AnimatePresence mode="popLayout" initial={false}>
        {status === "loading" ? (
          <motion.span
            key="loading"
            className="flex items-center gap-2"
            initial={{ opacity: 0, scale: 0.6 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.6 }}
            transition={{ duration: duration.quick, ease: ease.out }}
          >
            <motion.svg
              viewBox="0 0 18 18"
              className="size-[1.1em] -rotate-90"
              aria-hidden
              animate={progress === undefined && !reduce ? { rotate: [-90, 270] } : { rotate: -90 }}
              transition={{ repeat: Infinity, duration: 0.9, ease: "linear" }}
            >
              <circle cx="9" cy="9" r="7" fill="none" stroke="currentColor" strokeOpacity="0.25" strokeWidth="1.75" />
              <motion.circle
                cx="9"
                cy="9"
                r="7"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeDasharray={RING}
                initial={false}
                animate={{
                  strokeDashoffset:
                    progress === undefined
                      ? RING * 0.72
                      : RING * (1 - Math.min(Math.max(progress, 0), 1)),
                }}
                transition={{ duration: duration.quick }}
              />
            </motion.svg>
            <span className="sr-only">{loadingLabel}</span>
            {progress !== undefined && (
              <span className="tabular text-[0.85em]">{Math.round(progress * 100)}%</span>
            )}
          </motion.span>
        ) : status === "success" ? (
          <motion.span
            key="success"
            className="flex items-center gap-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <svg viewBox="0 0 18 18" className="size-[1.1em]" aria-hidden>
              <motion.path
                d="M3.5 9.5l3.5 3.5 7.5-8"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.75"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: duration.base, ease: ease.out }}
              />
            </svg>
            {children}
          </motion.span>
        ) : (
          <motion.span
            key="idle"
            className="flex items-center gap-2"
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: duration.quick, ease: ease.out }}
          >
            {icon}
            {children}
          </motion.span>
        )}
      </AnimatePresence>
      <span role="status" aria-live="polite" className="sr-only">
        {status === "success" ? "Done" : status === "error" ? "Failed" : ""}
      </span>
    </motion.button>
  );
});
