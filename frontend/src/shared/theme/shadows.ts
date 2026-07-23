/**
 * ECMP elevation / shadow tokens.
 */

export const shadows = {
  sm: "var(--ecmp-shadow-sm)",
  md: "var(--ecmp-shadow-md)",
  lg: "var(--ecmp-shadow-lg)",
} as const;

export type ShadowToken = keyof typeof shadows;
