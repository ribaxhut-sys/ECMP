import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";
import {
  Breadcrumb,
  type BreadcrumbItem,
} from "@/shared/ui/breadcrumb";

export interface PageHeaderProps extends HTMLAttributes<HTMLElement> {
  title: string;
  description?: ReactNode;
  breadcrumbs?: readonly BreadcrumbItem[];
  actions?: ReactNode;
}

export function PageHeader({
  className,
  title,
  description,
  breadcrumbs,
  actions,
  ...props
}: PageHeaderProps) {
  return (
    <header
      className={cn(
        "flex flex-col gap-4 border-b border-ecmp-border pb-4 md:flex-row md:items-end md:justify-between",
        className,
      )}
      {...props}
    >
      <div className="min-w-0 space-y-2">
        {breadcrumbs ? <Breadcrumb items={breadcrumbs} /> : null}
        <h1 className="text-[length:var(--ecmp-font-heading-size)] font-[number:var(--ecmp-font-heading-weight)] tracking-tight text-ecmp-text-primary">
          {title}
        </h1>
        {description ? (
          <div className="max-w-3xl text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
            {description}
          </div>
        ) : null}
      </div>
      {actions ? (
        <div className="flex flex-wrap items-center gap-2">{actions}</div>
      ) : null}
    </header>
  );
}
