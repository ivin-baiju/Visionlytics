import { useId } from "react";
import { Switch as RSwitch, Slider as RSlider } from "radix-ui";
import { motion } from "motion/react";
import { cn } from "../lib/cn";
import { spring } from "../motion";

export interface SwitchProps {
  checked: boolean;
  onCheckedChange: (v: boolean) => void;
  label: string;
  description?: string;
  disabled?: boolean;
}

/** Toggle styled as a two-position instrument switch. State is shown by position AND text. */
export function Switch({ checked, onCheckedChange, label, description, disabled }: SwitchProps) {
  const id = useId();
  return (
    <div className="flex items-start justify-between gap-6">
      <label htmlFor={id} className="grid gap-0.5">
        <span className="text-base text-fg">{label}</span>
        {description && <span className="text-sm text-muted">{description}</span>}
      </label>
      <div className="flex items-center gap-2">
        <span className="tabular w-6 text-right text-2xs text-muted" aria-hidden>
          {checked ? "on" : "off"}
        </span>
        <RSwitch.Root
          id={id}
          checked={checked}
          onCheckedChange={onCheckedChange}
          disabled={disabled}
          className={cn(
            "relative flex h-6 w-11 shrink-0 items-center rounded-[var(--radius-key)] border px-0.5 transition-colors duration-[var(--duration-quick)]",
            "disabled:opacity-40",
            checked ? "justify-end border-signal bg-signal-wash" : "justify-start border-hairline-strong bg-surface",
          )}
        >
          <RSwitch.Thumb asChild>
            <motion.span
              layout
              transition={spring.key}
              className={cn(
                "block size-[18px] rounded-[4px]",
                checked ? "bg-signal" : "bg-muted",
              )}
            />
          </RSwitch.Thumb>
        </RSwitch.Root>
      </div>
    </div>
  );
}

export interface SliderProps {
  label: string;
  value: number;
  onValueChange: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
  format?: (v: number) => string;
}

/** Slider with a graduated scale and a live mono readout. */
export function Slider({ label, value, onValueChange, min = 0, max = 1, step = 0.01, format = (v) => v.toFixed(2) }: SliderProps) {
  const ticks = 10;
  return (
    <div className="grid gap-2">
      <div className="flex items-baseline justify-between">
        <span className="text-sm text-muted" id={`${label}-l`}>{label}</span>
        <output className="tabular text-sm text-fg">{format(value)}</output>
      </div>
      <RSlider.Root
        value={[value]}
        onValueChange={([v]) => v !== undefined && onValueChange(v)}
        min={min}
        max={max}
        step={step}
        aria-labelledby={`${label}-l`}
        className="relative flex h-6 touch-none select-none items-center"
      >
        <RSlider.Track className="relative h-px grow bg-hairline-strong">
          <RSlider.Range className="absolute h-px bg-signal" />
        </RSlider.Track>
        <div aria-hidden className="pointer-events-none absolute inset-x-0 top-[calc(50%+5px)] flex justify-between">
          {Array.from({ length: ticks + 1 }, (_, i) => (
            <span key={i} className={cn("w-px bg-hairline-strong", i % 5 === 0 ? "h-2" : "h-1")} />
          ))}
        </div>
        <RSlider.Thumb
          aria-label={label}
          className="block h-4 w-2 rounded-[2px] border border-signal bg-bg transition-transform duration-[var(--duration-instant)] hover:scale-y-125 focus-visible:scale-y-125"
        />
      </RSlider.Root>
    </div>
  );
}
