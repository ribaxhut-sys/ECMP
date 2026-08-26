import { CM_BATCH1_OPEN_HREF } from "@/features/complaints/cmBatch1ListFilters";
import { formatDateTime24 } from "@/shared/utils/datetime";
import { nameInitials } from "@/shared/utils/initials";
import type {
  BranchCount,
  DashboardHeader,
  DashboardRecentActivityItem,
  DashboardResolutionSla,
  StatusCount,
  StatusCountStatus,
} from "@/lib/api/types";

export type SlaHealthLevel =
  | "excellent"
  | "healthy"
  | "warning"
  | "critical";

export type BranchBadgeKind = "top" | "attention" | "balanced";

export type SystemHealthKind = "healthy" | "attention" | "syncing" | "degraded";

export type OpsTone = "healthy" | "attention" | "critical" | "neutral";

export type QueueHealthLabelKey =
  | "waitingAssignment"
  | "waitingReview"
  | "queueInProgress"
  | "waitingEscalationApproval";

export type QueueHealthRowSpec = {
  id: string;
  queueKey: QueueHealthLabelKey;
  count: number;
  tone: OpsTone;
  href: string | null;
};

export type DashboardEmptyWorkCta = {
  href: string;
  ctaKey: "goToComplaints" | "goToQueue";
};

/** Empty dashboard work door is always CM list (DEC-026). */
export function dashboardEmptyWorkCta(): DashboardEmptyWorkCta {
  return { href: CM_BATCH1_OPEN_HREF, ctaKey: "goToComplaints" };
}

/**
 * Queue-health bars for CM Aggregate: waiting-assignment + escalate-pending.
 */
export function buildQueueHealthRows(input: {
  byStatus: StatusCount[] | null;
  waitingAssignmentHref: string | null;
  escalationHref: string | null;
}): QueueHealthRowSpec[] {
  const waitingAssignment = countByStatus(input.byStatus, "waitingAssignment") ?? 0;
  const escalated = countByStatus(input.byStatus, "escalatePending") ?? 0;
  return [
    {
      id: "waiting-assignment",
      queueKey: "waitingAssignment",
      count: waitingAssignment,
      tone: waitingAssignment > 0 ? "attention" : "healthy",
      href: input.waitingAssignmentHref,
    },
    {
      id: "waiting-escalation",
      queueKey: "waitingEscalationApproval",
      count: escalated,
      tone: escalated > 0 ? "attention" : "healthy",
      href: input.escalationHref,
    },
  ];
}

export const CRITICAL_ALERT_VISIBLE_LIMIT = 4;

export type CriticalAlertSpec = {
  id: string;
  tone: Extract<OpsTone, "critical" | "attention">;
  titleKey:
    | "alertSlaTitle"
    | "alertAssignmentSlaTitle"
    | "alertResolutionSlaTitle"
    | "alertEscalationTitle";
  count: number;
  href: string | null;
};

export function buildCriticalAlerts(input: {
  breached: number;
  assignmentBreached: number;
  resolutionBreached: number;
  escalated: number;
  escalationHref: string | null;
}): CriticalAlertSpec[] {
  const alerts: CriticalAlertSpec[] = [];
  if (input.breached > 0) {
    alerts.push({
      id: "sla-overall",
      tone: "critical",
      titleKey: "alertSlaTitle",
      count: input.breached,
      href: CM_BATCH1_OPEN_HREF,
    });
  }
  if (input.assignmentBreached > 0) {
    alerts.push({
      id: "sla-assignment",
      tone: "critical",
      titleKey: "alertAssignmentSlaTitle",
      count: input.assignmentBreached,
      href: "/complaints",
    });
  }
  if (input.resolutionBreached > 0 && input.resolutionBreached !== input.breached) {
    alerts.push({
      id: "sla-resolution",
      tone: "attention",
      titleKey: "alertResolutionSlaTitle",
      count: input.resolutionBreached,
      href: "#sla-overview",
    });
  }
  if (input.escalated > 0) {
    alerts.push({
      id: "escalation",
      tone: "attention",
      titleKey: "alertEscalationTitle",
      count: input.escalated,
      href: input.escalationHref,
    });
  }
  return alerts.sort((a, b) => {
    if (a.tone === b.tone) return 0;
    return a.tone === "critical" ? -1 : 1;
  });
}

