/**
 * ECMP focus ring tokens — one style for the entire application.
 * Applied globally via `:focus-visible` in `globals.css`.
 */

export const focus = {
  ringWidth: "var(--ecmp-focus-ring-width)",
  ringOffset: "var(--ecmp-focus-ring-offset)",
  ringColor: "var(--ecmp-focus-ring-color)",
} as const;

export type FocusToken = typeof focus;
