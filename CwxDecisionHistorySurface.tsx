"use client";

import type { ReactNode } from "react";
import { SectionHeader } from "@/shared/ui";
import { cn } from "@/shared/utils";

export type CwxDecisionHistorySurfaceProps = {
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
   * Native decision presentation (Foundation resolution / Aggregate resolutionHistory).
   * Parent owns SoT selection and data; this shell never branches on SoT.
   */
  children: ReactNode;
  className?: string;
};

/**
 * CWX-M4 Decision History Surface — presentation shell only.
 *
 * Answers: "What decisions have already been taken on this Case?"
 * Compose existing decision presentation via children.
 * Never fetch, mutate, permission-check, or select SoT.
 */
export function CwxDecisionHistorySurface({
  title,
  description,
  showHeading = true,
  children,
  className,
}: CwxDecisionHistorySurfaceProps) {
  return (
    <section
      data-testid="cwx-decision-history-surface"
      className={cn("space-y-[var(--ecmp-panel-gap)]", className)}
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
