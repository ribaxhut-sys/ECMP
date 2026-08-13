import { CM_BATCH1_OPEN_HREF } from "@/features/complaints/cmBatch1ListFilters";
import type {
  ComplaintStatus,
  DashboardHeader,
  DashboardSlaStage,
  DashboardSlaSummary,
  StatusCount,
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
  labelKey: QueueHealthLabelKey;
  count: number;
  tone: OpsTone;
  href: string | null;
};

export type DashboardEmptyWorkCta = {
  href: string;
  labelKey: "goToComplaints" | "goToQueue";
};

/** Empty dashboard work door is always CM list (DEC-026). */
export function dashboardEmptyWorkCta(): DashboardEmptyWorkCta {
  return { href: CM_BATCH1_OPEN_HREF, labelKey: "goToComplaints" };
}

/**
 * Queue-health bars for CM Aggregate: waiting-assignment + escalate-pending.
 */
export function buildQueueHealthRows(input: {
  byStatus: StatusCount[] | null;
  waitingAssignmentHref: string | null;
  escalationHref: string | null;
}): QueueHealthRowSpec[] {
  const waitingAssignment = countByStatus(input.byStatus, "NEW") ?? 0;
  const escalated = countByStatus(input.byStatus, "ESCALATED") ?? 0;
  return [
    {
      id: "waiting-assignment",
      labelKey: "waitingAssignment",
      count: waitingAssignment,
      tone: waitingAssignment > 0 ? "attention" : "healthy",
      href: input.waitingAssignmentHref,
    },
    {
      id: "waiting-escalation",
      labelKey: "waitingEscalationApproval",
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
      href: "/complaints/cm/cases",
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
  status: ComplaintStatus,
): number | null {
  if (!rows) return null;
  const match = rows.find((row) => row.status === status);
  return match?.count ?? 0;
}

export function slaCompletionRatio(stage: DashboardSlaStage): number {
  const total = stage.completed + stage.breached;
  if (total <= 0) return 1;
  return stage.completed / total;
}

export function slaHealthLevel(stage: DashboardSlaStage): SlaHealthLevel {
  if (stage.breached <= 0) {
    return stage.completed > 0 ? "excellent" : "healthy";
  }
  const ratio = slaCompletionRatio(stage);
  if (ratio >= 0.85) return "healthy";
  if (ratio >= 0.65) return "warning";
  return "critical";
}

export function slaLevelToOpsTone(level: SlaHealthLevel): OpsTone {
  if (level === "critical") return "critical";
  if (level === "warning") return "attention";
  return "healthy";
}

/** Three-letter avatar code for activity actors (DH → DHA, Elena → ELE). */
export function actorInitials(actor: string | null | undefined): string {
  const value = (actor ?? "").trim();
  if (!value) return "?";
  const parts = value.split(/\s+/).filter(Boolean);
  if (parts.length >= 3) {
    return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}${parts[2][0] ?? ""}`.toUpperCase();
  }
  if (parts.length === 2) {
    const first = parts[0] ?? "";
    const last = parts[1] ?? "";
    if (last.length >= 2) {
      return `${first[0] ?? ""}${last.slice(0, 2)}`.toUpperCase();
    }
    return `${first.slice(0, 2)}${last[0] ?? ""}`.toUpperCase().slice(0, 3);
  }
  return (parts[0] ?? "").slice(0, 3).toUpperCase();
}

/** Relative time for activity rows — presentation only. */
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
  const diffDay = Math.round(diffSec / 86400);
  if (Math.abs(diffDay) < 30) return rtf.format(diffDay, "day");
  const diffMonth = Math.round(diffSec / 2_592_000);
  if (Math.abs(diffMonth) < 12) return rtf.format(diffMonth, "month");
  return rtf.format(Math.round(diffSec / 31_536_000), "year");
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
  sla: DashboardSlaSummary | null;
  waitingAssignment?: number;
  escalatePending?: number;
}): SystemHealthKind {
  if (input.loading) return "syncing";
  if (input.error) return "degraded";
  const breached = input.sla?.overall.breached ?? 0;
  const waiting = input.waitingAssignment ?? 0;
  const escalate = input.escalatePending ?? 0;
  if (breached > 0 || waiting > 0 || escalate > 0) return "attention";
  return "healthy";
}

export function dashboardEnvironmentLabel(): "production" | "development" {
  return process.env.NODE_ENV === "production" ? "production" : "development";
}

export function resolutionRatePct(header: DashboardHeader | null): number | null {
  if (!header || header.totalComplaints <= 0) return null;
  return Math.round((header.closedComplaints / header.totalComplaints) * 100);
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
