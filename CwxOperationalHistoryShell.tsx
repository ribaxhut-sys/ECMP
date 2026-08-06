"use client";

import type { ReactNode } from "react";
import { SectionHeader } from "@/shared/ui";
import { cn } from "@/shared/utils";

export type CwxOperationalHistoryShellProps = {
  /** Presentation label only — parent supplies translated copy. Used for aria-label. */
  title: string;
  /** Optional presentation hint — never business/context fields. */
  description?: string;
  /**
   * History region content (navigation + active surface).
   * Parent owns SoT selection and data; this shell never branches on SoT.
   */
  children: ReactNode;
  className?: string;
};

/**
 * CWX-M4 Operational History Shell — presentation only.
 *
 * Answers: "What has happened to this Case?"
 * Compose history navigation and surfaces via children.
 * Never fetch, mutate, permission-check, or select SoT.
 */
export function CwxOperationalHistoryShell({
  title,
  description,
  children,
  className,
}: CwxOperationalHistoryShellProps) {
  return (
    <section
      data-testid="cwx-operational-history-shell"
      className={cn("space-y-[var(--ecmp-panel-gap)]", className)}
      aria-label={title}
    >
      <SectionHeader title={title} description={description} />
      {children}
    </section>
  );
}
