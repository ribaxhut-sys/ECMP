import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface QuickFilterOption {
  id: string;
  label: string;
  active?: boolean;
  disabled?: boolean;
  tone?: "default" | "critical" | "attention" | "healthy";
  count?: number;
}

export interface QuickFiltersProps
  extends Omit<HTMLAttributes<HTMLDivElement>, "onSelect"> {
  options: readonly QuickFilterOption[];
  onSelect: (id: string) => void;
  label?: string;
  trailing?: ReactNode;
}

const toneActiveClass: Record<
  NonNullable<QuickFilterOption["tone"]>,
  string
> = {
  default:
    "border-ecmp-primary bg-ecmp-primary-muted text-ecmp-primary",
  critical:
    "border-ecmp-danger bg-ecmp-danger-subtle text-ecmp-danger-text",
  attention:
    "border-ecmp-warning bg-ecmp-warning-subtle text-ecmp-warning-text",
  healthy:
    "border-ecmp-success bg-ecmp-success-subtle text-ecmp-success-text",
};

/**
 * Horizontal chip filters for workspace list surfaces.
 * Parent owns filter state; this is presentation only.
 */
export function QuickFilters({
  className,
  options,
  onSelect,
  label,
  trailing,
  ...props
}: QuickFiltersProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
      {...props}
    >
      <div className="min-w-0">
        {label ? (
          <p className="mb-2 text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
            {label}
          </p>
        ) : null}
        <div
          className="flex flex-wrap gap-2"
          role="toolbar"
          aria-label={label}
        >
          {options.map((option) => {
            const tone = option.tone ?? "default";
            const disabled = option.disabled === true;
            return (
              <button
                key={option.id}
                type="button"
                onClick={() => {
                  if (disabled) return;
                  onSelect(option.id);
                }}
                aria-pressed={option.active === true}
                aria-disabled={disabled || undefined}
                disabled={disabled}
                className={cn(
                  "inline-flex min-h-9 min-w-9 items-center gap-1.5 rounded-[var(--ecmp-radius-full)] border px-3 py-1.5",
                  "text-[length:var(--ecmp-font-helper-size)] font-medium",
                  "transition-[background-color,border-color,color,box-shadow] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]",
                  "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]",
                  disabled &&
                    "cursor-not-allowed opacity-50 hover:bg-ecmp-surface hover:text-ecmp-text-secondary",
                  !disabled &&
                    option.active &&
                    toneActiveClass[tone],
                  !disabled &&
                    !option.active &&
                    "border-ecmp-border bg-ecmp-surface text-ecmp-text-secondary hover:bg-ecmp-hover hover:text-ecmp-text-primary",
                )}
              >
                <span>{option.label}</span>
                {typeof option.count === "number" ? (
                  <span
                    className={cn(
                      "tabular-nums",
                      option.active
                        ? "opacity-90"
                        : "text-ecmp-text-secondary",
                    )}
                  >
                    {option.count}
                  </span>
                ) : null}
              </button>
            );
          })}
        </div>
      </div>
      {trailing ? <div className="shrink-0">{trailing}</div> : null}
    </div>
  );
}
