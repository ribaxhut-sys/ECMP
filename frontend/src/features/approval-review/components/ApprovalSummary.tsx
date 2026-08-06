"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody, CardHeader } from "@/shared/ui";
import type { MockComplaint } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface ApprovalSummaryProps {
  complaint: MockComplaint;
}

/** Read-only resolution + C-EVID-MIN summary (SCR-WS-10). */
export function ApprovalSummary({ complaint }: ApprovalSummaryProps) {
  const t = useTranslations("approvalReview");

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_18rem]">
      <Card>
        <CardHeader>
          <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
            {t("resolutionTitle")}
          </h2>
        </CardHeader>
        <CardBody>
          <p className="whitespace-pre-wrap text-ecmp-text-primary">
            {complaint.resolutionSummary ?? t("resolutionEmpty")}
          </p>
        </CardBody>
      </Card>

      <aside>
        <Card>
          <CardHeader>
            <h2 className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
              {t("evidenceTitle")}
            </h2>
            <p className="mt-1 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
              {t("evidenceHint")}
            </p>
          </CardHeader>
          <CardBody>
            {complaint.evidenceItems.length === 0 ? (
              <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {t("evidenceEmpty")}
              </p>
            ) : (
              <ul className="space-y-2">
                {complaint.evidenceItems.map((item) => (
                  <li
                    key={item.id}
                    className="flex items-center justify-between gap-2 rounded-[var(--ecmp-radius-md)] border border-ecmp-border/70 px-3 py-2"
                  >
                    <span className="truncate text-ecmp-text-primary">
                      {item.fileName}
                    </span>
                    <Badge
                      tone={item.status === "ATTACHED" ? "success" : "warning"}
                      variant="outline"
                    >
                      {t(`evidenceStatus.${item.status}`)}
                    </Badge>
                  </li>
                ))}
              </ul>
            )}
          </CardBody>
        </Card>
      </aside>
    </div>
  );
}
