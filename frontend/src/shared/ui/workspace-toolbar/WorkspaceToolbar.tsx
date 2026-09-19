import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface WorkspaceToolbarProps extends HTMLAttributes<HTMLDivElement> {
  summary?: ReactNode;
  search?: ReactNode;
  actions?: ReactNode;
  density?: ReactNode;
  refresh?: ReactNode;
  selectionLabel?: ReactNode;
  /** Sticky under the app header for list workspaces. */
  sticky?: boolean;
}

/**
 * List/workspace chrome: search, selection, density, refresh, bulk actions.
 */
export function WorkspaceToolbar({
  className,
  summary,
  search,
  actions,
  density,
  refresh,
  selectionLabel,
  sticky = true,
  ...props
}: WorkspaceToolbarProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-2.5 rounded-[var(--ecmp-radius-search)] border border-ecmp-border/80 bg-ecmp-surface/95 px-3 py-2.5 shadow-ecmp-raised backdrop-blur-sm",
        "sm:flex-row sm:items-center sm:justify-between sm:gap-[var(--ecmp-panel-gap)]",
        sticky &&
          // Scrollport is <main> (AppLayout shell), so stick to its top — not
          // under a document-level header offset.
          "sticky top-0 z-[calc(var(--ecmp-z-sticky-header)-1)]",
        className,
      )}
      {...props}
    >
      <div className="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:items-center">
        {search ? <div className="min-w-0 flex-1 sm:max-w-xs">{search}</div> : null}
        <div className="min-w-0 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
          {selectionLabel ?? summary}
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {density}
        {refresh}
        {actions}
      </div>
    </div>
  );
}