export function visibleAlertSlice<T>(
  alerts: readonly T[],
  expanded: boolean,
  limit: number = CRITICAL_ALERT_VISIBLE_LIMIT,
): T[] {
  if (expanded || alerts.length <= limit) return [...alerts];
  return alerts.slice(0, limit);
}

export function countByStatus(
  rows: StatusCount[] | null | undefined,
  status: StatusCountStatus,
): number | null {
  if (!rows) return null;
  const match = rows.find((row) => row.status === status);
  return match?.count ?? 0;
}

/**
 * DEC-031 compliance health. Judged only on settled complaints (met/missed);
 * `unknown` rows are excluded upstream so a data gap cannot flatter or damn
 * the figure. `null` compliance means nothing has settled yet — reported as
 * "healthy" rather than 0%, which would read as total failure.
 */
export function slaComplianceLevel(
  sla: DashboardResolutionSla | null,
): SlaHealthLevel {
  if (!sla) return "healthy";
  // Anything already past the target outranks the historical average — it is
  // a live problem, not a statistic.
  if (sla.overdue > 0) return "critical";
  if (sla.compliancePercentage === null) {
    return sla.warning > 0 ? "warning" : "healthy";
  }
  if (sla.compliancePercentage >= 95) return "excellent";
  if (sla.compliancePercentage >= 85) return "healthy";
  if (sla.compliancePercentage >= 65) return "warning";
  return "critical";
}

export function slaLevelToOpsTone(level: SlaHealthLevel): OpsTone {
  if (level === "critical") return "critical";
  if (level === "warning") return "attention";
  return "healthy";
}

/** Three-letter avatar code for activity actors (Dedi Harianto → DHA, Elena → ELE). */
export function actorInitials(actor: string | null | undefined): string {
  return nameInitials(actor) ?? "?";
}

/**
 * Relative time for same-day activity; calendar datetime after 24h.
 * id-ID RelativeTimeFormat would otherwise show "kemarin dulu" for -2 days.
 */
export function formatRelativeTime(
  value: string,
  locale: string,
  nowMs: number = Date.now(),
): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  const diffSec = Math.round((date.getTime() - nowMs) / 1000);
  const abs = Math.abs(diffSec);
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: "auto" });

  if (abs < 60) return rtf.format(diffSec, "second");
  const diffMin = Math.round(diffSec / 60);
  if (Math.abs(diffMin) < 60) return rtf.format(diffMin, "minute");
  const diffHour = Math.round(diffSec / 3600);
  if (Math.abs(diffHour) < 24) return rtf.format(diffHour, "hour");
  return formatDateTime24(value, locale, value);
}

/** Simple ranking badges for branch volume share. */
export function branchBadgeKind(
  index: number,
  sharePct: number,
  totalBranches: number,
): BranchBadgeKind {
  if (totalBranches <= 1) return "balanced";
  if (index === 0) return "top";
  if (sharePct >= 30) return "attention";
  return "balanced";
}

export function resolveSystemHealth(input: {
  loading: boolean;
  error: boolean;
  sla: DashboardResolutionSla | null;
  waitingAssignment?: number;
  escalatePending?: number;
}): SystemHealthKind {
  if (input.loading) return "syncing";
  if (input.error) return "degraded";
  // DEC-031: a complaint past its 30-day target is the strongest operational
  // signal on this bar — stronger than a queue that merely has work in it.
  const overdue = input.sla?.overdue ?? 0;
  if (overdue > 0) return "degraded";
  const approaching = input.sla?.warning ?? 0;
  const waiting = input.waitingAssignment ?? 0;
  const escalate = input.escalatePending ?? 0;
  if (approaching > 0 || waiting > 0 || escalate > 0) return "attention";
  return "healthy";
}

export function dashboardEnvironmentLabel(): "lab" | "production" | "development" {
  const surface = (process.env.NEXT_PUBLIC_ECMP_SURFACE ?? "").trim().toLowerCase();
  if (surface === "lab") return "lab";
  if (surface === "production") return "production";
  return process.env.NODE_ENV === "production" ? "production" : "development";
}

