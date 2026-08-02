/**
 * ECMP border-radius tokens.
 * Scale: sm 4 · md 8 · lg 12 · xl 16 · full.
 * Component roles map to the scale — consume roles in Phase 1+.
 */

export const radius = {
  sm: "var(--ecmp-radius-sm)",
  md: "var(--ecmp-radius-md)",
  lg: "var(--ecmp-radius-lg)",
  xl: "var(--ecmp-radius-xl)",
  full: "var(--ecmp-radius-full)",
  button: "var(--ecmp-radius-button)",
  input: "var(--ecmp-radius-input)",
  select: "var(--ecmp-radius-select)",
  textarea: "var(--ecmp-radius-textarea)",
  badge: "var(--ecmp-radius-badge)",
  card: "var(--ecmp-radius-card)",
  table: "var(--ecmp-radius-table)",
  modal: "var(--ecmp-radius-modal)",
  dialog: "var(--ecmp-radius-dialog)",
  dropdown: "var(--ecmp-radius-dropdown)",
  surface: "var(--ecmp-radius-surface)",
} as const;

export type RadiusToken = keyof typeof radius;
