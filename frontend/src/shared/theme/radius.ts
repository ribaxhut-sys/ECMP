/**
 * ECMP border-radius tokens.
 */

export const radius = {
  sm: "var(--ecmp-radius-sm)",
  md: "var(--ecmp-radius-md)",
  lg: "var(--ecmp-radius-lg)",
  xl: "var(--ecmp-radius-xl)",
  full: "var(--ecmp-radius-full)",
} as const;

export type RadiusToken = keyof typeof radius;
