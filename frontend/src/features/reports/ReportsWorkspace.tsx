"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  branchOptionLabel,
  sortBranchesHeadOfficeFirst,
} from "@/features/dashboard/dashboardUtils";
import { fetchBranches, type Branch } from "@/lib/api";
import { formatDateTime24 } from "@/shared/utils/datetime";
import {
  Badge,
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
import { PrintReportDialog } from "./PrintReportDialog";
import {
  buildReportCsv,
  downloadCsv,
  reportCsvFilename,
} from "./reportCsv";
import { ReportBriefing } from "./ReportBriefing";
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
import { canPickReportUnit } from "./reportUnitScope";
import { UserActivityPanel } from "./UserActivityPanel";
import { useReportsData } from "./useReportsData";

export function ReportsWorkspace() {
  const router = useRouter();
  const { user, hasPermission } = useAuth();
  const t = useTranslations("reports");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const canRead = hasPermission("reports:read") || hasPermission("*");
  const { state, reload, period, setPeriod } = useReportsData();
  const loading = state.status === "loading" || state.status === "idle";
  const data = state.status === "success" ? state.data : null;
  const [printOpen, setPrintOpen] = useState(false);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [branchesReady, setBranchesReady] = useState(!user?.branchId);
  const [unitId, setUnitId] = useState("");

  useEffect(() => {
    if (!canRead) return;
    if (!user?.branchId) setBranchesReady(true);
    let cancelled = false;
    fetchBranches(100)
      .then((res) => {
        if (!cancelled) setBranches(res.data);
      })
      .catch(() => {
        if (!cancelled) setBranches([]);
      })
      .finally(() => {
        if (!cancelled) setBranchesReady(true);
      });
    return () => {
      cancelled = true;
    };
  }, [canRead, user?.branchId]);

  const homeCode = branches.find((branch) => branch.id === user?.branchId)?.code;
  const canPickUnit = canPickReportUnit(user?.branchId, homeCode);
  const queryBranchId = canPickUnit
    ? unitId || undefined
    : user?.branchId || undefined;

  useEffect(() => {
    if (!canRead) return;
    if (user?.branchId && !branchesReady) return;
    void reload(period, queryBranchId);
  }, [canRead, reload, period, queryBranchId, user?.branchId, branchesReady]);

  const unitOptions = useMemo(
    () => [
      { value: "", label: t("unitAll") },
      ...sortBranchesHeadOfficeFirst(branches).map((branch) => ({
        value: branch.id,
        label: branchOptionLabel(branch),
      })),
    ],
    [branches, t],
  );

  const selectedUnitLabel = useMemo(() => {
    if (canPickUnit) {
      return unitOptions.find((option) => option.value === unitId)?.label
        ?? t("unitAll");
    }
    const home = branches.find((branch) => branch.id === user?.branchId);
    return home ? branchOptionLabel(home) : t("unitLabel");
  }, [branches, canPickUnit, t, unitId, unitOptions, user?.branchId]);

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
    if (data.byUser && data.byUser.length > 0) {
      rows.push(
        [],
        [
          t("userActivityUser"),
          t("userActivityUnit"),
          t("userActivityCreated"),
          t("userActivityDecided"),
          t("userActivityClosed"),
          t("userActivityEvents"),
          t("userActivityLast"),
        ],
      );
      for (const row of data.byUser) {
        rows.push([
          row.displayName,
          row.branchName ?? "",
          row.createdCount,
          row.decidedCount,
          row.closedCount,
          row.activityCount,
          row.lastActivityAt
            ? formatDateTime24(row.lastActivityAt, locale)
            : "",
        ]);
      }
    }
    downloadCsv(reportCsvFilename(period), buildReportCsv(rows));
  };

  const headerActions = (
    <div className="flex flex-wrap items-center gap-2">
      {canPickUnit ? (
        <div className="w-[14rem]">
          <Select
            name="reportUnit"
            aria-label={t("unitLabel")}
            value={unitId}
            disabled={loading}
            onChange={(e) => setUnitId(e.target.value)}
            options={unitOptions}
          />
        </div>
      ) : null}
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
        onClick={() => setPrintOpen(true)}
        disabled={loading}
        className="min-h-[var(--ecmp-touch-min)]"
      >
        {t("printReport")}
      </Button>
      <Button
        variant="outline"
        onClick={() => void reload(period, queryBranchId)}
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
        description={t("description")}
        meta={
          <>
            <Badge variant="outline" tone="primary">
              {t(REPORT_PERIOD_LABEL_KEY[period])}
            </Badge>
            <Badge variant="outline">{selectedUnitLabel}</Badge>
            {!loading && data ? (
              <Badge variant="outline">
                {t("asOf")}{" "}
                {formatDateTime24(new Date().toISOString(), locale)}
              </Badge>
            ) : null}
          </>
        }
        actions={headerActions}
      />

      {state.status === "error" ? (
        <ErrorState
          title={t("unableToLoad")}
          message={state.error}
          actionLabel={t("refreshReport")}
          onRetry={() => void reload(period, queryBranchId)}
        />
      ) : (
        <div className="flex flex-col gap-[var(--ecmp-section-gap)]">
          <ReportBriefing data={data} loading={loading} />

          <ReportSummaryCards
            summary={data?.summary ?? null}
            previousSummary={data?.previous?.summary ?? null}
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

          <UserActivityPanel
            rows={data?.byUser ?? null}
            loading={loading}
          />

          <div className="grid grid-cols-1 gap-[var(--ecmp-section-gap)] xl:grid-cols-5">
            <div className="xl:col-span-3">
              <OperationalHealthPanel
                summary={data?.summary ?? null}
                loading={loading}
              />
            </div>
            <div className="xl:col-span-2">
              <InsightsPanel
                byStatus={data?.byStatus ?? data?.summary?.byStatus ?? null}
                loading={loading}
              />
            </div>
          </div>
        </div>
      )}

      <PrintReportDialog
        open={printOpen}
        onClose={() => setPrintOpen(false)}
        period={period}
        branchId={queryBranchId}
      />
    </PageContainer>
  );
}
