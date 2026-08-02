/**
 * ECMP spacing scale (px).
 * Map to Tailwind: 4→1, 8→2, 12→3, 16→4, 24→6, 32→8, 40→10, 48→12, 64→16.
 *
 * Usage rules:
 * - Prefer this scale for padding, margin, and gap.
 * - Prefer layout tokens (`layout.ts`) for page/section rhythm.
 * - Do not invent one-off spacing (e.g. 18px, 22px).
 */

export const spacing = {
  4: "var(--ecmp-space-4)",
  8: "var(--ecmp-space-8)",
  12: "var(--ecmp-space-12)",
  16: "var(--ecmp-space-16)",
  24: "var(--ecmp-space-24)",
  32: "var(--ecmp-space-32)",
  40: "var(--ecmp-space-40)",
  48: "var(--ecmp-space-48)",
  64: "var(--ecmp-space-64)",
} as const;

/** Tailwind class helpers for the approved spacing scale. */
export const spacingClass = {
  4: "1",
  8: "2",
  12: "3",
  16: "4",
  24: "6",
  32: "8",
  40: "10",
  48: "12",
  64: "16",
} as const;

export type SpacingToken = keyof typeof spacing;
