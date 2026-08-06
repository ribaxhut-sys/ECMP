"use client";

import { useTranslations } from "next-intl";
import { Alert, Badge, Card, CardBody } from "@/shared/ui";
import type { MockComplaint } from "@/features/supervisor-assign/mock/assignmentRepository";
import { latestRejectHistory } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface RejectionContinuityBannerProps {
  complaint: MockComplaint;
}

/** C-REJECT-CONT — highlight latest reject reason on SCR-WS-06. */
export function RejectionContinuityBanner({
  complaint,
}: RejectionContinuityBannerProps) {
  const t = useTranslations("rejectedResubmission");
  const latest = latestRejectHistory(complaint);
  const reason =
    latest?.reason?.trim() || complaint.rejectReason?.trim() || null;

  if (!reason) return null;

  return (
    <Card>
      <CardBody className="space-y-2">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="danger" variant="soft">
            {t("rejectedBadge")}
          </Badge>
          {latest ? (
            <span className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
              {t("rejectedBy", { actor: latest.actorName })}
            </span>
          ) : null}
        </div>
        <Alert tone="warning" title={t("rejectBannerTitle")} />
        <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
          {reason}
        </p>
      </CardBody>
    </Card>
  );
}
