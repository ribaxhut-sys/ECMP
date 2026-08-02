/**
 * ECMP elevation / shadow tokens.
 * Soft enterprise shadows only — no heavy drop shadows.
 *
 * Usage:
 * - surface: flat panels on page background
 * - raised: cards, table chrome
 * - floating: popovers, dropdowns
 * - overlay: modals
 * - hover: interactive elevation on hover
 * - sm/md/lg: legacy scale (kept for existing classNames)
 */

export const shadows = {
  sm: "var(--ecmp-shadow-sm)",
  md: "var(--ecmp-shadow-md)",
  lg: "var(--ecmp-shadow-lg)",
  surface: "var(--ecmp-shadow-surface)",
  raised: "var(--ecmp-shadow-raised)",
  floating: "var(--ecmp-shadow-floating)",
  overlay: "var(--ecmp-shadow-overlay)",
  hover: "var(--ecmp-shadow-hover)",
} as const;

export type ShadowToken = keyof typeof shadows;
