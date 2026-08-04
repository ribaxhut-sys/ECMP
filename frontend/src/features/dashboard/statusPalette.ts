import type { ComplaintStatus } from "@/lib/api/types";

/**
 * Softer chart palette — primary teal stays brand-forward,
 * other statuses use muted mixes so the donut feels analytics-calm.
 */
export const STATUS_CHART_COLORS: Record<ComplaintStatus, string> = {
  NEW: "color-mix(in srgb, var(--ecmp-info) 78%, white)",
  ASSIGNED: "var(--ecmp-primary)",
  IN_PROGRESS: "color-mix(in srgb, var(--ecmp-warning) 72%, white)",
  PENDING: "color-mix(in srgb, var(--ecmp-secondary) 55%, white)",
  ESCALATED: "color-mix(in srgb, var(--ecmp-danger) 80%, white)",
  RESOLVED: "color-mix(in srgb, var(--ecmp-success) 75%, white)",
  CLOSED: "color-mix(in srgb, var(--ecmp-text-secondary) 45%, white)",
};

export const STATUS_CHART_FALLBACK =
  "color-mix(in srgb, var(--ecmp-secondary) 50%, white)";
