/**
 * ECMP typography tokens.
 * Body minimum: 16px. Prefer CSS variables / Tailwind token classes.
 * CSS (`globals.css`) is the source of truth.
 */

export const typography = {
  display: {
    fontSize: "var(--ecmp-font-display-size)",
    lineHeight: "var(--ecmp-font-display-line)",
    fontWeight: "var(--ecmp-font-display-weight)",
  },
  /** @deprecated Prefer `pageTitle` — kept for existing consumers */
  heading: {
    fontSize: "var(--ecmp-font-heading-size)",
    lineHeight: "var(--ecmp-font-heading-line)",
    fontWeight: "var(--ecmp-font-heading-weight)",
  },
  pageTitle: {
    fontSize: "var(--ecmp-font-page-title-size)",
    lineHeight: "var(--ecmp-font-page-title-line)",
    fontWeight: "var(--ecmp-font-page-title-weight)",
  },
  /** @deprecated Prefer `sectionTitle` — kept for existing consumers */
  title: {
    fontSize: "var(--ecmp-font-title-size)",
    lineHeight: "var(--ecmp-font-title-line)",
    fontWeight: "var(--ecmp-font-title-weight)",
  },
  sectionTitle: {
    fontSize: "var(--ecmp-font-section-title-size)",
    lineHeight: "var(--ecmp-font-section-title-line)",
    fontWeight: "var(--ecmp-font-section-title-weight)",
  },
  cardTitle: {
    fontSize: "var(--ecmp-font-card-title-size)",
    lineHeight: "var(--ecmp-font-card-title-line)",
    fontWeight: "var(--ecmp-font-card-title-weight)",
  },
  subtitle: {
    fontSize: "var(--ecmp-font-subtitle-size)",
    lineHeight: "var(--ecmp-font-subtitle-line)",
    fontWeight: "var(--ecmp-font-subtitle-weight)",
  },
  body: {
    fontSize: "var(--ecmp-font-body-size)",
    lineHeight: "var(--ecmp-font-body-line)",
    fontWeight: "var(--ecmp-font-body-weight)",
  },
  bodySmall: {
    fontSize: "var(--ecmp-font-body-small-size)",
    lineHeight: "var(--ecmp-font-body-small-line)",
    fontWeight: "var(--ecmp-font-body-small-weight)",
  },
  label: {
    fontSize: "var(--ecmp-font-label-size)",
    lineHeight: "var(--ecmp-font-label-line)",
    fontWeight: "var(--ecmp-font-label-weight)",
  },
  helper: {
    fontSize: "var(--ecmp-font-helper-size)",
    lineHeight: "var(--ecmp-font-helper-line)",
    fontWeight: "var(--ecmp-font-helper-weight)",
  },
  caption: {
    fontSize: "var(--ecmp-font-caption-size)",
    lineHeight: "var(--ecmp-font-caption-line)",
    fontWeight: "var(--ecmp-font-caption-weight)",
  },
  overline: {
    fontSize: "var(--ecmp-font-overline-size)",
    lineHeight: "var(--ecmp-font-overline-line)",
    fontWeight: "var(--ecmp-font-overline-weight)",
    letterSpacing: "var(--ecmp-font-overline-tracking)",
  },
} as const;

export type TypographyVariant = keyof typeof typography;