export function resolutionRatePct(header: DashboardHeader | null): number | null {
  if (!header || header.totalComplaints <= 0) return null;
  return Math.round((header.closedComplaints / header.totalComplaints) * 100);
}

/** Closed / total as a whole percent; null when there is nothing to rate. */
export function completionPercent(closed: number, total: number): number | null {
  if (total <= 0) return null;
  return Math.round((closed / total) * 100);
}

/** Higher case-completion first (visible %); then complaint volume. */
export function compareBranchHealth(
  a: Pick<BranchCount, "total" | "closed" | "caseTotal" | "caseClosed">,
  b: Pick<BranchCount, "total" | "closed" | "caseTotal" | "caseClosed">,
): number {
  const aCase = completionPercent(a.caseClosed, a.caseTotal) ?? -1;
  const bCase = completionPercent(b.caseClosed, b.caseTotal) ?? -1;
  if (bCase !== aCase) return bCase - aCase;
  return b.total - a.total;
}

export function sortBranchesByHealth(
  rows: readonly BranchCount[],
): BranchCount[] {
  return [...rows].sort(compareBranchHealth);
}

/** True proportional width 0–100 from count/max. */
export function proportionalPct(count: number, max: number): number {
  if (max <= 0 || count <= 0) return 0;
  return Math.min(100, (count / max) * 100);
}

/** Main visual anchor surface (Queue Health only). */
export const DASHBOARD_SURFACE_MAIN =
  "rounded-[var(--ecmp-radius-lg)] border border-ecmp-border/50 bg-ecmp-surface shadow-[0_1px_2px_rgb(0_0_0_/0.04)]";

/** Quiet secondary panel — whitespace over chrome. */
export const DASHBOARD_SURFACE_QUIET =
  "rounded-[var(--ecmp-radius-md)] bg-ecmp-surface-sunken/35";

export const DASHBOARD_PAD = "p-3.5";
export const DASHBOARD_SECTION_GAP = "space-y-2.5";
export const DASHBOARD_CARD_GAP = "gap-2.5";
export const DASHBOARD_SHELL =
  "relative mx-auto w-full max-w-[1440px] space-y-2.5 px-4 py-3 sm:px-5 lg:px-6";

export const DASHBOARD_TITLE =
  "text-[20px] font-medium leading-tight tracking-tight text-ecmp-text-primary";
export const DASHBOARD_SECTION_TITLE =
  "text-[13px] font-medium tracking-tight text-ecmp-text-secondary";
export const DASHBOARD_CARD_TITLE =
  "text-[12px] font-medium leading-snug text-ecmp-text-secondary";
/** Command-center micro label — mono, uppercase, wide-tracked. Zone 1/2 only. */
export const DASHBOARD_COMMAND_LABEL =
  "font-mono text-[11px] font-medium uppercase tracking-[0.08em] text-ecmp-text-secondary";
export const DASHBOARD_METRIC =
  "font-mono text-[26px] font-medium leading-none tracking-tight tabular-nums text-ecmp-text-primary md:text-[28px]";
/** Single hero figure — the one number the page wants you to see first. */
export const DASHBOARD_METRIC_HERO =
  "font-mono text-[52px] font-medium leading-none tracking-tight tabular-nums text-ecmp-text-primary md:text-[64px]";
/** Seamless tile grid — 1px hairlines via bg-color gap trick, no per-tile shadow/radius. */
export const DASHBOARD_TILE_GRID =
  "grid gap-px overflow-hidden rounded-[var(--ecmp-radius-lg)] border border-ecmp-border/60 bg-ecmp-border/60";
export const DASHBOARD_TILE = "bg-ecmp-surface";
export const DASHBOARD_BODY =
  "text-[13px] leading-snug text-ecmp-text-secondary";
export const DASHBOARD_CAPTION =
  "text-[12px] leading-snug text-ecmp-text-secondary";
/** Small uppercase label marking a lower-priority zone (context, not decision). */
export const DASHBOARD_ZONE_LABEL =
  "font-mono text-[11px] font-medium uppercase tracking-wide text-ecmp-text-secondary/70";

