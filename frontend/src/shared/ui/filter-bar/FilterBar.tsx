import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface FilterBarProps extends HTMLAttributes<HTMLDivElement> {
  search?: ReactNode;
  filters?: ReactNode;
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
  actions,
  exportSlot,
  reset,
  ...props
}: FilterBarProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-[var(--ecmp-panel-gap)] rounded-[var(--ecmp-radius-card)] border border-ecmp-border bg-ecmp-surface p-3 shadow-ecmp-raised sm:p-4",
        className,
      )}
      {...props}
    >
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div className="flex min-w-0 flex-1 flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end">
          {search ? <div className="min-w-0 flex-1 sm:min-w-[12rem]">{search}</div> : null}
          {filters ? (
            <div className="flex min-w-0 flex-wrap items-end gap-2">{filters}</div>
          ) : null}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {reset}
          {exportSlot}
          {actions}
        </div>
      </div>
    </div>
  );
}
