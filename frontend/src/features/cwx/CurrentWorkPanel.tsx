"use client";

import { useTranslations } from "next-intl";
import { Card, CardBody, CardHeader, CardTitle } from "@/shared/ui";
import type {
  CurrentWorkFields,
  CwxNextActionKey,
} from "./deriveOperationalContext";

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

function nextActionMessageKey(key: CwxNextActionKey): string | null {
  switch (key) {
    case "assign":
      return "nextActionAssign";
    case "start_progress":
      return "nextActionStartProgress";
    case "mark_pending":
      return "nextActionMarkPending";
    case "resume":
      return "nextActionResume";
    case "close":
      return "nextActionClose";
    case "resolve":
      return "nextActionResolve";
    case "review_escalation":
      return "nextActionReviewEscalation";
    case "none":
      return null;
  }
}

export type CwxCurrentWorkPanelProps = {
  fields: CurrentWorkFields;
  responsibleLabel?: string;
  dueLabel?: string;
};

/**
 * CWX-M2 Current Work — what should happen next.
 * Hidden when case is closed/cancelled (fields.show === false).
 */
export function CwxCurrentWorkPanel({
  fields,
  responsibleLabel,
  dueLabel,
}: CwxCurrentWorkPanelProps) {
  const t = useTranslations("cwx");
  if (!fields.show) return null;

  const nextKey = nextActionMessageKey(fields.nextActionKey);
  const nextLabel = nextKey ? t(nextKey) : null;
  const blockingLabel =
    fields.blockingReasonKey === "waiting_customer"
      ? t("blockingWaitingCustomer")
      : null;

  return (
    <Card data-testid="cwx-current-work">
      <CardHeader>
        <CardTitle>{t("currentWorkTitle")}</CardTitle>
      </CardHeader>
      <CardBody>
        <dl className="grid grid-cols-1 gap-[var(--ecmp-form-gap)] sm:grid-cols-2">
          {fields.responsible && responsibleLabel ? (
            <Field label={t("fieldResponsible")} value={responsibleLabel} />
          ) : null}
          {fields.dueAt && dueLabel ? (
            <Field label={t("fieldDue")} value={dueLabel} />
          ) : null}
          {nextLabel ? (
            <Field label={t("fieldNextAction")} value={nextLabel} />
          ) : null}
          {blockingLabel ? (
            <Field label={t("fieldBlocking")} value={blockingLabel} />
          ) : null}
        </dl>
      </CardBody>
    </Card>
  );
}