/** Open backlog accent — never critical from ratio alone (lab-safe). */
export function openBacklogAccent(
  open: number,
  total: number,
): "healthy" | "attention" | "normal" {
  if (total <= 0 || open <= 0) return "healthy";
  const ratio = open / total;
  if (total >= 20 && ratio >= 0.85) return "attention";
  if (total >= 10 && ratio >= 0.95) return "attention";
  return "normal";
}

export const DASHBOARD_RIPPLE =
  "relative overflow-hidden transition-[transform,opacity] duration-150 motion-safe:hover:-translate-y-px";

export const DASHBOARD_HOVER_ROW =
  "transition-colors duration-150 hover:bg-ecmp-hover/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ecmp-focus";

export const OPS_TONE_DOT: Record<OpsTone, string> = {
  healthy: "bg-ecmp-success",
  attention: "bg-ecmp-warning",
  critical: "bg-ecmp-danger",
  neutral: "bg-ecmp-text-secondary/50",
};

export const OPS_TONE_TEXT: Record<OpsTone, string> = {
  healthy: "text-ecmp-success-text",
  attention: "text-ecmp-warning-text",
  critical: "text-ecmp-danger-text",
  neutral: "text-ecmp-text-secondary",
};

export const OPS_TONE_BAR: Record<OpsTone, string> = {
  healthy: "bg-ecmp-success",
  attention: "bg-ecmp-warning",
  critical: "bg-ecmp-danger",
  neutral: "bg-ecmp-primary/70",
};

export const OPS_TONE_RAIL: Record<OpsTone, string> = {
  healthy: "bg-ecmp-success",
  attention: "bg-ecmp-warning",
  critical: "bg-ecmp-danger",
  neutral: "bg-ecmp-border",
};

/**
 * Branch picker label. Most branch codes are just the name reformatted
 * (e.g. "UPPPD-GAMBIR" / "UPPPD Gambir") — showing both repeats the same
 * text. Only prefix the code when it carries information the name doesn't
 * (e.g. "JKT-01" / "Cabang Jakarta Pusat").
 */
export function branchOptionLabel(branch: { code: string; name: string }): string {
  const normalize = (value: string) => value.replace(/[^a-z0-9]/gi, "").toUpperCase();
  return normalize(branch.code) === normalize(branch.name)
    ? branch.name
    : `${branch.code} — ${branch.name}`;
}

/**
 * Compact branch name for tight chart labels — every branch shares the
 * "UPPPD" unit prefix (e.g. "UPPPD Tanah Abang"), so it adds no information
 * there and just eats horizontal space. Drops it; leaves other names as-is.
 */
export function branchHealthShortLabel(name: string): string {
  return name.replace(/^UPPPD[\s-]+/i, "").trim() || name;
}

/** The 3 per-branch bars in fixed order (never reordered): case total, resolved at branch, escalated. */
export const BRANCH_HEALTH_BAR_KEYS = ["caseTotal", "caseClosed", "escalated"] as const;

export type BranchHealthBarKey = (typeof BRANCH_HEALTH_BAR_KEYS)[number];

/**
 * Shared scale for the branch health bars — the largest single value across
 * all 3 bars, maxed across every row, so bar length stays comparable within
 * a branch and across branches.
 */
export function branchHealthScale(rows: readonly BranchCount[]): number {
  let max = 0;
  for (const row of rows) {
    max = Math.max(max, row.caseTotal, row.caseClosed, row.escalated);
  }
  return max;
}

/**
 * UTC month window as ISO strings — dateTo is inclusive (end of the last
 * day), matching /reports/by-branch's `created_at <= dateTo` filter.
 */
export function monthDateRangeIso(
  year: number,
  month: number,
): { dateFrom: string; dateTo: string } {
  const start = new Date(Date.UTC(year, month - 1, 1, 0, 0, 0, 0));
  const end = new Date(Date.UTC(year, month, 0, 23, 59, 59, 999));
  return { dateFrom: start.toISOString(), dateTo: end.toISOString() };
}

