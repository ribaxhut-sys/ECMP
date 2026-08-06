"use client";

import { useMemo } from "react";
import { useTranslations } from "next-intl";
import type { BranchCount, StatusCount } from "@/lib/api/types";
import {
  Card,
  CardBody,
  CardHeader,
  Empty,
  PanelHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";
import {
  highestQueueBranch,
  resolutionBuckets,
} from "./reportSummaryStats";

function InsightTile({
  title,
  value,
  caption,
  emptyTitle,
  emptyDescription,
  onRefresh,
}: {
  title: string;
  value?: string | null;
  caption?: string | null;
  emptyTitle: string;
  emptyDescription: string;
  onRefresh?: () => void;
}) {
  const t = useTranslations("reports");

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
            primaryAction={
              onRefresh
                ? { label: t("refreshReport"), onClick: onRefresh }
                : undefined
            }
          />
        )}
      </CardBody>
    </Card>
  );
}

export function InsightsPanel({
  byStatus,
  byBranch,
  loading,
  onRefresh,
}: {
  byStatus: StatusCount[] | null;
  byBranch: BranchCount[] | null;
  loading: boolean;
  onRefresh?: () => void;
}) {
  const t = useTranslations("reports");

  const buckets = useMemo(() => resolutionBuckets(byStatus), [byStatus]);
  const topQueue = useMemo(() => highestQueueBranch(byBranch), [byBranch]);

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

  const queueInsight = topQueue
    ? {
        value: topQueue.branchName?.trim() || t("unknownBranch"),
        caption: t("highestQueueCaption", { count: topQueue.total }),
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
        <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] md:grid-cols-2">
          <InsightTile
            title={t("topOperationalRisk")}
            value={topRisk?.value}
            caption={topRisk?.caption}
            emptyTitle={t("insightUnavailable")}
            emptyDescription={t("topRiskUnavailable")}
            onRefresh={onRefresh}
          />
          <InsightTile
            title={t("highestQueue")}
            value={queueInsight?.value}
            caption={queueInsight?.caption}
            emptyTitle={t("insightUnavailable")}
            emptyDescription={t("highestQueueUnavailable")}
            onRefresh={onRefresh}
          />
        </div>
      )}
    </section>
  );
}
