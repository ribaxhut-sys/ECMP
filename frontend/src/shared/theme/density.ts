/**
 * ECMP density tokens.
 * Comfortable (default ops UI) vs Compact (dense tables).
 * No UI density switch in Phase 0 — tokens only.
 */

export const density = {
  comfortable: {
    row: "var(--ecmp-density-comfortable-row)",
    gap: "var(--ecmp-density-comfortable-gap)",
    cellY: "var(--ecmp-density-comfortable-cell-y)",
  },
  compact: {
    row: "var(--ecmp-density-compact-row)",
    gap: "var(--ecmp-density-compact-gap)",
    cellY: "var(--ecmp-density-compact-cell-y)",
  },
} as const;

export type DensityToken = typeof density;
