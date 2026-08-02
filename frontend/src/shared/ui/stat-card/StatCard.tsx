import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/shared/utils";
import { IconTrendDown, IconTrendUp } from "@/shared/icons";
import { Badge, type BadgeTone } from "@/shared/ui/badge";

export type StatTrend = "up" | "down" | "neutral";

export interface StatCardProps extends HTMLAttributes<HTMLElement> {
  title: string;
  value?: ReactNode;
  subtitle?: ReactNode;
  trend?: StatTrend;
  delta?: ReactNode;
  status?: string;
  statusTone?: BadgeTone;
  icon?: ReactNode;
  loading?: boolean;
  variant?: "default" | "emphasis";
}

export function StatCard({
  className,
  title,
  value,
  subtitle,
  trend = "neutral",
  delta,
  status,
  statusTone = "neutral",
  icon,
  loading = false,
  variant = "default",
  ...props
}: StatCardProps) {
  return (
    <article
      className={cn(
        "rounded-[var(--ecmp-radius-card)] border border-ecmp-border bg-ecmp-surface p-4 shadow-ecmp-raised md:p-5",
        "transition-[box-shadow,border-color] duration-[var(--ecmp-duration-normal)] ease-[var(--ecmp-ease-hover)]",
        "hover:shadow-ecmp-hover",
        variant === "emphasis" && "border-ecmp-primary/30 bg-ecmp-primary-muted/40",
        className,
      )}
      {...props}
    >
      <div className="flex items-start justify-between gap-3">
        <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
          {title}
        </p>
        {icon ? (
          <div className="flex size-9 items-center justify-center rounded-[var(--ecmp-radius-md)] bg-ecmp-surface-sunken text-ecmp-text-secondary">
            {icon}
          </div>
        ) : null}
      </div>

      {loading ? (
        <div
          className="mt-3 space-y-2"
          aria-busy="true"
          aria-label="Loading"
        >
          <div className="h-8 animate-pulse rounded-[var(--ecmp-radius-md)] bg-ecmp-secondary-muted motion-reduce:animate-none" />
          <div className="h-4 w-1/2 animate-pulse rounded-[var(--ecmp-radius-md)] bg-ecmp-secondary-muted motion-reduce:animate-none" />
        </div>
      ) : (
        <>
          <p className="mt-3 text-[length:var(--ecmp-font-page-title-size)] font-[number:var(--ecmp-font-page-title-weight)] tracking-tight text-ecmp-text-primary">
            {value}
          </p>
          {(subtitle || delta || status) && (
            <div className="mt-2 flex flex-wrap items-center gap-2">
              {trend !== "neutral" ? (
                <span
                  className={cn(
                    "inline-flex items-center gap-1 text-[length:var(--ecmp-font-helper-size)]",
                    trend === "up" && "text-ecmp-success-text",
                    trend === "down" && "text-ecmp-danger-text",
                  )}
                >
                  {trend === "up" ? (
                    <IconTrendUp className="size-4" aria-hidden />
                  ) : (
                    <IconTrendDown className="size-4" aria-hidden />
                  )}
                  {delta}
                </span>
              ) : delta ? (
                <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {delta}
                </span>
              ) : null}
              {status ? <Badge tone={statusTone}>{status}</Badge> : null}
              {subtitle ? (
                <span className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {subtitle}
                </span>
              ) : null}
            </div>
          )}
        </>
      )}
    </article>
  );
}

/** Alias for StatCard — same presentational KPI tile. */
export const MetricCard = StatCard;
