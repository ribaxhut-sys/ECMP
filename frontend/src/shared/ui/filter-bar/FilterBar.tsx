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
  /** One visual row (search + filters + actions). Wraps only if the viewport is too narrow. */
  inline?: boolean;
  /**
   * Default (non-inline) layout only. Internal Complaints puts search on the
   * second row so Status/Kategori/Prioritas stay on one line with the actions.
   */
  searchPlacement?: "top" | "bottom";
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
  inline = false,
  searchPlacement = "top",
  ...props
}: FilterBarProps) {
  const actionsCluster = (
    <div className="flex shrink-0 flex-wrap items-center gap-2">
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
  );

  return (
    <div
      className={cn(
        "flex flex-col gap-[var(--ecmp-panel-gap)] rounded-[var(--ecmp-radius-card)] border border-ecmp-border/80 bg-ecmp-surface p-3 shadow-ecmp-raised sm:p-4",
        className,
      )}
      {...props}
    >
      {inline ? (
        <div className="flex flex-row flex-wrap items-end gap-3">
          <div className="flex min-w-0 flex-1 flex-row flex-wrap items-end gap-3">
            {search ? <div className="min-w-[10rem] flex-1">{search}</div> : null}
            {filters ? (
              <div className="flex min-w-0 flex-wrap items-end gap-2">
                {filters}
              </div>
            ) : null}
          </div>
          {actionsCluster}
        </div>
      ) : (
        // Two rows. Filter fields use a grid so FormField `w-full` does not
        // stack each Select on its own line. Search may sit above or below.
        <div className="flex flex-col gap-3">
          {searchPlacement !== "bottom" && search ? (
            <div className="min-w-0 w-full">{search}</div>
          ) : null}
          {filters || reset || actions || exportSlot || advanced ? (
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              {filters ? (
                <div className="grid min-w-0 w-full flex-1 grid-cols-1 gap-2 sm:grid-cols-3">
                  {filters}
                </div>
              ) : (
                <div />
              )}
              {actionsCluster}
            </div>
          ) : null}
          {searchPlacement === "bottom" && search ? (
            <div className="min-w-0 w-full">{search}</div>
          ) : null}
        </div>
      )}
      {advanced && advancedOpen ? (
        <div className="flex flex-wrap items-end gap-2 border-t border-ecmp-border pt-[var(--ecmp-panel-gap)]">
          {advanced}
        </div>
      ) : null}
    </div>
  );
}
