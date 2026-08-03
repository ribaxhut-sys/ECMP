"use client";

import { CwxContextBadges } from "./ContextBadges";
import { CwxOperationalContextPanel } from "./OperationalContextPanel";
import { CwxCurrentWorkPanel } from "./CurrentWorkPanel";
import { CwxCaseSummaryCard } from "./CwxCaseSummaryCard";
import { CwxCustomerSummary } from "./CustomerSummary";
import type { DerivedOperationalContext } from "./deriveOperationalContext";

export type CwxOperationalContextBlockProps = {
  derived: DerivedOperationalContext;
  operationalLabels: {
    status: string;
    assignedTo?: string;
    escalationStatus?: string;
    branch?: string;
    lastUpdated?: string;
  };
  caseSummaryStageLabel: string;
  caseSummaryCreatedLabel?: string;
  responsibleLabel?: string;
  dueLabel?: string;
};

/**
 * CWX-M2 composition — badges + operational panels above legacy main content.
 */
export function CwxOperationalContextBlock({
  derived,
  operationalLabels,
  caseSummaryStageLabel,
  caseSummaryCreatedLabel,
  responsibleLabel,
  dueLabel,
}: CwxOperationalContextBlockProps) {
  return (
    <div
      data-testid="cwx-operational-context-block"
      className="space-y-[var(--ecmp-section-gap)]"
    >
      <CwxContextBadges badges={derived.badges} />
      <div className="grid grid-cols-1 gap-[var(--ecmp-section-gap)] lg:grid-cols-2">
        <CwxOperationalContextPanel
          fields={derived.operational}
          labels={operationalLabels}
        />
        <CwxCurrentWorkPanel
          fields={derived.currentWork}
          responsibleLabel={responsibleLabel}
          dueLabel={dueLabel}
        />
        <CwxCaseSummaryCard
          fields={derived.caseSummary}
          stageLabel={caseSummaryStageLabel}
          createdLabel={caseSummaryCreatedLabel}
        />
        <CwxCustomerSummary fields={derived.customerSummary} />
      </div>
    </div>
  );
}
