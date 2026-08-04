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

export type InsightKind =
  | "slaBreached"
  | "escalationReview"
  | "backlog"
  | "normal";

export type SystemHealthKind = "healthy" | "attention" | "syncing" | "degraded";

export type OpsTone = "healthy" | "attention" | "critical" | "neutral";

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

export function actorInitials(actor: string | null | undefined): string {
  const value = (actor ?? "").trim();
  if (!value) return "?";
  const parts = value.split(/\s+/).filter(Boolean);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
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

/** Rule-based operational insights — presentation only, no AI. */
export function buildTodaysInsights(input: {
  header: DashboardHeader | null;
  sla: DashboardSlaSummary | null;
  byStatus: StatusCount[] | null;
}): InsightKind[] {
  const insights: InsightKind[] = [];
  const breached = input.sla?.overall.breached ?? 0;
  const escalated = countByStatus(input.byStatus, "ESCALATED") ?? 0;
  const open = input.header?.openComplaints ?? 0;
  const closed = input.header?.closedComplaints ?? 0;

  if (breached > 0) insights.push("slaBreached");
  if (escalated > 5) insights.push("escalationReview");
  if (input.header && open > closed) insights.push("backlog");

  if (insights.length === 0) return ["normal"];
  return insights;
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

export function secondsSince(from: Date | null, nowMs: number = Date.now()): number | null {
  if (!from) return null;
  return Math.max(0, Math.floor((nowMs - from.getTime()) / 1000));
}

export function resolveSystemHealth(input: {
  loading: boolean;
  error: boolean;
  sla: DashboardSlaSummary | null;
}): SystemHealthKind {
  if (input.loading) return "syncing";
  if (input.error) return "degraded";
  const breached = input.sla?.overall.breached ?? 0;
  if (breached > 0) return "attention";
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

/** Flat strip — no card chrome (status / briefing). */
export const DASHBOARD_STRIP =
  "border-b border-ecmp-border/40 bg-transparent";

/** Main visual anchor surface (Queue Health only). */
export const DASHBOARD_SURFACE_MAIN =
  "rounded-[var(--ecmp-radius-lg)] border border-ecmp-border/50 bg-ecmp-surface shadow-[0_1px_2px_rgb(0_0_0_/0.04)]";

/** Quiet secondary panel — whitespace over chrome. */
export const DASHBOARD_SURFACE_QUIET =
  "rounded-[var(--ecmp-radius-md)] bg-ecmp-surface-sunken/35";

/** @deprecated Prefer MAIN / QUIET / STRIP — kept for residual imports. */
export const DASHBOARD_SURFACE = DASHBOARD_SURFACE_MAIN;
export const DASHBOARD_SURFACE_FLAT = DASHBOARD_SURFACE_QUIET;

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
export const DASHBOARD_METRIC =
  "text-[26px] font-medium leading-none tracking-tight tabular-nums text-ecmp-text-primary md:text-[28px]";
export const DASHBOARD_METRIC_LG =
  "text-[32px] font-medium leading-none tracking-tight tabular-nums text-ecmp-text-primary md:text-[36px]";
export const DASHBOARD_BODY =
  "text-[13px] leading-snug text-ecmp-text-secondary";
export const DASHBOARD_CAPTION =
  "text-[12px] leading-snug text-ecmp-text-secondary";

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
