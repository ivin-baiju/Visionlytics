import { createContext, useContext, useId, useState, type ReactNode } from "react";
import { Tabs as RTabs } from "radix-ui";
import { motion } from "motion/react";
import { cn } from "../lib/cn";
import { spring } from "../motion";

const ActiveCtx = createContext<{ value: string; group: string }>({ value: "", group: "" });

export interface TabsProps {
  value?: string;
  defaultValue: string;
  onValueChange?: (v: string) => void;
  children: ReactNode;
  className?: string;
}

/** Tabs with a shared-layout indicator that springs between triggers. */
export function Tabs({ value, defaultValue, onValueChange, children, className }: TabsProps) {
  const [inner, setInner] = useState(defaultValue);
  const current = value ?? inner;
  const group = useId();
  return (
    <ActiveCtx.Provider value={{ value: current, group }}>
      <RTabs.Root
        value={current}
        onValueChange={(v) => {
          setInner(v);
          onValueChange?.(v);
        }}
        className={className}
      >
        {children}
      </RTabs.Root>
    </ActiveCtx.Provider>
  );
}

export function TabsList({ children, className, label }: { children: ReactNode; className?: string; label: string }) {
  return (
    <RTabs.List
      aria-label={label}
      className={cn("relative flex gap-1 border-b border-hairline", className)}
    >
      {children}
    </RTabs.List>
  );
}

export function TabsTrigger({ value, children, count }: { value: string; children: ReactNode; count?: number }) {
  const { value: active, group } = useContext(ActiveCtx);
  const on = active === value;
  return (
    <RTabs.Trigger
      value={value}
      className={cn(
        "relative -mb-px flex h-10 items-center gap-2 px-3 text-sm transition-colors duration-[var(--duration-quick)]",
        "focus-visible:outline-offset-0",
        on ? "text-fg" : "text-muted hover:text-fg",
      )}
    >
      {children}
      {count !== undefined && (
        <span className={cn("tabular text-2xs", on ? "text-signal" : "text-faint")}>{count}</span>
      )}
      {on && (
        <motion.span
          layoutId={`tab-indicator-${group}`}
          transition={spring.indicator}
          className="absolute inset-x-2 -bottom-px h-px bg-signal"
          aria-hidden
        />
      )}
    </RTabs.Trigger>
  );
}

export const TabsContent = ({ value, children, className }: { value: string; children: ReactNode; className?: string }) => (
  <RTabs.Content value={value} className={cn("pt-4 focus-visible:outline-none", className)}>
    {children}
  </RTabs.Content>
);
