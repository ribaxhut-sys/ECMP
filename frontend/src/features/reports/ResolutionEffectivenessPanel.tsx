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
import { escalationTotal, resolutionBuckets } from "./reportSummaryStats";

export function ResolutionEffectivenessPanel({
  rows,
  loading,
}: {
  rows: StatusCount[] | null;
  loading: boolean;
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
        />
      ) : (
        <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] sm:grid-cols-2 xl:grid-cols-4">
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
              buckets.escalationApproved > 0
                ? t("escalatedStoryWithApproved", {
                    approved: buckets.escalationApproved,
                  })
                : t("escalatedStory")
            }
          />
        </div>
      )}
    </section>
  );
}
