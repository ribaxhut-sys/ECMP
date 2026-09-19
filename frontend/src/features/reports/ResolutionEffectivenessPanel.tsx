"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import type { StatusCount } from "@/lib/api/types";
import { cn } from "@/shared/utils";
import {
  Empty,
  SectionHeader,
  Skeleton,
  StatCard,
} from "@/shared/ui";
import {
  escalationTotal,
  operationalHealthFromRate,
  resolutionBuckets,
  resolutionMixRows,
  resolutionRatePercent,
  type ResolutionMixKey,
} from "./reportSummaryStats";

const MIX_BAR_CLASS: Record<ResolutionMixKey, string> = {
  resolved: "bg-ecmp-success",
  inProgress: "bg-ecmp-primary",
  waiting: "bg-ecmp-warning",
  escalated: "bg-ecmp-danger",
};

const MIX_DOT_CLASS: Record<ResolutionMixKey, string> = {
  resolved: "bg-ecmp-success",
  inProgress: "bg-ecmp-primary",
  waiting: "bg-ecmp-warning",
  escalated: "bg-ecmp-danger",
};

export function ResolutionEffectivenessPanel({
  rows,
  loading,
}: {
  rows: StatusCount[] | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");
  const buckets = useMemo(() => resolutionBuckets(rows), [rows]);
  const mix = useMemo(
    () => (buckets ? resolutionMixRows(buckets) : []),
    [buckets],
  );
  const resolvedRate = resolutionRatePercent(
    buckets
      ? {
          total:
            buckets.resolved +
            buckets.waiting +
            buckets.inProgress +
            escalationTotal(buckets),
          open: 0,
          closed: buckets.resolved,
        }
      : null,
  );
  const resolvedHealth = operationalHealthFromRate(resolvedRate);

  return (
    <section
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("resolutionEffectiveness")}
    >
      <SectionHeader
        title={t("resolutionEffectiveness")}
        description={t("resolutionEffectivenessDescription")}
      />

      {loading ? (
        <Skeleton rows={3} />
      ) : !buckets ? (
        <Empty
          title={t("noResolutionData")}
          description={t("noResolutionDataDescription")}
        />
      ) : (
        <div className="space-y-[var(--ecmp-card-gap)]">
          {mix.length > 0 ? (
            <div className="rounded-[var(--ecmp-radius-card)] border border-ecmp-border/80 bg-ecmp-surface p-4 shadow-ecmp-raised">
              <p className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
                {t("resolutionMix")}
              </p>
              <div
                className="mt-3 flex h-2.5 overflow-hidden rounded-[var(--ecmp-radius-full)] bg-ecmp-secondary-muted"
                role="img"
                aria-label={t("resolutionMix")}
              >
                {mix
                  .filter((row) => row.share > 0)
                  .map((row) => (
                    <div
                      key={row.key}
                      className={cn("h-full", MIX_BAR_CLASS[row.key])}
                      style={{ width: `${row.share}%` }}
                      title={`${t(row.key)} ${row.share}%`}
                    />
                  ))}
              </div>
              <ul className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5">
                {mix.map((row) => (
                  <li
                    key={row.key}
                    className="flex items-center gap-1.5 text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary"
                  >
                    <span
                      className={cn(
                        "size-2 shrink-0 rounded-full",
                        MIX_DOT_CLASS[row.key],
                      )}
                      aria-hidden
                    />
                    <span>{t(row.key)}</span>
                    <span className="tabular-nums text-ecmp-text-primary">
                      {row.count} ({row.share}%)
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              hierarchy="secondary"
              accent={resolvedHealth?.tone ?? "normal"}
              title={t("resolved")}
              value={<span className="tabular-nums">{buckets.resolved}</span>}
              status={resolvedHealth ? t(resolvedHealth.labelKey) : undefined}
              statusTone={
                resolvedHealth?.labelKey === "healthy"
                  ? "success"
                  : resolvedHealth?.labelKey === "attention"
                    ? "warning"
                    : resolvedHealth
                      ? "danger"
                      : undefined
              }
              subtitle={t("resolvedStory")}
            />
            <StatCard
              hierarchy="secondary"
              accent="normal"
              title={t("inProgress")}
              value={<span className="tabular-nums">{buckets.inProgress}</span>}
              subtitle={t("inProgressStory")}
            />
            <StatCard
              hierarchy="secondary"
              accent="attention"
              title={t("waiting")}
              value={<span className="tabular-nums">{buckets.waiting}</span>}
              status={buckets.waiting > 0 ? t("attention") : t("healthy")}
              statusTone={buckets.waiting > 0 ? "warning" : "success"}
              subtitle={t("waitingStory")}
            />
            <StatCard
              hierarchy="secondary"
              accent="critical"
              title={t("escalated")}
              value={
                <span className="tabular-nums">{escalationTotal(buckets)}</span>
              }
              status={
                escalationTotal(buckets) > 0 ? t("attention") : t("healthy")
              }
              statusTone={
                escalationTotal(buckets) > 0 ? "warning" : "success"
              }
              subtitle={
                buckets.escalationScheduled > 0
                  ? t("escalatedStoryWithScheduled", {
                      scheduled: buckets.escalationScheduled,
                    })
                  : buckets.escalationApproved > 0
                    ? t("escalatedStoryWithApproved", {
                        approved: buckets.escalationApproved,
                      })
                    : t("escalatedStory")
              }
            />
          </div>
        </div>
      )}
    </section>
  );
}
