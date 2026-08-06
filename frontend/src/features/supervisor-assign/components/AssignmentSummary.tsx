"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody, CardHeader } from "@/shared/ui";
import type { MockComplaint } from "../mock/assignmentRepository";

export interface AssignmentSummaryProps {
  complaint: MockComplaint;
  selectedUnitName?: string | null;
}

/** Case context + pending assignment summary (SCR-WS-09). */
export function AssignmentSummary({
  complaint,
  selectedUnitName,
}: AssignmentSummaryProps) {
  const t = useTranslations("supervisorAssign");

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-medium text-ecmp-text-primary">
            {complaint.reference}
          </span>
          <Badge tone="info" variant="outline">
            {complaint.status === "ASSIGNED"
              ? t("statusAssigned")
              : t("statusRegistered")}
          </Badge>
        </div>
      </CardHeader>
      <CardBody className="space-y-3">
        <dl className="grid gap-3 sm:grid-cols-2">
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("fieldSubject")}
            </dt>
            <dd className="text-ecmp-text-primary">{complaint.subject}</dd>
          </div>
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("fieldCustomer")}
            </dt>
            <dd className="text-ecmp-text-primary">{complaint.customerName}</dd>
          </div>
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("fieldChannel")}
            </dt>
            <dd className="text-ecmp-text-primary">{complaint.channel}</dd>
          </div>
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("fieldPriority")}
            </dt>
            <dd className="text-ecmp-text-primary">
              {t(`priority.${complaint.priority}`)}
            </dd>
          </div>
        </dl>
        {selectedUnitName ? (
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("pendingUnit", { unit: selectedUnitName })}
          </p>
        ) : null}
        {complaint.status === "ASSIGNED" && complaint.assignedUnitName ? (
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-success-text">
            {t("assignedToUnit", { unit: complaint.assignedUnitName })}
          </p>
        ) : null}
      </CardBody>
    </Card>
  );
}
