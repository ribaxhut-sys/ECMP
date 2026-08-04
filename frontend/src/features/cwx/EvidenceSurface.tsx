"use client";

import type { ReactNode } from "react";
import { SectionHeader } from "@/shared/ui";

export type CwxEvidenceSurfaceProps = {
  /** Presentation label only — parent supplies translated copy. Used for aria-label. */
  title: string;
  /** Optional presentation hint — never business/context fields. */
  description?: string;
  /**
   * When false, omit visual SectionHeader so a native child that already
   * provides its own heading is the sole visual title (a11y via aria-label).
   */
  showHeading?: boolean;
  /**
   * Native evidence capability (Foundation or Aggregate).
   * Parent owns SoT selection; this shell never branches on SoT.
   */
  children: ReactNode;
};

/**
 * CWX-M3 Evidence Surface — presentation shell only.
 *
 * Answers: "What evidence supports this Case?"
 * Compose native attachment capability via children.
 * Never fetch, mutate, permission-check, or select SoT.
 */
export function CwxEvidenceSurface({
  title,
  description,
  showHeading = true,
  children,
}: CwxEvidenceSurfaceProps) {
  return (
    <section
      data-testid="cwx-evidence-surface"
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={title}
    >
      {showHeading ? (
        <SectionHeader title={title} description={description} />
      ) : description ? (
        <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          {description}
        </p>
      ) : null}
      {children}
    </section>
  );
}
