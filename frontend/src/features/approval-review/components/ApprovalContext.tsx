"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody, CardHeader } from "@/shared/ui";
import type { MockComplaint } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface ApprovalContextProps {
  complaint: MockComplaint;
}

/** Case context + submitted meta (SCR-WS-10). No Timeline / History. */
export function ApprovalContext({ complaint }: ApprovalContextProps) {
  const t = useTranslations("approvalReview");

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-medium text-ecmp-text-primary">
            {complaint.reference}
          </span>
          <Badge tone="warning" variant="outline">
            {complaint.status}
          </Badge>
          <Badge tone="neutral" variant="soft">
            {t(`priority.${complaint.priority}`)}
          </Badge>
        </div>
      </CardHeader>
      <CardBody>
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
              {t("fieldUnit")}
            </dt>
            <dd className="text-ecmp-text-primary">
              {complaint.assignedUnitName ?? "—"}
            </dd>
          </div>
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("fieldSubmitted")}
            </dt>
            <dd className="text-ecmp-text-primary">
              {complaint.submittedAt
                ? new Date(complaint.submittedAt).toLocaleString()
                : "—"}
            </dd>
          </div>
        </dl>
      </CardBody>
    </Card>
  );
}
