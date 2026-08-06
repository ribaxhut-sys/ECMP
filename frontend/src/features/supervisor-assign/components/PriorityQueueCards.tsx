"use client";

import { useTranslations } from "next-intl";
import { Alert, Badge, Button, Card, CardBody } from "@/shared/ui";
import type {
  MockComplaint,
  MockPriority,
} from "../mock/assignmentRepository";

function priorityTone(
  priority: MockPriority,
): "danger" | "warning" | "neutral" {
  if (priority === "HIGH") return "danger";
  if (priority === "MEDIUM") return "warning";
  return "neutral";
}

export interface EscalationQueueCardProps {
  complaint: MockComplaint;
  onOpen?: (id: string) => void;
}

/**
 * SCR-Q-02 — New escalation row (B6 display; R2-B3 opens SCR-WS-11).
 */
export function EscalationQueueCard({
  complaint,
  onOpen,
}: EscalationQueueCardProps) {
  const t = useTranslations("supervisorQueuePriority");
  const interactive = Boolean(onOpen);

  return (
    <Card
      interactive={interactive}
      role={interactive ? "button" : undefined}
      tabIndex={interactive ? 0 : undefined}
      aria-label={
        interactive
          ? t("openEscalationAria", { reference: complaint.reference })
          : undefined
      }
      onClick={interactive ? () => onOpen?.(complaint.id) : undefined}
      onKeyDown={
        interactive
          ? (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onOpen?.(complaint.id);
              }
            }
          : undefined
      }
    >
      <CardBody className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium text-ecmp-text-primary">
              {complaint.reference}
            </span>
            <Badge tone="danger" variant="outline">
              {t("escalationBadge")}
            </Badge>
            <Badge tone={priorityTone(complaint.priority)} variant="soft">
              {t(`priority.${complaint.priority}`)}
            </Badge>
            <Badge tone="info" variant="outline">
              {complaint.status}
            </Badge>
          </div>
          <p className="truncate text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
            {complaint.subject}
          </p>
          <p className="text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
            {complaint.escalationNote ?? t("escalationReasonFallback")}
          </p>
        </div>
        <div className="flex shrink-0 flex-col items-stretch gap-2 sm:items-end">
          {interactive ? (
            <Button type="button" variant="outline">
              {t("escalationOpenAction")}
            </Button>
          ) : (
            <>
              <Button
                type="button"
                variant="outline"
                disabled
                title={t("escalationStubTitle")}
              >
                {t("escalationStubAction")}
              </Button>
              <p className="max-w-[14rem] text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
                {t("escalationStubHint")}
              </p>
            </>
          )}
        </div>
      </CardBody>
    </Card>
  );
}

export interface SlaRiskQueueCardProps {
  complaint: MockComplaint;
  onOpen?: (id: string) => void;
}

/** SCR-Q-02 — SLA at-risk / overdue row (B6). */
export function SlaRiskQueueCard({
  complaint,
  onOpen,
}: SlaRiskQueueCardProps) {
  const t = useTranslations("supervisorQueuePriority");
  const due = complaint.slaDueAt
    ? new Date(complaint.slaDueAt).getTime()
    : null;
  const remainingMs = due != null ? due - Date.now() : null;
  let slaLabel = t("slaUnknown");
  let slaTone: "danger" | "warning" = "warning";
  if (remainingMs != null) {
    const hours = remainingMs / 3600_000;
    if (remainingMs < 0) {
      slaLabel = t("slaOverdue", { hours: Math.ceil(Math.abs(hours)) });
      slaTone = "danger";
    } else {
      slaLabel = t("slaRemaining", { hours: Math.max(1, Math.ceil(hours)) });
      slaTone = "warning";
    }
  }

  const interactive = Boolean(onOpen);

  return (
    <Card
      interactive={interactive}
      role={interactive ? "button" : undefined}
      tabIndex={interactive ? 0 : undefined}
      aria-label={
        interactive
          ? t("openSlaAria", { reference: complaint.reference })
          : undefined
      }
      onClick={interactive ? () => onOpen?.(complaint.id) : undefined}
      onKeyDown={
        interactive
          ? (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onOpen?.(complaint.id);
              }
            }
          : undefined
      }
    >
      <CardBody className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-medium text-ecmp-text-primary">
              {complaint.reference}
            </span>
            <Badge tone={slaTone} variant="outline">
              {slaLabel}
            </Badge>
            <Badge tone={priorityTone(complaint.priority)} variant="soft">
              {t(`priority.${complaint.priority}`)}
            </Badge>
            <Badge tone="info" variant="outline">
              {complaint.status}
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
        <div className="shrink-0 text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
          <p>{t("segmentSla")}</p>
        </div>
      </CardBody>
    </Card>
  );
}

/** Banner for escalation count highlight (SCR-Q-02 notifications). */
export function EscalationCountBanner({ count }: { count: number }) {
  const t = useTranslations("supervisorQueuePriority");
  if (count <= 0) return null;
  return <Alert tone="warning" title={t("escalationCountBanner", { count })} />;
}
