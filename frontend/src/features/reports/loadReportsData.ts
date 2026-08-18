import { fetchDashboardAggregateKpis, fetchReportCycleTime } from "@/lib/api";
import type { ReportPeriodRange } from "./reportPeriods";
import type {
  CycleTimeSummary,
  ReportSummary,
  StatusCount,
} from "@/lib/api/types";
import { buildAggregateKpis } from "@/features/dashboard/loadDashboardData";

export type ReportsData = {
  summary: ReportSummary | null;
  byStatus: StatusCount[] | null;
  cycleTime: CycleTimeSummary | null;
};

/**
 * Operational reports use the same Aggregate KPI as the dashboard (DEC-026).
 *
 * Per-unit breakdown lives on the dashboard (Kesehatan Cabang), which reads
 * API-212 with the richer case-completion fields. Reports no longer duplicate
 * it with a volume-only ranking.
 *
 * Cycle time is a side panel: a failure there degrades to "no data" instead of
 * taking the whole page down with it.
 */
export async function loadReportsData(
  range: ReportPeriodRange = {},
): Promise<ReportsData> {
  const [res, cycleRes] = await Promise.all([
    fetchDashboardAggregateKpis(range),
    fetchReportCycleTime(range).catch(() => null),
  ]);
  const kpis = buildAggregateKpis({
    total: res.data.total,
    open: res.data.open,
    closed: res.data.closed,
    escalatePending: res.data.escalatePending,
    waitingAssignment: res.data.waitingAssignment,
    escalateApproved: res.data.escalateApproved,
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
  };
}
