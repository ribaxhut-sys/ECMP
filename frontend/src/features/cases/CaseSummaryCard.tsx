"use client";

import Link from "next/link";
import type { CmCase } from "@/lib/api/cmCase";
import {
  Card,
  CardBody,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/shared/ui";
import { CaseStatusBadge } from "./CaseStatusBadge";

export function CaseSummaryCard({
  caseData,
  href,
}: {
  caseData: CmCase;
  href?: string;
}) {
  const detailHref =
    href ?? `/complaints/cm/cases/${encodeURIComponent(caseData.caseId)}`;

  return (
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 space-y-1">
          <CardTitle className="truncate">{caseData.caseNumber}</CardTitle>
          <CardDescription className="truncate">{caseData.subject}</CardDescription>
        </div>
        <CaseStatusBadge status={caseData.status} />
      </CardHeader>
      <CardBody className="space-y-3">
        <dl className="grid gap-2 text-[length:var(--ecmp-font-body-size)] sm:grid-cols-2">
          <div>
            <dt className="text-ecmp-text-secondary">Type</dt>
            <dd>{caseData.caseType}</dd>
          </div>
          <div>
            <dt className="text-ecmp-text-secondary">Priority</dt>
            <dd>{caseData.priority}</dd>
          </div>
          <div>
            <dt className="text-ecmp-text-secondary">Unit</dt>
            <dd>{caseData.owningUnitId ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-ecmp-text-secondary">Customer</dt>
            <dd className="truncate">{caseData.customerId}</dd>
          </div>
        </dl>
        <Link
          href={detailHref}
          className="inline-flex min-h-[44px] items-center rounded-[var(--ecmp-radius-sm)] border border-ecmp-border bg-ecmp-secondary px-3 text-[length:var(--ecmp-font-caption-size)] font-medium text-ecmp-secondary-foreground hover:opacity-90"
        >
          View case
        </Link>
      </CardBody>
    </Card>
  );
}
