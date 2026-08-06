import type { HTMLAttributes } from "react";
import { cn } from "@/shared/utils";

export type ProgressMeterTone =
  | "healthy"
  | "normal"
  | "attention"
  | "critical";

export interface ProgressMeterProps extends HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  label?: string;
  tone?: ProgressMeterTone;
  showValue?: boolean;
}

const toneBarClass: Record<ProgressMeterTone, string> = {
  healthy: "bg-ecmp-success",
  normal: "bg-ecmp-info",
  attention: "bg-ecmp-warning",
  critical: "bg-ecmp-danger",
};

/**
 * Compact progress indicator for queue/health surfaces.
 */
export function ProgressMeter({
  className,
  value,
  max = 100,
  label,
  tone = "normal",
  showValue = true,
  ...props
}: ProgressMeterProps) {
  const safeMax = max <= 0 ? 1 : max;
  const pct = Math.max(0, Math.min(100, (value / safeMax) * 100));

  return (
    <div className={cn("space-y-1.5", className)} {...props}>
      {(label || showValue) && (
        <div className="flex items-center justify-between gap-2 text-[length:var(--ecmp-font-helper-size)]">
          {label ? (
            <span className="text-ecmp-text-secondary">{label}</span>
          ) : (
            <span />
          )}
          {showValue ? (
            <span className="tabular-nums text-ecmp-text-primary">
              {Math.round(pct)}%
            </span>
          ) : null}
        </div>
      )}
      <div
        className="h-2 overflow-hidden rounded-[var(--ecmp-radius-full)] bg-ecmp-secondary-muted"
        role="progressbar"
        aria-valuenow={Math.round(pct)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label}
      >
        <div
          className={cn(
            "h-full rounded-[var(--ecmp-radius-full)] transition-[width] duration-[var(--ecmp-duration-normal)]",
            toneBarClass[tone],
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
