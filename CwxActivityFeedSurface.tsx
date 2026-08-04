"use client";

import type { ReactNode } from "react";
import { SectionHeader } from "@/shared/ui";
import { cn } from "@/shared/utils";

export type CwxActivityFeedSurfaceProps = {
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
   * Native activity capability (Foundation TimelineCard).
   * Parent owns SoT selection; this shell never branches on SoT.
   */
  children: ReactNode;
  className?: string;
};

/**
 * CWX-M4 Activity Feed Surface — presentation shell only.
 *
 * Answers: "What activity has occurred on this Case?"
 * Compose native timeline capability via children (TimelineCard as-is).
 * Never fetch, mutate, permission-check, or select SoT.
 */
export function CwxActivityFeedSurface({
  title,
  description,
  showHeading = true,
  children,
  className,
}: CwxActivityFeedSurfaceProps) {
  return (
    <section
      data-testid="cwx-activity-feed-surface"
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
