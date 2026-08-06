"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody, CardHeader } from "@/shared/ui";
import type { MockComplaint } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface FollowUpContextProps {
  complaint: MockComplaint;
}

/** Context + read-only case summary (SCR-WS-02). */
export function FollowUpContext({ complaint }: FollowUpContextProps) {
  const t = useTranslations("intake");

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_18rem]">
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium text-ecmp-text-primary">
              {complaint.reference}
            </span>
            <Badge tone="info" variant="outline">
              {t(`status.${complaint.status}`)}
            </Badge>
          </div>
        </CardHeader>
        <CardBody className="space-y-3">
          <dl className="grid gap-3 sm:grid-cols-2">
            <div>
              <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                {t("fieldCustomer")}
              </dt>
              <dd className="text-ecmp-text-primary">
                {complaint.customerName} ({complaint.customerRef})
              </dd>
            </div>
            <div>
              <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                {t("fieldSubject")}
              </dt>
              <dd className="text-ecmp-text-primary">{complaint.subject}</dd>
            </div>
            <div>
              <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                {t("fieldCategory")}
              </dt>
              <dd className="text-ecmp-text-primary">
                {t(`category.${complaint.category}`)}
              </dd>
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
            <div>
              <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
                {t("fieldStatus")}
              </dt>
              <dd className="text-ecmp-text-primary">{complaint.status}</dd>
            </div>
          </dl>
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("fieldDescription")}
            </dt>
            <dd className="mt-1 text-ecmp-text-primary">{complaint.description}</dd>
          </div>
        </CardBody>
      </Card>

      <aside>
        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("caseSummaryTitle")}
            </h2>
          </CardHeader>
          <CardBody className="space-y-2 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            <p>{t("caseSummaryStatus", { status: complaint.status })}</p>
            <p>
              {t("caseSummaryNotes", {
                count: complaint.followUpNotes.length,
              })}
            </p>
            <p className="text-ecmp-text-primary">{complaint.subject}</p>
          </CardBody>
        </Card>
      </aside>
    </div>
  );
}
