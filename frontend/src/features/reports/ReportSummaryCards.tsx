"use client";

import { useTranslations } from "next-intl";
import type { ReportSummary } from "@/lib/api/types";
import { IconCheck, IconQueue } from "@/shared/icons";
import {
  Empty,
  SectionHeader,
  Skeleton,
  StatCard,
  type StatAccent,
} from "@/shared/ui";
import {
  reportHeadlineCounts,
  resolutionRatePercent,
} from "./reportSummaryStats";

function openAccentFromRate(openRate: number): StatAccent {
  if (openRate >= 70) return "critical";
  if (openRate >= 40) return "attention";
  return "healthy";
}

export function ReportSummaryCards({
  summary,
  loading,
}: {
  summary: ReportSummary | null;
  loading: boolean;
}) {
  const t = useTranslations("reports");

  if (loading) {
    return (
      <section
        data-testid="reports-summary-cards"
        className="space-y-[var(--ecmp-panel-gap)]"
        aria-label={t("executiveSummary")}
      >
        <SectionHeader
          title={t("executiveSummary")}
          description={t("executiveSummaryDescription")}
        />
        <Skeleton rows={3} />
      </section>
    );
  }

  const headlines = reportHeadlineCounts(summary);
  const resolutionRate = resolutionRatePercent(headlines);

  if (!headlines) {
    return (
      <section
        data-testid="reports-summary-cards"
        className="space-y-[var(--ecmp-panel-gap)]"
        aria-label={t("executiveSummary")}
      >
        <SectionHeader
          title={t("executiveSummary")}
          description={t("executiveSummaryDescription")}
        />
        <Empty
          title={t("noSummary")}
          description={t("noSummaryDescription")}
        />
      </section>
    );
  }

  const openRate =
    headlines.total > 0
      ? Math.round((headlines.open / headlines.total) * 100)
      : 0;
  const openAccent = openAccentFromRate(openRate);
  const resolutionAccent: StatAccent =
    resolutionRate == null
      ? "normal"
      : resolutionRate >= 60
        ? "healthy"
        : resolutionRate >= 30
          ? "attention"
          : "critical";

  return (
    <section
      data-testid="reports-summary-cards"
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={t("executiveSummary")}
    >
      <SectionHeader
        title={t("executiveSummary")}
        description={t("executiveSummaryDescription")}
      />
      <div className="grid grid-cols-1 gap-[var(--ecmp-card-gap)] md:grid-cols-2 lg:grid-cols-3">
        <StatCard
          hierarchy="primary"
          accent={openAccent}
          title={t("openComplaints")}
          value={<span className="tabular-nums">{headlines.open}</span>}
          icon={<IconQueue className="size-5" aria-hidden />}
          status={
            openAccent === "critical"
              ? t("critical")
              : openAccent === "attention"
                ? t("attention")
                : t("healthy")
          }
          statusTone={
            openAccent === "critical"
              ? "danger"
              : openAccent === "attention"
                ? "warning"
                : "success"
          }
          subtitle={t("openStory")}
          description={`${openRate}% ${t("openRate").toLowerCase()}`}
        />

        <StatCard
          hierarchy="secondary"
          accent="normal"
          title={t("totalComplaints")}
          value={<span className="tabular-nums">{headlines.total}</span>}
          subtitle={t("volumeStory")}
          description={t("closedOfTotal", {
            closed: headlines.closed,
            total: headlines.total,
          })}
        />

        <StatCard
          hierarchy="secondary"
          accent={resolutionAccent}
          title={t("resolutionRate")}
          value={
            <span className="tabular-nums">
              {resolutionRate == null ? "—" : `${resolutionRate}%`}
            </span>
          }
          icon={<IconCheck className="size-5" aria-hidden />}
          status={
            resolutionAccent === "critical"
              ? t("critical")
              : resolutionAccent === "attention"
                ? t("attention")
                : t("healthy")
          }
          statusTone={
            resolutionAccent === "critical"
              ? "danger"
              : resolutionAccent === "attention"
                ? "warning"
                : "success"
          }
          subtitle={t("resolutionRateStory")}
          description={t("closedStory")}
        />
      </div>
    </section>
  );
}
