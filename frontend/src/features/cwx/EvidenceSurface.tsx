"use client";

import type { ReactNode } from "react";
import { SectionHeader } from "@/shared/ui";

export type CwxEvidenceSurfaceProps = {
  /** Presentation label only — parent supplies translated copy. */
  title: string;
  /** Optional presentation hint — never business/context fields. */
  description?: string;
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
  children,
}: CwxEvidenceSurfaceProps) {
  return (
    <section
      data-testid="cwx-evidence-surface"
      className="space-y-[var(--ecmp-panel-gap)]"
      aria-label={title}
    >
      <SectionHeader title={title} description={description} />
      {children}
    </section>
  );
}
