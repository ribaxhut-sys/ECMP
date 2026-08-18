import type { StatusCountStatus } from "@/lib/api/types";

/**
 * Command-center chart palette — saturated, so segments read at a glance
 * against the flat tile background instead of blending into it.
 */
export const STATUS_CHART_COLORS: Partial<Record<StatusCountStatus, string>> = {
  REGISTERED: "color-mix(in srgb, var(--ecmp-color-info) 88%, white)",
  waitingAssignment: "color-mix(in srgb, var(--ecmp-color-info) 88%, white)",
  escalateApproved: "var(--ecmp-color-primary)",
  IN_PROGRESS: "color-mix(in srgb, var(--ecmp-color-warning) 84%, white)",
  escalateScheduled: "color-mix(in srgb, var(--ecmp-color-secondary) 68%, white)",
  escalatePending: "color-mix(in srgb, var(--ecmp-color-danger) 90%, white)",
  CLOSED: "color-mix(in srgb, var(--ecmp-color-text-secondary) 55%, white)",
};

export const STATUS_CHART_FALLBACK =
  "color-mix(in srgb, var(--ecmp-color-secondary) 50%, white)";
