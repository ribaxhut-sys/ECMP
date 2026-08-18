"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import type { StatusCount } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  Empty,
  PanelHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import { resolutionBuckets } from "./reportSummaryStats";

function InsightTile({
  title,
  value,
  caption,
  emptyTitle,
  emptyDescription,
}: {
  title: string;
  value?: string | null;
  caption?: string | null;
  emptyTitle: string;
  emptyDescription: string;
}) {
  return (
    <Card className="h-full">
      <CardHeader>
        <PanelHeader title={title} className="mb-0 border-0 pb-0" />
      </CardHeader>
      <CardBody>
        {value ? (
          <div className="space-y-1">
            <p className="text-[length:var(--ecmp-font-section-title-size)] font-[number:var(--ecmp-font-section-title-weight)] text-ecmp-text-primary">
              {value}
            </p>
            {caption ? (
              <p className="text-[length:var(--ecmp-font-helper-size)] text-ecmp-text-secondary">
                {caption}
              </p>
            ) : null}
          </div>
        ) : (
          <Empty
            className="border-0 bg-transparent px-2 py-6"
            title={emptyTitle}
            description={emptyDescription}
          />
        )}
      </CardBody>
    </Card>
  );
}

export function InsightsPanel({
  byStatus,
  loading,
}: {
  byStatus: StatusCount[] | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");

  const buckets = useMemo(() => resolutionBuckets(byStatus), [byStatus]);

  const topRisk =
    buckets && buckets.escalated > 0
      ? {
          value: t("topRiskEscalated", { count: buckets.escalated }),
          caption: t("topRiskEscalatedCaption"),
        }
      : buckets && buckets.waiting > 0
        ? {
            value: t("topRiskWaiting", { count: buckets.waiting }),
            caption: t("topRiskWaitingCaption"),
          }
        : null;

  return (
    <section
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("insights")}
    >
      <SectionHeader
        title={t("insights")}
        description={t("insightsDescription")}
      />
      {loading ? (
        <Skeleton rows={3} />
      ) : (
        <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)]">
          <InsightTile
            title={t("topOperationalRisk")}
            value={topRisk?.value}
            caption={topRisk?.caption}
            emptyTitle={t("insightUnavailable")}
            emptyDescription={t("topRiskUnavailable")}
          />
        </div>
      )}
    </section>
  );
}
