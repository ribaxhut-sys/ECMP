"use client";

import type { ReactNode } from "react";
import type { CwxLayoutLevel } from "./deriveContextLevel";

export type CwxContextAwareLayoutProps = {
  level: CwxLayoutLevel;
  header: ReactNode;
  decisionBar: ReactNode;
  main: ReactNode;
  /** M1 placeholders only — no business panels. */
  labels: {
    customerHistorySlot: string;
    decisionStatusSlot: string;
    slaAlertSlot: string;
    reserved: string;
  };
};

function SlotPlaceholder({
  testId,
  title,
  hint,
}: {
  testId: string;
  title: string;
  hint: string;
}) {
  return (
    <aside
      data-testid={testId}
      className="rounded-[var(--ecmp-radius-md)] border border-dashed border-ecmp-border/70 bg-ecmp-surface-sunken/30 px-3 py-2.5"
      aria-label={title}
    >
      <p className="text-[12px] font-medium text-ecmp-text-secondary">{title}</p>
      <p className="mt-0.5 text-[11px] text-ecmp-text-secondary/80">{hint}</p>
    </aside>
  );
}

/**
 * CWX-M1 Context-Aware Layout — slots appear by level; content is placeholder only.
 */
export function CwxContextAwareLayout({
  level,
  header,
  decisionBar,
  main,
  labels,
}: CwxContextAwareLayoutProps) {
  return (
    <div
      data-testid="cwx-context-aware-layout"
      data-cwx-level={level}
      className="flex min-h-[60vh] flex-col gap-3"
    >
      {header}

      {level >= 4 ? (
        <SlotPlaceholder
          testId="cwx-slot-sla-alert"
          title={labels.slaAlertSlot}
          hint={labels.reserved}
        />
      ) : null}

      {level >= 3 ? (
        <SlotPlaceholder
          testId="cwx-slot-decision-status"
          title={labels.decisionStatusSlot}
          hint={labels.reserved}
        />
      ) : null}

      {level >= 2 ? (
        <SlotPlaceholder
          testId="cwx-slot-customer-history"
          title={labels.customerHistorySlot}
          hint={labels.reserved}
        />
      ) : null}

      <div data-testid="cwx-main" className="min-w-0 flex-1">
        {main}
      </div>

      {decisionBar}
    </div>
  );
}
