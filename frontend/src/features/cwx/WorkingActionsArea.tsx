"use client";

import type { ReactNode } from "react";
import { SectionHeader } from "@/shared/ui";
import { cn } from "@/shared/utils";

export type CwxWorkingActionsAreaProps = {
  /** Presentation label only — parent supplies translated copy. */
  title: string;
  /** Optional presentation hint — never business/context fields. */
  description?: string;
  /**
   * Native working-action capability (Foundation cards or Aggregate dialogs).
   * Parent owns SoT selection; this shell never branches on SoT.
   */
  children: ReactNode;
  className?: string;
};

/**
 * CWX-M3 Working Actions Area — presentation shell only.
 *
 * Answers: "What work can I perform right now?"
 * Compose native action capability via children.
 * Decision Bar remains the canonical entry (CWX-M1); this is the execution surface.
 * Never fetch, mutate, permission-check, or select SoT.
 */
export function CwxWorkingActionsArea({
  title,
  description,
  children,
  className,
}: CwxWorkingActionsAreaProps) {
  return (
    <section
      data-testid="cwx-working-actions-area"
      className={cn("space-y-[var(--ecmp-panel-gap)]", className)}
      aria-label={title}
    >
      <SectionHeader title={title} description={description} />
      {children}
    </section>
  );
}
