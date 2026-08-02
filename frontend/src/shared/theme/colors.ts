/**
 * ECMP design tokens — colors.
 * Prefer CSS variables (`var(--ecmp-color-*)`) or Tailwind theme classes.
 * Do not hardcode hex values in components.
 * CSS (`globals.css`) is the source of truth.
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
    bg: "var(--ecmp-color-success-bg)",
    border: "var(--ecmp-color-success-border)",
    text: "var(--ecmp-color-success-text)",
    subtle: "var(--ecmp-color-success-subtle)",
  },
  warning: {
    DEFAULT: "var(--ecmp-color-warning)",
    foreground: "var(--ecmp-color-warning-foreground)",
    muted: "var(--ecmp-color-warning-muted)",
    bg: "var(--ecmp-color-warning-bg)",
    border: "var(--ecmp-color-warning-border)",
    text: "var(--ecmp-color-warning-text)",
    subtle: "var(--ecmp-color-warning-subtle)",
  },
  danger: {
    DEFAULT: "var(--ecmp-color-danger)",
    foreground: "var(--ecmp-color-danger-foreground)",
    muted: "var(--ecmp-color-danger-muted)",
    bg: "var(--ecmp-color-danger-bg)",
    border: "var(--ecmp-color-danger-border)",
    text: "var(--ecmp-color-danger-text)",
    subtle: "var(--ecmp-color-danger-subtle)",
  },
  info: {
    DEFAULT: "var(--ecmp-color-info)",
    foreground: "var(--ecmp-color-info-foreground)",
    muted: "var(--ecmp-color-info-muted)",
    bg: "var(--ecmp-color-info-bg)",
    border: "var(--ecmp-color-info-border)",
    text: "var(--ecmp-color-info-text)",
    subtle: "var(--ecmp-color-info-subtle)",
  },
  surface: {
    DEFAULT: "var(--ecmp-color-surface)",
    raised: "var(--ecmp-color-surface-raised)",
    sunken: "var(--ecmp-color-surface-sunken)",
    floating: "var(--ecmp-color-surface-floating)",
    overlay: "var(--ecmp-color-surface-overlay)",
  },
  background: "var(--ecmp-color-background)",
  border: "var(--ecmp-color-border)",
  text: {
    primary: "var(--ecmp-color-text-primary)",
    secondary: "var(--ecmp-color-text-secondary)",
  },
  interaction: {
    hover: "var(--ecmp-color-hover)",
    selected: "var(--ecmp-color-selected)",
    pressed: "var(--ecmp-color-pressed)",
    disabled: "var(--ecmp-color-disabled)",
    muted: "var(--ecmp-color-muted)",
  },
  focus: "var(--ecmp-color-focus)",
  /** @deprecated Prefer `surface.overlay` — kept for existing Modal consumers */
  overlay: "var(--ecmp-color-overlay)",
} as const;

export type ColorToken = typeof colors;
