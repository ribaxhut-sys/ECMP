import type { HTMLAttributes, ReactNode } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { IconTrendDown, IconTrendUp } from "@/shared/icons";
import { Badge, type BadgeTone } from "@/shared/ui/badge";

export type StatTrend = "up" | "down" | "neutral";
export type StatHierarchy = "primary" | "secondary" | "supporting";
export type StatAccent =
  | "healthy"
  | "normal"
  | "attention"
  | "critical"
  | "archived";

export interface StatCardProps extends HTMLAttributes<HTMLElement> {
  title: string;
  value?: ReactNode;
  subtitle?: ReactNode;
  description?: ReactNode;
  trend?: StatTrend;
  delta?: ReactNode;
  status?: string;
  statusTone?: BadgeTone;
  accent?: StatAccent;
  hierarchy?: StatHierarchy;
  icon?: ReactNode;
  loading?: boolean;
  variant?: "default" | "emphasis";
}

const accentIconClass: Record<StatAccent, string> = {
  healthy: "bg-ecmp-success-subtle text-ecmp-success-text",
  normal: "bg-ecmp-info-subtle text-ecmp-info-text",
  attention: "bg-ecmp-warning-subtle text-ecmp-warning-text",
  critical: "bg-ecmp-danger-subtle text-ecmp-danger-text",
  archived: "bg-ecmp-secondary-muted text-ecmp-text-secondary",
};

const accentBorderClass: Record<StatAccent, string> = {
  healthy: "border-l-ecmp-success",
  normal: "border-l-ecmp-info",
  attention: "border-l-ecmp-warning",
  critical: "border-l-ecmp-danger",
  archived: "border-l-ecmp-secondary",
};

export function StatCard({
  className,
  title,
  value,
  subtitle,
  description,
  trend = "neutral",
  delta,
  status,
  statusTone = "neutral",
  accent = "normal",
  hierarchy = "secondary",
  icon,
  loading = false,
  variant = "default",
  ...props
}: StatCardProps) {
  const tCommon = useTranslations("common");
  const isPrimary = hierarchy === "primary";
  const isSupporting = hierarchy === "supporting";

  return (
    <article
      className={cn(
        "rounded-[var(--ecmp-radius-card)] border border-ecmp-border bg-ecmp-surface shadow-ecmp-raised",
        "border-l-4",
        accentBorderClass[accent],
        isPrimary && "p-5 md:p-6",
        !isPrimary && !isSupporting && "p-4 md:p-5",
        isSupporting && "p-3.5 md:p-4",
        variant === "emphasis" && "border-ecmp-primary/30 bg-ecmp-primary-muted/40",
        className,
      )}
      {...props}
    >
      <div className="flex items-start justify-between gap-3">
        <p
          className={cn(
            "text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary",
            isSupporting && "text-[length:var(--ecmp-font-caption-size)]",
          )}
        >
          {title}
        </p>
        {icon ? (
          <div
            className={cn(
              "flex items-center justify-center rounded-[var(--ecmp-radius-md)]",
              isPrimary ? "size-10" : "size-9",
              accentIconClass[accent],
            )}
          >
            {icon}
          </div>
        ) : null}
      </div>

      {loading ? (
        <div
          className="mt-3 space-y-2"
          aria-busy="true"
          aria-label={tCommon("loadingContent")}
        >
          <div className="h-8 animate-pulse rounded-[var(--ecmp-radius-md)] bg-ecmp-secondary-muted motion-reduce:animate-none" />
          <div className="h-4 w-1/2 animate-pulse rounded-[var(--ecmp-radius-md)] bg-ecmp-secondary-muted motion-reduce:animate-none" />
        </div>
      ) : (
        <>
          <p
            className={cn(
              "mt-3 tracking-tight text-ecmp-text-primary tabular-nums",
              isPrimary &&
                "text-[length:var(--ecmp-font-display-size)] font-[number:var(--ecmp-font-page-title-weight)] leading-none",
              !isPrimary &&
                !isSupporting &&
                "text-[length:var(--ecmp-font-page-title-size)] font-[number:var(--ecmp-font-page-title-weight)]",
              isSupporting &&
                "text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)]",
            )}
          >
            {value}
          </p>

          {(subtitle || description || delta || status || trend !== "neutral") && (
            <div className="mt-2 flex flex-col gap-1.5">
              <div className="flex flex-wrap items-center gap-2">
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
              </div>
              {subtitle ? (
                <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                  {subtitle}
                </p>
              ) : null}
              {description ? (
                <p className="text-[length:var(--ecmp-font-caption-size)] leading-relaxed text-ecmp-text-secondary">
                  {description}
                </p>
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
