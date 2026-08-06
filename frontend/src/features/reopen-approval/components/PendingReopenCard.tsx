"use client";

import { useTranslations } from "next-intl";
import { Badge, Card, CardBody } from "@/shared/ui";
import type { MockComplaint } from "@/features/supervisor-assign/mock/assignmentRepository";

export interface PendingReopenCardProps {
  complaint: MockComplaint;
  onOpen: (id: string) => void;
}

/** Queue row for SCR-Q-02 pending reopen segment. */
export function PendingReopenCard({
  complaint,
  onOpen,
}: PendingReopenCardProps) {
  const t = useTranslations("reopenApproval");

  return (
    <Card
      interactive
      role="button"
      tabIndex={0}
      aria-label={t("openAria", { reference: complaint.reference })}
      onClick={() => onOpen(complaint.id)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onOpen(complaint.id);
        }
      }}
    >
      <CardBody className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium text-ecmp-text-primary">
              {complaint.reference}
            </span>
            <Badge tone="warning" variant="soft">
              {t("pendingBadge")}
            </Badge>
          </div>
          <p className="truncate text-ecmp-text-primary">{complaint.subject}</p>
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {t("customerUnit", {
              customer: complaint.customerName,
              unit: complaint.assignedUnitName ?? "—",
            })}
          </p>
        </div>
      </CardBody>
    </Card>
  );
}
