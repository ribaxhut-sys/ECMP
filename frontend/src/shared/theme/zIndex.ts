/**
 * ECMP z-index scale.
 * No magic numbers in components — consume these tokens.
 */

export const zIndex = {
  stickyHeader: "var(--ecmp-z-sticky-header)",
  dropdown: "var(--ecmp-z-dropdown)",
  sidebar: "var(--ecmp-z-sidebar)",
  overlay: "var(--ecmp-z-overlay)",
  modal: "var(--ecmp-z-modal)",
  toast: "var(--ecmp-z-toast)",
  loading: "var(--ecmp-z-loading)",
} as const;

export type ZIndexToken = keyof typeof zIndex;
