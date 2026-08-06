import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface FilterBarProps extends HTMLAttributes<HTMLDivElement> {
  search?: ReactNode;
  filters?: ReactNode;
  advanced?: ReactNode;
  advancedOpen?: boolean;
  onAdvancedToggle?: () => void;
  advancedToggleLabel?: string;
  actions?: ReactNode;
  exportSlot?: ReactNode;
  reset?: ReactNode;
}

/**
 * Presentational filter chrome. Parent owns filter/search state and handlers.
 */
export function FilterBar({
  className,
  search,
  filters,
  advanced,
  advancedOpen = false,
  onAdvancedToggle,
  advancedToggleLabel = "Advanced filters",
  actions,
  exportSlot,
  reset,
  ...props
}: FilterBarProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-[var(--ecmp-panel-gap)] rounded-[var(--ecmp-radius-card)] border border-ecmp-border/80 bg-ecmp-surface p-3 shadow-ecmp-raised sm:p-4",
        className,
      )}
      {...props}
    >
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div className="flex min-w-0 flex-1 flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end">
          {search ? (
            <div className="min-w-0 flex-1 sm:min-w-[14rem]">{search}</div>
          ) : null}
          {filters ? (
            <div className="flex min-w-0 flex-wrap items-end gap-2">
              {filters}
            </div>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {advanced && onAdvancedToggle ? (
            <button
              type="button"
              onClick={onAdvancedToggle}
              aria-expanded={advancedOpen}
              className={cn(
                "inline-flex min-h-9 items-center rounded-[var(--ecmp-radius-button)] border border-ecmp-border bg-ecmp-surface px-3",
                "text-[length:var(--ecmp-font-helper-size)] font-medium text-ecmp-text-secondary",
                "hover:bg-ecmp-hover hover:text-ecmp-text-primary",
                "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]",
                advancedOpen && "border-ecmp-primary/40 bg-ecmp-primary-muted text-ecmp-primary",
              )}
            >
              {advancedToggleLabel}
            </button>
          ) : null}
          {reset}
          {exportSlot}
          {actions}
        </div>
      </div>
      {advanced && advancedOpen ? (
        <div className="flex flex-wrap items-end gap-2 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
          {advanced}
        </div>
      ) : null}
    </div>
  );
}
