import { fetchDashboardAggregateKpis, fetchDashboardTrends } from "@/lib/api";
import type {
  DashboardHeader,
  DashboardResolutionSla,
  DashboardTrendItem,
  StatusCount,
} from "@/lib/api/types";

/**
 * Mode A operational KPI from CM Aggregate (DEC-026 Single SoT).
 * Gated by dashboard:read so MANAGER (BC-8.4) can see own-branch KPIs without
 * complaints:read / unscoped list access.
 */
export type AggregateDashboardKpis = {
  total: number;
  open: number;
  closed: number;
  escalatePending: number;
  waitingAssignment: number;
  escalateApproved: number;
  escalateScheduled: number;
  inProgress: number;
  /** Mutually exclusive operational slices — sum equals total. */
  byStatus: StatusCount[];
  header: DashboardHeader;
  /** DEC-031 rollup as returned by the API; null when not measured. */
  sla: DashboardResolutionSla | null;
};

export type DashboardData = {
  header: DashboardHeader | null;
  /**
   * DEC-031 resolution-SLA rollup, computed server-side on the same call as
   * the KPI counts. Null when measurement is switched off
   * (COMPLAINT_RESOLUTION_TARGET_DAYS=0).
   */
  sla: DashboardResolutionSla | null;
  byStatus: StatusCount[] | null;
  /** 30-day daily complaint-count trend from CM Aggregate. */
  trend: DashboardTrendItem[] | null;
};

export function buildAggregateKpis(input: {
  total: number;
  open: number;
  closed: number;
  escalatePending: number;
  waitingAssignment?: number;
  escalateApproved?: number;
  escalateScheduled?: number;
  inProgress?: number;
  sla?: DashboardResolutionSla | null;
}): AggregateDashboardKpis {
  const escalateApproved = input.escalateApproved ?? 0;
  const escalateScheduled = input.escalateScheduled ?? 0;
  const inProgress = input.inProgress ?? 0;
  const waitingAssignment =
    input.waitingAssignment ??
    Math.max(
      0,
      input.open -
        input.escalatePending -
        escalateApproved -
        escalateScheduled -
        inProgress,
    );
  // Mutually exclusive slices. Keys are Aggregate statuses or operational
  // slice ids — never Foundation NEW / ASSIGNED / PENDING / ESCALATED.
  const byStatus: StatusCount[] = [
    {
      status: "waitingAssignment",
      count: waitingAssignment,
      labelKey: "openUnescalated",
    },
    {
      status: "escalatePending",
      count: input.escalatePending,
      labelKey: "waitingEscalationApproval",
    },
    {
      status: "escalateApproved",
      count: escalateApproved,
      labelKey: "escalationApproved",
    },
    {
      status: "escalateScheduled",
      count: escalateScheduled,
      labelKey: "escalationScheduled",
    },
    {
      status: "IN_PROGRESS",
      count: inProgress,
      labelKey: "queueInProgress",
    },
    {
      status: "CLOSED",
      count: input.closed,
      labelKey: "closedComplaints",
    },
  ];
  return {
    total: input.total,
    open: input.open,
    closed: input.closed,
    escalatePending: input.escalatePending,
    waitingAssignment,
    escalateApproved,
    escalateScheduled,
    inProgress,
    byStatus,
    header: {
      totalComplaints: input.total,
      openComplaints: input.open,
      closedComplaints: input.closed,
    },
    sla: input.sla ?? null,
  };
}

async function loadAggregateKpis(): Promise<AggregateDashboardKpis> {
  const res = await fetchDashboardAggregateKpis();
  const data = res.data;
  return buildAggregateKpis({
    total: data.total,
    open: data.open,
    closed: data.closed,
    escalatePending: data.escalatePending,
    waitingAssignment: data.waitingAssignment,
    escalateApproved: data.escalateApproved,
    escalateScheduled: data.escalateScheduled,
    inProgress: data.inProgress,
    sla: data.sla ?? null,
  });
}

/**
 * Dashboard payload (DEC-026): CM Aggregate is the only complaint SoT.
 * The SLA rollup rides on the aggregate-KPI response (DEC-031) — no extra
 * round trip, and no scheduler behind it.
 */
export async function loadDashboardData(): Promise<DashboardData> {
  const [aggregate, trends] = await Promise.allSettled([
    loadAggregateKpis(),
    fetchDashboardTrends("30d"),
  ]);

  if (aggregate.status === "rejected") {
    throw aggregate.reason;
  }

  return {
    header: aggregate.value.header,
    sla: aggregate.value.sla,
    byStatus: aggregate.value.byStatus,
    trend: trends.status === "fulfilled" ? trends.value.data.items : null,
  };
}
