/**
 * ECMP typography tokens.
 * Body minimum: 16px. Prefer CSS variables / Tailwind token classes.
 */

export const typography = {
  display: {
    fontSize: "var(--ecmp-font-display-size)",
    lineHeight: "var(--ecmp-font-display-line)",
    fontWeight: "var(--ecmp-font-display-weight)",
  },
  heading: {
    fontSize: "var(--ecmp-font-heading-size)",
    lineHeight: "var(--ecmp-font-heading-line)",
    fontWeight: "var(--ecmp-font-heading-weight)",
  },
  title: {
    fontSize: "var(--ecmp-font-title-size)",
    lineHeight: "var(--ecmp-font-title-line)",
    fontWeight: "var(--ecmp-font-title-weight)",
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
  caption: {
    fontSize: "var(--ecmp-font-caption-size)",
    lineHeight: "var(--ecmp-font-caption-line)",
    fontWeight: "var(--ecmp-font-caption-weight)",
  },
} as const;

export type TypographyVariant = keyof typeof typography;
