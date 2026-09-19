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
  type StatTrend,
} from "@/shared/ui";
import {
  countDelta,
  previousRateFromSummary,
  rateDelta,
  signedCount,
} from "./reportBriefing";
import {
  reportHeadlineCounts,
  resolutionRatePercent,
} from "./reportSummaryStats";

function openAccentFromRate(openRate: number): StatAccent {
  if (openRate >= 70) return "critical";
  if (openRate >= 40) return "attention";
  return "healthy";
}

function vsPrevious(
  label: string,
  delta: number | null,
  higherIsBetter: boolean | null,
): { trend?: StatTrend; delta?: string } {
  if (delta == null) return {};
  const trend: StatTrend =
    higherIsBetter == null || delta === 0
      ? "neutral"
      : (delta > 0) === higherIsBetter
        ? "up"
        : "down";
  return { trend, delta: label };
}

export function ReportSummaryCards({
  summary,
  previousSummary,
  loading,
}: {
  summary: ReportSummary | null;
  previousSummary?: ReportSummary | null;
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

  const previousHeadlines = reportHeadlineCounts(previousSummary);
  const openDelta = countDelta(headlines.open, previousHeadlines?.open);
  const totalDelta = countDelta(headlines.total, previousHeadlines?.total);
  const rateChange = rateDelta(
    resolutionRate,
    previousRateFromSummary(previousSummary),
  );
  const openVs = vsPrevious(
    t("vsPreviousDelta", { delta: signedCount(openDelta ?? 0) }),
    openDelta,
    false,
  );
  const totalVs = vsPrevious(
    t("vsPreviousDelta", { delta: signedCount(totalDelta ?? 0) }),
    totalDelta,
    null,
  );
  const rateVs = vsPrevious(
    t("vsPreviousRateDelta", { delta: signedCount(rateChange ?? 0) }),
    rateChange,
    true,
  );

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
          {...openVs}
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
          {...totalVs}
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
          {...rateVs}
        />
      </div>
    </section>
  );
}
