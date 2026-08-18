import { fetchDashboardAggregateKpis, fetchDashboardTrends } from "@/lib/api";
import type {
  DashboardHeader,
  DashboardSlaSummary,
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
};

export type DashboardData = {
  header: DashboardHeader | null;
  /** Always null (BQ-005 / CAP-006 deferred). */
  sla: DashboardSlaSummary | null;
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
  // Mutually exclusive slices. Open-and-not-escalated is "Terbuka", not "Baru".
  // PENDING is the HQ_SCHEDULED slice (still ESCALATION_ACTIVE), not "waiting".
  const byStatus: StatusCount[] = [
    {
      status: "NEW",
      count: waitingAssignment,
      labelKey: "openUnescalated",
    },
    {
      status: "ESCALATED",
      count: input.escalatePending,
      labelKey: "waitingEscalationApproval",
    },
    {
      status: "ASSIGNED",
      count: escalateApproved,
      labelKey: "escalationApproved",
    },
    {
      status: "PENDING",
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
  });
}

/**
 * Dashboard payload (DEC-026): CM Aggregate is the only complaint SoT.
 * SLA clocks stay null (BQ-005 / CAP-006 deferred).
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
    sla: null,
    byStatus: aggregate.value.byStatus,
    trend: trends.status === "fulfilled" ? trends.value.data.items : null,
  };
}
