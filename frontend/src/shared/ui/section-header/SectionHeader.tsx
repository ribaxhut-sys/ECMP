import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";

export interface SectionHeaderProps extends HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: ReactNode;
  actions?: ReactNode;
}

export function SectionHeader({
  className,
  title,
  description,
  actions,
  ...props
}: SectionHeaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between",
        className,
      )}
      {...props}
    >
      <div className="min-w-0">
        <h2 className="text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] leading-[var(--ecmp-font-section-title-line)] text-ecmp-text-primary">
          {title}
        </h2>
        {description ? (
          <div className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
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