/** Localized "January".."December" options, value = 1-12. */
export function branchHealthMonthOptions(
  locale: string,
): { value: number; label: string }[] {
  const formatter = new Intl.DateTimeFormat(locale, { month: "long" });
  return Array.from({ length: 12 }, (_, i) => {
    const label = formatter.format(new Date(Date.UTC(2000, i, 1)));
    return {
      value: i + 1,
      label: label.charAt(0).toUpperCase() + label.slice(1),
    };
  });
}

/** Most recent `span` years, newest first, ending at `currentYear`. */
export function branchHealthYearOptions(
  currentYear: number,
  span = 5,
): number[] {
  return Array.from({ length: span }, (_, i) => currentYear - i);
}

const HEAD_OFFICE_UNIT_CODE = "PUSAT";

/** Head Office (Pusat) first, then every other branch alphabetically by name. */
export function sortBranchesHeadOfficeFirst<T extends { code: string; name: string }>(
  branches: readonly T[],
): T[] {
  return [...branches].sort((a, b) => {
    const aIsHeadOffice = a.code.toUpperCase() === HEAD_OFFICE_UNIT_CODE;
    const bIsHeadOffice = b.code.toUpperCase() === HEAD_OFFICE_UNIT_CODE;
    if (aIsHeadOffice !== bIsHeadOffice) return aIsHeadOffice ? -1 : 1;
    return a.name.localeCompare(b.name, "id");
  });
}

/** One row per complaint number, from the latest event in the activity window. */
export type ComplaintActivitySummary = {
  complaintNumber: string;
  caseNumber: string | null;
  actor: string | null;
  lastEventType: string;
  lastTimestamp: string;
};

/** Higher wins when two events share the same timestamp. */
const ACTIVITY_OUTCOME_RANK: Record<string, number> = {
  "complaint.closed": 80,
  "complaint.resolved": 70,
  "complaint.escalation_requested": 60,
  "complaint.escalation_approved": 60,
  "complaint.escalation_rejected": 60,
  "complaint.escalation_cancelled": 60,
  "complaint.escalated_to_pusat": 65,
  "complaint.escalation_to_pusat_cancelled": 60,
  "complaint.escalation_returned": 60,
  "complaint.handling_continued": 40,
  "complaint.handling_taken_over": 40,
  "complaint.case_created": 20,
  "complaint.created": 10,
};

function activityOutcomeRank(eventType: string): number {
  return ACTIVITY_OUTCOME_RANK[eventType] ?? 30;
}

/** Fallback `complaint.other` is not an operator-facing work state. */
export function isUnknownDashboardActivity(eventType: string): boolean {
  return eventType === "complaint.other";
}

export function aggregateComplaintActivitySummaries(
  rows: readonly DashboardRecentActivityItem[],
): ComplaintActivitySummary[] {
  const byNumber = new Map<string, DashboardRecentActivityItem[]>();
  for (const row of rows) {
    if (isUnknownDashboardActivity(row.eventType)) continue;
    const list = byNumber.get(row.complaintNumber) ?? [];
    list.push(row);
    byNumber.set(row.complaintNumber, list);
  }

  const summaries: ComplaintActivitySummary[] = [];
  for (const [complaintNumber, events] of byNumber) {
    const latest = [...events].sort((a, b) => {
      const byTime = a.timestamp.localeCompare(b.timestamp);
      if (byTime !== 0) return byTime;
      return activityOutcomeRank(a.eventType) - activityOutcomeRank(b.eventType);
    }).at(-1);
    if (!latest) continue;
    summaries.push({
      complaintNumber,
      caseNumber: latest.caseNumber?.trim() || null,
      actor: latest.actor || null,
      lastEventType: latest.eventType,
      lastTimestamp: latest.timestamp,
    });
  }

  return summaries.sort((a, b) => {
    const byTime = b.lastTimestamp.localeCompare(a.lastTimestamp);
    if (byTime !== 0) return byTime;
    return activityOutcomeRank(b.lastEventType) - activityOutcomeRank(a.lastEventType);
  });
}

/** Case number is what officers work by day-to-day; fall back to the
 * complaint number only for pre-case events (e.g. complaint just created). */
export function activitySubjectText(
  row: Pick<DashboardRecentActivityItem, "complaintNumber"> & {
    caseNumber?: string | null;
  },
): string {
  return row.caseNumber?.trim() || row.complaintNumber;
}
