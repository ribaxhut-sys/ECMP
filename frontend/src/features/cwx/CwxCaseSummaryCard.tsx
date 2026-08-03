"use client";

import { useTranslations } from "next-intl";
import { Card, CardBody, CardHeader, CardTitle } from "@/shared/ui";
import type { CaseSummaryFields } from "./deriveOperationalContext";

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

export type CwxCaseSummaryCardProps = {
  fields: CaseSummaryFields;
  /** Translated current stage / created display. */
  stageLabel: string;
  createdLabel?: string;
};

/**
 * CWX-M2 Case Summary — compact glance. Does not repeat Priority.
 * Severity omitted when no separate severity field exists on the payload.
 */
export function CwxCaseSummaryCard({
  fields,
  stageLabel,
  createdLabel,
}: CwxCaseSummaryCardProps) {
  const t = useTranslations("cwx");

  return (
    <Card data-testid="cwx-case-summary">
      <CardHeader>
        <CardTitle>{t("caseSummaryTitle")}</CardTitle>
      </CardHeader>
      <CardBody>
        <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
          {fields.category ? (
            <Field label={t("fieldCategory")} value={fields.category} />
          ) : null}
          {fields.channel ? (
            <Field label={t("fieldChannel")} value={fields.channel} />
          ) : null}
          {fields.createdAt && createdLabel ? (
            <Field label={t("fieldCreated")} value={createdLabel} />
          ) : null}
          <Field label={t("fieldStage")} value={stageLabel} />
        </dl>
      </CardBody>
    </Card>
  );
}
