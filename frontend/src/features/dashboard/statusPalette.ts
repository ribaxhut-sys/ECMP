import type { ComplaintStatus } from "@/lib/api/types";

/**
 * Command-center chart palette — saturated, so segments read at a glance
 * against the flat tile background instead of blending into it.
 */
export const STATUS_CHART_COLORS: Record<ComplaintStatus, string> = {
  NEW: "color-mix(in srgb, var(--ecmp-color-info) 88%, white)",
  ASSIGNED: "var(--ecmp-color-primary)",
  IN_PROGRESS: "color-mix(in srgb, var(--ecmp-color-warning) 84%, white)",
  PENDING: "color-mix(in srgb, var(--ecmp-color-secondary) 68%, white)",
  ESCALATED: "color-mix(in srgb, var(--ecmp-color-danger) 90%, white)",
  RESOLVED: "color-mix(in srgb, var(--ecmp-color-success) 86%, white)",
  CLOSED: "color-mix(in srgb, var(--ecmp-color-text-secondary) 55%, white)",
};

export const STATUS_CHART_FALLBACK =
  "color-mix(in srgb, var(--ecmp-color-secondary) 50%, white)";
