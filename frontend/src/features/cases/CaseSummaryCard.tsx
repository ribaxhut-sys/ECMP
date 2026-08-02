"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import type { CmCase } from "@/lib/api/cmCase";
import { cn } from "@/shared/utils";
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
  const t = useTranslations("cases");
  const detailHref =
    href ?? `/complaints/cm/cases/${encodeURIComponent(caseData.caseId)}`;

  return (
    <Card>
      <CardHeader className="flex flex-row flex-wrap items-start justify-between gap-[var(--ecmp-form-gap)]">
        <div className="min-w-0 space-y-1">
          <CardTitle className="truncate">{caseData.caseNumber}</CardTitle>
          <CardDescription className="truncate">{caseData.subject}</CardDescription>
        </div>
        <CaseStatusBadge status={caseData.status} />
      </CardHeader>
      <CardBody className="space-y-[var(--ecmp-panel-gap)]">
        <dl className="grid gap-[var(--ecmp-form-gap)] text-[length:var(--ecmp-font-body-size)] sm:grid-cols-2">
          <div className="space-y-1">
            <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("type")}
            </dt>
            <dd className="text-ecmp-text-primary">{caseData.caseType}</dd>
          </div>
          <div className="space-y-1">
            <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("priority")}
            </dt>
            <dd className="text-ecmp-text-primary">{caseData.priority}</dd>
          </div>
          <div className="space-y-1">
            <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("unit")}
            </dt>
            <dd className="text-ecmp-text-primary">{caseData.owningUnitId ?? "—"}</dd>
          </div>
          <div className="space-y-1">
            <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
              {t("customer")}
            </dt>
            <dd className="truncate text-ecmp-text-primary">{caseData.customerId}</dd>
          </div>
        </dl>
        <Link
          href={detailHref}
          className={cn(
            "inline-flex min-h-[var(--ecmp-touch-min)] items-center justify-center rounded-[var(--ecmp-radius-button)]",
            "border border-transparent bg-ecmp-secondary px-3 font-medium",
            "text-[length:var(--ecmp-font-body-small-size)] text-ecmp-secondary-foreground shadow-ecmp-raised",
            "hover:bg-[color-mix(in_srgb,var(--ecmp-color-secondary)_88%,black)] hover:shadow-ecmp-hover",
            "focus-visible:outline-none focus-visible:ring-[length:var(--ecmp-focus-ring-width)] focus-visible:ring-ecmp-focus focus-visible:ring-offset-[length:var(--ecmp-focus-ring-offset)]",
          )}
        >
          {t("view")}
        </Link>
      </CardBody>
    </Card>
  );
}
