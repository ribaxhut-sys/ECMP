/**
 * ECMP layout tokens.
 * Prefer these for page chrome rhythm. Do not hardcode gutters/max-widths.
 * Pages are not migrated in Phase 0 — tokens are ready for Phase 1+.
 */

export const layout = {
  pageGutter: "var(--ecmp-page-gutter)",
  sectionGap: "var(--ecmp-section-gap)",
  panelGap: "var(--ecmp-panel-gap)",
  cardGap: "var(--ecmp-card-gap)",
  dashboardGap: "var(--ecmp-dashboard-gap)",
  formGap: "var(--ecmp-form-gap)",
  contentMaxWidth: "var(--ecmp-content-max-width)",
  formMaxWidth: "var(--ecmp-form-max-width)",
  sidebarWidth: "var(--ecmp-sidebar-width)",
  headerHeight: "var(--ecmp-header-height)",
  touchMin: "var(--ecmp-touch-min)",
} as const;

export type LayoutToken = keyof typeof layout;
