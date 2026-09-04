import { fetchDashboardAggregateKpis, fetchReportByUser, fetchReportCycleTime } from "@/lib/api";
import type { ReportPeriodRange } from "./reportPeriods";
import type {
  CycleTimeSummary,
  ReportSummary,
  StatusCount,
  UserActivityCount,
} from "@/lib/api/types";
import { buildAggregateKpis } from "@/features/dashboard/loadDashboardData";

export type ReportsData = {
  summary: ReportSummary | null;
  byStatus: StatusCount[] | null;
  cycleTime: CycleTimeSummary | null;
  byUser: UserActivityCount[] | null;
  previous: {
    summary: ReportSummary | null;
    byStatus: StatusCount[] | null;
    cycleTime: CycleTimeSummary | null;
  } | null;
};

async function loadWindow(
  range: ReportPeriodRange,
  branchId?: string,
): Promise<Omit<ReportsData, "previous">> {
  const query = branchId ? { ...range, branchId } : range;
  const [res, cycleRes, userRes] = await Promise.all([
    fetchDashboardAggregateKpis(query),
    fetchReportCycleTime(query).catch(() => null),
    fetchReportByUser(query).catch(() => null),
  ]);
  const kpis = buildAggregateKpis({
    total: res.data.total,
    open: res.data.open,
    closed: res.data.closed,
    escalatePending: res.data.escalatePending,
    waitingAssignment: res.data.waitingAssignment,
    escalateApproved: res.data.escalateApproved,
    escalateScheduled: res.data.escalateScheduled,
    inProgress: res.data.inProgress,
  });
  const summary: ReportSummary = {
    total: kpis.total,
    byStatus: kpis.byStatus,
  };
  return {
    summary,
    byStatus: kpis.byStatus,
    cycleTime: cycleRes?.data ?? null,
    byUser: userRes?.data ?? null,
  };
}

/**
 * Operational reports use the same Aggregate KPI as the dashboard (DEC-026).
 *
 * Per-unit breakdown lives on the dashboard (Kesehatan Cabang), which reads
 * API-212 with the richer case-completion fields. Reports no longer duplicate
 * it with a volume-only ranking.
 *
 * Cycle time and per-user activity are side panels: a failure there degrades
 * to "no data" instead of taking the whole page down with it. Previous-period
 * comparison is optional — a failure there degrades to "no comparison", not a
 * failed page.
 */
export async function loadReportsData(
  range: ReportPeriodRange = {},
  branchId?: string,
  previousRange?: ReportPeriodRange | null,
): Promise<ReportsData> {
  const current = await loadWindow(range, branchId);
  if (!previousRange) {
    return { ...current, previous: null };
  }
  try {
    const previous = await loadWindow(previousRange, branchId);
    return { ...current, previous };
  } catch {
    return { ...current, previous: null };
  }
}
