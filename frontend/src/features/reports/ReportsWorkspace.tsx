"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { formatDateTime24 } from "@/shared/utils/datetime";
import {
  Button,
  Empty,
  ErrorState,
  PageContainer,
  PageHeader,
  Select,
} from "@/shared/ui";
import { cycleTimeBucketRows } from "./cycleTimeStats";
import { CycleTimePanel } from "./CycleTimePanel";
import { InsightsPanel } from "./InsightsPanel";
import { OperationalHealthPanel } from "./OperationalHealthPanel";
import {
  buildReportCsv,
  downloadCsv,
  reportCsvFilename,
} from "./reportCsv";
import { ReportSummaryCards } from "./ReportSummaryCards";
import { ResolutionEffectivenessPanel } from "./ResolutionEffectivenessPanel";
import {
  REPORT_PERIOD_KEYS,
  REPORT_PERIOD_LABEL_KEY,
  type ReportPeriodKey,
} from "./reportPeriods";
import {
  escalationTotal,
  reportHeadlineCounts,
  resolutionBuckets,
  resolutionRatePercent,
} from "./reportSummaryStats";
import { useReportsData } from "./useReportsData";

export function ReportsWorkspace() {
  const router = useRouter();
  const { hasPermission } = useAuth();
  const t = useTranslations("reports");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const canRead = hasPermission("reports:read") || hasPermission("*");
  const { state, reload, period, setPeriod } = useReportsData();
  const loading = state.status === "loading" || state.status === "idle";
  const data = state.status === "success" ? state.data : null;

  useEffect(() => {
    if (!canRead) return;
    void reload(period);
  }, [canRead, reload, period]);

  const exportCsv = () => {
    if (!data) return;
    const headlines = reportHeadlineCounts(data.summary);
    const buckets = resolutionBuckets(data.byStatus);
    const rate = resolutionRatePercent(headlines);
    const rows: (string | number)[][] = [
      [t("title"), t(REPORT_PERIOD_LABEL_KEY[period])],
      // Operator-facing stamp: WIB like every other date on the page,
      // never the raw UTC instant.
      [t("csvGeneratedAt"), formatDateTime24(new Date().toISOString(), locale)],
      [],
      [t("csvMetric"), t("csvCount")],
      [t("totalComplaints"), headlines?.total ?? 0],
      [t("openComplaints"), headlines?.open ?? 0],
      [t("closedComplaints"), headlines?.closed ?? 0],
      [t("resolutionRate"), rate == null ? "" : `${rate}%`],
    ];
    if (data.cycleTime && data.cycleTime.closedCases > 0) {
      const cycle = data.cycleTime;
      rows.push(
        [],
        [t("cycleTime"), t("csvCount")],
        [t("cycleTimeClosedCases"), cycle.closedCases],
        [t("cycleTimeMedian"), cycle.medianDays ?? ""],
        [t("cycleTimeAverage"), cycle.averageDays ?? ""],
        [t("cycleTimeP90"), cycle.p90Days ?? ""],
      );
      for (const row of cycleTimeBucketRows(cycle)) {
        rows.push([t(row.labelKey), row.count]);
      }
    }
    if (buckets) {
      rows.push(
        [],
        [t("resolutionEffectiveness"), t("csvCount")],
        [t("resolved"), buckets.resolved],
        [t("inProgress"), buckets.inProgress],
        [t("waiting"), buckets.waiting],
        [t("escalated"), escalationTotal(buckets)],
        [t("escalationApproved"), buckets.escalationApproved],
        [t("escalationScheduled"), buckets.escalationScheduled],
      );
    }
    downloadCsv(reportCsvFilename(period), buildReportCsv(rows));
  };

  const headerActions = (
    <div className="flex flex-wrap items-center gap-2">
      <div className="w-[12rem]">
        <Select
          name="reportPeriod"
          aria-label={t("periodLabel")}
          value={period}
          disabled={loading}
          onChange={(e) => setPeriod(e.target.value as ReportPeriodKey)}
          options={REPORT_PERIOD_KEYS.map((key) => ({
            value: key,
            label: t(REPORT_PERIOD_LABEL_KEY[key]),
          }))}
        />
      </div>
      <Button
        variant="outline"
        onClick={exportCsv}
        disabled={loading || !data}
        className="min-h-[var(--ecmp-touch-min)]"
      >
        {t("exportCsv")}
      </Button>
      <Button
        variant="outline"
        onClick={() => void reload(period)}
        disabled={loading}
        className="min-h-[var(--ecmp-touch-min)]"
      >
        {loading ? tCommon("refreshing") : t("refreshReport")}
      </Button>
    </div>
  );

  if (!canRead) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <PageHeader
          overline={t("overline")}
          title={t("title")}
          breadcrumbs={[
            { label: tCommon("home"), href: "/dashboard" },
            { label: t("title") },
          ]}
          description={t("description")}
        />
        <Empty
          title={t("accessRestricted")}
          description={t("accessRestrictedDescription")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
        title={t("title")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title") },
        ]}
        actions={headerActions}
      />

      {state.status === "error" ? (
        <ErrorState
          title={t("unableToLoad")}
          message={state.error}
          actionLabel={t("refreshReport")}
          onRetry={() => void reload(period)}
        />
      ) : (
        <div className="flex flex-col gap-[var(--ecmp-section-gap)]">
          <ReportSummaryCards
            summary={data?.summary ?? null}
            loading={loading}
          />

          <ResolutionEffectivenessPanel
            rows={data?.byStatus ?? data?.summary?.byStatus ?? null}
            loading={loading}
          />

          <CycleTimePanel
            summary={data?.cycleTime ?? null}
            loading={loading}
          />

          <OperationalHealthPanel
            summary={data?.summary ?? null}
            loading={loading}
          />

          <InsightsPanel
            byStatus={data?.byStatus ?? data?.summary?.byStatus ?? null}
            loading={loading}
          />
        </div>
      )}
    </PageContainer>
  );
}
