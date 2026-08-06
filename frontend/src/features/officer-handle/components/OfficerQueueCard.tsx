"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody } from "@/shared/ui";
import {
  slaRemainingMs,
  hasEscalationContextRequest,
  hasRejectContinuity,
  hasReopenContinuity,
  type MockComplaint,
  type MockPriority,
} from "@/features/supervisor-assign/mock/assignmentRepository";
import { isBatchAtLeast } from "@/shared/config/uiBatch";

function priorityTone(
  priority: MockPriority,
): "danger" | "warning" | "neutral" {
  if (priority === "HIGH") return "danger";
  if (priority === "MEDIUM") return "warning";
  return "neutral";
}

function statusTone(
  status: MockComplaint["status"],
): "info" | "primary" | "warning" {
  if (status === "REOPENED") return "warning";
  return status === "IN_PROGRESS" ? "primary" : "info";
}

export interface OfficerQueueCardProps {
  complaint: MockComplaint;
  onOpen: (id: string) => void;
}

/** Queue row for SCR-Q-01 (assigned / in-progress / reopened). */
export function OfficerQueueCard({
  complaint,
  onOpen,
}: OfficerQueueCardProps) {
  const t = useTranslations("officerHandle");
  const tReject = useTranslations("rejectedResubmission");
  const tReopen = useTranslations("reopenedContinuation");
  const tEsc = useTranslations("escalationHandover");
  const showRejected =
    isBatchAtLeast("R2B1") && hasRejectContinuity(complaint);
  const showReopened =
    isBatchAtLeast("R2B2") && hasReopenContinuity(complaint);
  const showEscalationContext =
    isBatchAtLeast("R2B3") && hasEscalationContextRequest(complaint);
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
    <Card
      interactive
      role="button"
      tabIndex={0}
      aria-label={t("openHandlingAria", { reference: complaint.reference })}
      onClick={() => onOpen(complaint.id)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onOpen(complaint.id);
        }
      }}
    >
      <CardBody className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium text-ecmp-text-primary">
              {complaint.reference}
            </span>
            <Badge tone={statusTone(complaint.status)} variant="outline">
              {t(`status.${complaint.status}`)}
            </Badge>
            {showRejected ? (
              <Badge tone="danger" variant="soft">
                {tReject("rejectedBadge")}
              </Badge>
            ) : null}
            {showReopened ? (
              <Badge tone="warning" variant="soft">
                {tReopen("reopenedBadge")}
              </Badge>
            ) : null}
            {showEscalationContext ? (
              <Badge tone="warning" variant="soft">
                {tEsc("contextRequestedBadge")}
              </Badge>
            ) : null}
            <Badge tone={priorityTone(complaint.priority)} variant="soft">
              {t(`priority.${complaint.priority}`)}
            </Badge>
          </div>
          <p className="truncate text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
            {complaint.subject}
          </p>
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("customerUnit", {
              customer: complaint.customerName,
              unit: complaint.assignedUnitName ?? "—",
            })}
          </p>
        </div>
        <div className="shrink-0">
          <Badge tone={slaTone} variant="soft">
            {slaLabel}
          </Badge>
        </div>
      </CardBody>
    </Card>
  );
}
