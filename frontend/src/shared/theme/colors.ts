/**
 * ECMP design tokens — colors.
 * Prefer CSS variables (`var(--ecmp-color-*)`) or Tailwind theme classes.
 * Do not hardcode hex values in components.
 */

export const colors = {
  primary: {
    DEFAULT: "var(--ecmp-color-primary)",
    foreground: "var(--ecmp-color-primary-foreground)",
    muted: "var(--ecmp-color-primary-muted)",
  },
  secondary: {
    DEFAULT: "var(--ecmp-color-secondary)",
    foreground: "var(--ecmp-color-secondary-foreground)",
    muted: "var(--ecmp-color-secondary-muted)",
  },
  success: {
    DEFAULT: "var(--ecmp-color-success)",
    foreground: "var(--ecmp-color-success-foreground)",
    muted: "var(--ecmp-color-success-muted)",
  },
  warning: {
    DEFAULT: "var(--ecmp-color-warning)",
    foreground: "var(--ecmp-color-warning-foreground)",
    muted: "var(--ecmp-color-warning-muted)",
  },
  danger: {
    DEFAULT: "var(--ecmp-color-danger)",
    foreground: "var(--ecmp-color-danger-foreground)",
    muted: "var(--ecmp-color-danger-muted)",
  },
  info: {
    DEFAULT: "var(--ecmp-color-info)",
    foreground: "var(--ecmp-color-info-foreground)",
    muted: "var(--ecmp-color-info-muted)",
  },
  surface: "var(--ecmp-color-surface)",
  background: "var(--ecmp-color-background)",
  border: "var(--ecmp-color-border)",
  text: {
    primary: "var(--ecmp-color-text-primary)",
    secondary: "var(--ecmp-color-text-secondary)",
  },
  focus: "var(--ecmp-color-focus)",
  overlay: "var(--ecmp-color-overlay)",
} as const;

export type ColorToken = typeof colors;
