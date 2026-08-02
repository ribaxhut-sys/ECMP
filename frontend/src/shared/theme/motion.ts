/**
 * ECMP motion tokens.
 * Use for hover, focus, modal/toast enter-exit, skeleton pulse.
 * Never animate entire pages. Respect prefers-reduced-motion (globals.css).
 */

export const motion = {
  duration: {
    fast: "var(--ecmp-duration-fast)",
    normal: "var(--ecmp-duration-normal)",
    slow: "var(--ecmp-duration-slow)",
  },
  ease: {
    standard: "var(--ecmp-ease-standard)",
    enter: "var(--ecmp-ease-enter)",
    exit: "var(--ecmp-ease-exit)",
    hover: "var(--ecmp-ease-hover)",
  },
} as const;

export type MotionToken = typeof motion;
