"use client";

import { useTranslations } from "next-intl";
import { Card, CardBody, CardHeader, CardTitle } from "@/shared/ui";
import type { CustomerSummaryFields } from "./deriveOperationalContext";

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

export type CwxCustomerSummaryProps = {
  fields: CustomerSummaryFields;
};

/**
 * CWX-M2 Customer Summary — reference only. Never Customer Master.
 * Renders nothing when no existing customer fields are present.
 */
export function CwxCustomerSummary({ fields }: CwxCustomerSummaryProps) {
  const t = useTranslations("cwx");
  const hasAny =
    Boolean(fields.name) ||
    typeof fields.complaintCount === "number" ||
    Boolean(fields.customerType);

  if (!hasAny) return null;

  return (
    <Card data-testid="cwx-customer-summary">
      <CardHeader>
        <CardTitle>{t("customerSummaryTitle")}</CardTitle>
      </CardHeader>
      <CardBody>
        <p className="mb-[var(--ecmp-form-gap)] text-[11px] text-ecmp-text-secondary">
          {t("customerSummaryHint")}
        </p>
        <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
          {fields.name ? (
            <Field label={t("fieldCustomerName")} value={fields.name} />
          ) : null}
          {fields.customerType ? (
            <Field label={t("fieldCustomerType")} value={fields.customerType} />
          ) : null}
          {typeof fields.complaintCount === "number" ? (
            <Field
              label={t("fieldComplaintCount")}
              value={String(fields.complaintCount)}
            />
          ) : null}
        </dl>
      </CardBody>
    </Card>
  );
}
