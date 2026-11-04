import { forwardRef, useId, type InputHTMLAttributes } from "react";
import { cn } from "../lib/cn";

export interface FieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  hint?: string;
  error?: string;
}

/** Text field: label above, hairline bottom rule, error text tied via aria-describedby. */
export const Field = forwardRef<HTMLInputElement, FieldProps>(function Field(
  { label, hint, error, className, id, ...props },
  ref,
) {
  const auto = useId();
  const fid = id ?? auto;
  const desc = error ? `${fid}-err` : hint ? `${fid}-hint` : undefined;
  return (
    <div className={cn("grid gap-1.5", className)}>
      <label htmlFor={fid} className="text-sm text-muted">{label}</label>
      <input
        ref={ref}
        id={fid}
        aria-invalid={error ? true : undefined}
        aria-describedby={desc}
        className={cn(
          "h-10 rounded-[var(--radius-key)] border bg-bg px-3 text-base text-fg placeholder:text-faint",
          "transition-[border-color,box-shadow] duration-[var(--duration-quick)]",
          "focus-visible:border-signal focus-visible:shadow-[0_0_0_3px_var(--color-signal-wash)] focus-visible:outline-none",
          error ? "border-err" : "border-hairline-strong hover:border-fg/40",
        )}
        {...props}
      />
      {error ? (
        <p id={`${fid}-err`} className="text-sm text-err">{error}</p>
      ) : hint ? (
        <p id={`${fid}-hint`} className="text-sm text-muted">{hint}</p>
      ) : null}
    </div>
  );
});
