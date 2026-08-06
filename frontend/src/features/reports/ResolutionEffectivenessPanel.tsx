"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import type { StatusCount } from "@/lib/api/types";
import {
  Empty,
  SectionHeader,
  Skeleton,
  StatCard,
} from "@/shared/ui";
import { resolutionBuckets } from "./reportSummaryStats";

export function ResolutionEffectivenessPanel({
  rows,
  loading,
  onRefresh,
}: {
  rows: StatusCount[] | null;
  loading: boolean;
  onRefresh?: () => void;
}) {
  const t = useTranslations("reports");
  const buckets = useMemo(() => resolutionBuckets(rows), [rows]);

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
          primaryAction={
            onRefresh
              ? { label: t("refreshReport"), onClick: onRefresh }
              : undefined
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-2 xl:grid-cols-3">
          <StatCard
            hierarchy="secondary"
            accent="healthy"
            title={t("resolved")}
            value={<span className="tabular-nums">{buckets.resolved}</span>}
            status={t("healthy")}
            statusTone="success"
            subtitle={t("resolvedStory")}
          />
          <StatCard
            hierarchy="secondary"
            accent="attention"
            title={t("waiting")}
            value={<span className="tabular-nums">{buckets.waiting}</span>}
            status={t("attention")}
            statusTone="warning"
            subtitle={t("waitingStory")}
          />
          <StatCard
            hierarchy="secondary"
            accent="critical"
            title={t("escalated")}
            value={<span className="tabular-nums">{buckets.escalated}</span>}
            status={
              buckets.escalated > 0 ? t("attention") : t("healthy")
            }
            statusTone={buckets.escalated > 0 ? "warning" : "success"}
            subtitle={t("escalatedStory")}
          />
        </div>
      )}
    </section>
  );
}
