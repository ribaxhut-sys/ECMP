"use client";

import { useTranslations } from "next-intl";
import { Card, CardBody, CardHeader, CardTitle } from "@/shared/ui";
import type { OperationalContextFields } from "./deriveOperationalContext";

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0 space-y-1">
      <dt className="text-[length:var(--ecmp-font-overline-size)] font-[number:var(--ecmp-font-overline-weight)] uppercase tracking-[var(--ecmp-font-overline-tracking)] text-ecmp-text-secondary">
        {label}
      </dt>
      <dd className="break-words text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
        {value}
      </dd>
    </div>
  );
}

export type CwxOperationalContextPanelProps = {
  fields: OperationalContextFields;
  /** Pre-formatted / translated display values. */
  labels: {
    status: string;
    assignedTo?: string;
    escalationStatus?: string;
    branch?: string;
    lastUpdated?: string;
  };
};

/**
 * CWX-M2 Operational Context — secondary ops only.
 * Never repeats Priority / Owner / SLA / Current Work.
 */
export function CwxOperationalContextPanel({
  fields,
  labels,
}: CwxOperationalContextPanelProps) {
  const t = useTranslations("cwx");

  return (
    <Card data-testid="cwx-operational-context">
      <CardHeader>
        <CardTitle>{t("operationalContextTitle")}</CardTitle>
      </CardHeader>
      <CardBody>
        <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
          <Field label={t("fieldStatus")} value={labels.status} />
          {fields.assignedTo && labels.assignedTo ? (
            <Field label={t("fieldAssignedTo")} value={labels.assignedTo} />
          ) : null}
          {fields.escalationStatus && labels.escalationStatus ? (
            <Field
              label={t("fieldEscalationStatus")}
              value={labels.escalationStatus}
            />
          ) : null}
          {fields.branch && labels.branch ? (
            <Field label={t("fieldBranch")} value={labels.branch} />
          ) : null}
          {fields.lastUpdated && labels.lastUpdated ? (
            <Field label={t("fieldLastUpdated")} value={labels.lastUpdated} />
          ) : null}
        </dl>
      </CardBody>
    </Card>
  );
}
