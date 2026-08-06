import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface PanelHeaderProps extends HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: ReactNode;
  actions?: ReactNode;
}

export function PanelHeader({
  className,
  title,
  description,
  actions,
  ...props
}: PanelHeaderProps) {
  return (
    <div
      className={cn(
        "mb-[var(--ecmp-panel-gap)] flex flex-col gap-2 border-b border-ecmp-border pb-[var(--ecmp-space-12)] sm:flex-row sm:items-center sm:justify-between",
        className,
      )}
      {...props}
    >
      <div className="min-w-0">
        <h3 className="text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] leading-[var(--ecmp-font-card-title-line)] text-ecmp-text-primary">
          {title}
        </h3>
        {description ? (
          <div className="mt-0.5 text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
            {description}
          </div>
        ) : null}
      </div>
      {actions ? (
        <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div>
      ) : null}
    </div>
  );
}
