/**
 * ECMP icon system tokens.
 * Shared icons (`shared/icons`) use stroke 1.75 and default size-5 (20px).
 * Standard sizes: 16 (inline chrome), 20 (default UI), 24 (emphasis / empty).
 * Phase 0 documents only — no icon component rewrites.
 */

export const icons = {
  size: {
    16: "var(--ecmp-icon-size-16)",
    20: "var(--ecmp-icon-size-20)",
    24: "var(--ecmp-icon-size-24)",
  },
  stroke: "var(--ecmp-icon-stroke)",
  /** Tailwind size class equivalents */
  sizeClass: {
    16: "size-4",
    20: "size-5",
    24: "size-6",
  },
} as const;

export type IconToken = typeof icons;
