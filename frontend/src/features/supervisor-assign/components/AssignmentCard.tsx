"use client";

import { useLocale, useTranslations } from "next-intl";
import { Badge, Card, CardBody } from "@/shared/ui";
import type { MockComplaint, MockPriority } from "../mock/assignmentRepository";

function priorityTone(
  priority: MockPriority,
): "danger" | "warning" | "neutral" {
  if (priority === "HIGH") return "danger";
  if (priority === "MEDIUM") return "warning";
  return "neutral";
}

export interface AssignmentCardProps {
  complaint: MockComplaint;
  onOpen: (id: string) => void;
}

/** Queue row card for SCR-Q-02 unassigned segment (B1 mock). */
export function AssignmentCard({ complaint, onOpen }: AssignmentCardProps) {
  const t = useTranslations("supervisorAssign");
  const locale = useLocale();

  return (
    <Card
      interactive
      role="button"
      tabIndex={0}
      aria-label={t("openAssignmentAria", { reference: complaint.reference })}
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
            <Badge tone="info" variant="outline">
              {t("statusRegistered")}
            </Badge>
            <Badge tone={priorityTone(complaint.priority)} variant="soft">
              {t(`priority.${complaint.priority}`)}
            </Badge>
          </div>
          <p className="truncate text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
            {complaint.subject}
          </p>
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("customerChannel", {
              customer: complaint.customerName,
              channel: complaint.channel,
            })}
          </p>
        </div>
        <div className="shrink-0 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          <p>{t("segmentUnassigned")}</p>
          <p>
            {t("registeredAt", {
              when: new Date(complaint.registeredAt).toLocaleString(locale),
            })}
          </p>
        </div>
      </CardBody>
    </Card>
  );
}
