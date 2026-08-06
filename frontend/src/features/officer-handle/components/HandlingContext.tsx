"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody, CardHeader } from "@/shared/ui";
import {
  slaRemainingMs,
  type MockComplaint,
} from "@/features/supervisor-assign/mock/assignmentRepository";

export interface HandlingContextProps {
  complaint: MockComplaint;
}

/** Context header: case / customer / assignment / SLA (SCR-WS-04). */
export function HandlingContext({ complaint }: HandlingContextProps) {
  const t = useTranslations("officerHandle");
  const remaining = slaRemainingMs(complaint);
  let slaLabel = t("slaUnknown");
  let slaTone: "danger" | "warning" | "success" | "neutral" = "neutral";
  if (remaining !== null) {
    const hours = remaining / 3600_000;
    if (remaining < 0) {
      slaLabel = t("slaOverdue", { hours: Math.ceil(Math.abs(hours)) });
      slaTone = "danger";
    } else {
      slaLabel = t("slaRemainingHours", {
        hours: Math.max(1, Math.ceil(hours)),
      });
      slaTone = hours < 8 ? "warning" : "success";
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-medium text-ecmp-text-primary">
            {complaint.reference}
          </span>
          <Badge tone={complaint.status === "IN_PROGRESS" ? "primary" : "info"} variant="outline">
            {t(`status.${complaint.status}`)}
          </Badge>
          <Badge tone="neutral" variant="soft">
            {t(`priority.${complaint.priority}`)}
          </Badge>
          <Badge tone={slaTone} variant="soft">
            {slaLabel}
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
              {t("fieldChannel")}
            </dt>
            <dd className="text-ecmp-text-primary">{complaint.channel}</dd>
          </div>
          <div>
            <dt className="text-[length:var(--ecmp-font-overline-size)] uppercase tracking-wide text-ecmp-text-secondary">
              {t("fieldUnit")}
            </dt>
            <dd className="text-ecmp-text-primary">
              {complaint.assignedUnitName ?? "—"}
            </dd>
          </div>
        </dl>
      </CardBody>
    </Card>
  );
}
