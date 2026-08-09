"use client";

import type { ReactNode } from "react";
import { Badge, type BadgeTone } from "@/shared/ui";

export type CwxContextHeaderProps = {
  complaintId: string;
  customer: string;
  title: string;
  priorityLabel: string;
  priorityTone?: BadgeTone;
  currentWork: string;
  owner: string;
  slaLabel: string;
  slaTone?: BadgeTone;
};

/**
 * CWX-M1 Context Header — sticky, ≤2 rows, no secondary actions.
 */
export function CwxContextHeader({
  complaintId,
  customer,
  title,
  priorityLabel,
  priorityTone = "neutral",
  currentWork,
  owner,
  slaLabel,
  slaTone = "neutral",
}: CwxContextHeaderProps) {
  return (
    <header
      data-testid="cwx-context-header"
      className="sticky top-0 z-20 border-b border-ecmp-border/60 bg-ecmp-background/95 px-1 py-2.5 backdrop-blur-sm"
    >
      {/* Row 1 — identity */}
      <div className="flex min-w-0 flex-wrap items-baseline gap-x-3 gap-y-1">
        <p className="shrink-0 font-mono text-[13px] font-medium tabular-nums text-ecmp-text-primary">
          {complaintId}
        </p>
        <p className="min-w-0 truncate text-[14px] font-medium text-ecmp-text-primary">
          {title}
        </p>
        <p className="min-w-0 truncate text-[13px] text-ecmp-text-secondary">
          {customer}
        </p>
      </div>

      {/* Row 2 — operational signals */}
      <div className="mt-1.5 flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1 text-[12px]">
        <Badge tone={priorityTone} variant="soft">
          {priorityLabel}
        </Badge>
        <span className="text-ecmp-text-secondary">
          <span className="text-ecmp-text-secondary/80">Work </span>
          <span className="font-medium text-ecmp-text-primary">{currentWork}</span>
        </span>
        <span className="text-ecmp-text-secondary">
          <span className="text-ecmp-text-secondary/80">Owner </span>
          <span className="font-medium text-ecmp-text-primary">{owner}</span>
        </span>
        <span className="inline-flex items-center gap-1.5 text-ecmp-text-secondary">
          <span className="text-ecmp-text-secondary/80">SLA</span>
          <Badge tone={slaTone} variant="soft">
            {slaLabel}
          </Badge>
        </span>
      </div>
    </header>
  );
}

export function CwxContextHeaderSkeleton(): ReactNode {
  return (
    <div
      data-testid="cwx-context-header-skeleton"
      className="h-[4.25rem] animate-pulse rounded-[var(--ecmp-radius-md)] bg-ecmp-surface-sunken/50"
      aria-hidden
    />
  );
}
