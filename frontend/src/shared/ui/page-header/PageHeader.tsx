import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";
import {
  Breadcrumb,
  type BreadcrumbItem,
} from "@/shared/ui/breadcrumb";

export interface PageHeaderProps extends HTMLAttributes<HTMLElement> {
  /** Optional overline / workspace type label above the title. */
  overline?: string;
  title: string;
  description?: ReactNode;
  breadcrumbs?: readonly BreadcrumbItem[];
  actions?: ReactNode;
  /** Optional meta strip under the title (badges, status chips). */
  meta?: ReactNode;
}

/**
 * Page hero chrome — overline, breadcrumb, title, subtitle, meta, actions.
 * Spacing aligned with shell layout tokens.
 */
export function PageHeader({
  className,
  overline,
  title,
  description,
  breadcrumbs,
  actions,
  meta,
  ...props
}: PageHeaderProps) {
  return (
    <header
      className={cn(
        "mb-[var(--ecmp-section-gap)] flex flex-col gap-[var(--ecmp-panel-gap)]",
        "border-b border-ecmp-border/70 pb-[var(--ecmp-section-gap)]",
        "md:flex-row md:items-start md:justify-between md:gap-[var(--ecmp-section-gap)]",
        className,
      )}
      {...props}
    >
      <div className="min-w-0 space-y-2">
        {breadcrumbs ? <Breadcrumb items={breadcrumbs} /> : null}
        {overline ? (
          <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-primary">
            {overline}
          </p>
        ) : null}
        <h1 className="text-[length:var(--ecmp-font-page-title-size)] font-[number:var(--ecmp-font-page-title-weight)] leading-[var(--ecmp-font-page-title-line)] tracking-tight text-ecmp-text-primary">
          {title}
        </h1>
        {description ? (
          <div className="max-w-3xl text-[length:var(--ecmp-font-body-size)] leading-relaxed text-ecmp-text-secondary">
            {description}
          </div>
        ) : null}
        {meta ? (
          <div className="flex flex-wrap items-center gap-2 pt-1">{meta}</div>
        ) : null}
      </div>
      {actions ? (
        <div className="flex shrink-0 flex-wrap items-center gap-2 md:pt-1">
          {actions}
        </div>
      ) : null}
    </header>
  );
}
