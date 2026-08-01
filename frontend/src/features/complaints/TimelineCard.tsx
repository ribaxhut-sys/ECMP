"use client";

import { useCallback, useEffect, useState } from "react";
import { useLocale, useTranslations } from "next-intl";
import { ApiError, fetchComplaintTimeline } from "@/lib/api";
import type { TimelineEntry } from "@/lib/api/types";
import { formatDateTime } from "@/i18n/formatting";
import {
  Alert,
  Card,
  CardBody,
  CardHeader,
  CardTitle,
  Empty,
  Skeleton,
} from "@/shared/ui";
import { cn } from "@/shared/utils";

/** UI activity kinds (mapped from API TimelineEvent + metadata). */
export type TimelineActivityType =
  | "CREATED"
  | "ASSIGNED"
  | "STATUS_CHANGED"
  | "PRIORITY_CHANGED"
  | "SLA"
  | "OTHER";

function isSlaEvent(eventType: string): boolean {
  return eventType.startsWith("sla.");
}

function activityType(entry: TimelineEntry): TimelineActivityType {
  const changeType =
    typeof entry.metadata?.changeType === "string"
      ? entry.metadata.changeType
      : null;

  if (isSlaEvent(entry.eventType) || changeType === "SLA_STATUS_CHANGED") {
    return "SLA";
  }
  if (changeType === "PRIORITY_CHANGED") return "PRIORITY_CHANGED";
  if (changeType === "STATUS_CHANGED" && entry.eventType === "complaint.updated") {
    return "STATUS_CHANGED";
  }

  switch (entry.eventType) {
    case "complaint.created":
      return "CREATED";
    case "complaint.assigned":
    case "complaint.reassigned":
      return "ASSIGNED";
    case "complaint.updated":
      if (entry.fromStatus && entry.toStatus && entry.fromStatus !== entry.toStatus) {
        return "STATUS_CHANGED";
      }
      return "OTHER";
    case "complaint.resolved":
    case "complaint.closed":
    case "escalation.closed":
    case "complaint.escalated":
    case "complaint.escalation_requested":
    case "complaint.escalation_approved":
    case "complaint.escalation_rejected":
    case "complaint.appointment_booked":
    case "complaint.appointment_checked_in":
    case "complaint.appointment_completed":
    case "complaint.appointment_no_show":
    case "complaint.final_resolution_submitted":
      return "STATUS_CHANGED";
    default:
      return "OTHER";
  }
}

function activityIcon(type: TimelineActivityType): string {
  switch (type) {
    case "CREATED":
      return "+";
    case "ASSIGNED":
      return "👤";
    case "STATUS_CHANGED":
      return "⇄";
    case "PRIORITY_CHANGED":
      return "!";
    case "SLA":
      return "⏱";
    default:
      return "•";
  }
}

function activityTypeLabelKey(type: TimelineActivityType): string {
  switch (type) {
    case "CREATED":
      return "activityTypeCreated";
    case "ASSIGNED":
      return "activityTypeAssigned";
    case "STATUS_CHANGED":
      return "activityTypeStatusChanged";
    case "PRIORITY_CHANGED":
      return "activityTypePriorityChanged";
    case "SLA":
      return "activityTypeSla";
    default:
      return "activityTypeOther";
  }
}

function slaSummaryKey(eventType: string): string | null {
  switch (eventType) {
    case "sla.assignment.breached":
      return "activitySlaAssignmentBreached";
    case "sla.appointment.breached":
      return "activitySlaAppointmentBreached";
    case "sla.escalation.breached":
      return "activitySlaEscalationBreached";
    case "sla.resolution.breached":
      return "activitySlaResolutionBreached";
    case "sla.assignment.completed":
      return "activitySlaAssignmentCompleted";
    case "sla.appointment.completed":
      return "activitySlaAppointmentCompleted";
    case "sla.escalation.completed":
      return "activitySlaEscalationCompleted";
    case "sla.resolution.completed":
      return "activitySlaResolutionCompleted";
    default:
      return null;
  }
}

export function TimelineCard({
  complaintId,
  refreshKey = 0,
}: {
  complaintId: string;
  refreshKey?: number;
}) {
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");
  const locale = useLocale();

  function activityMessage(entry: TimelineEntry): string {
    const type = activityType(entry);

    if (type === "SLA") {
      const slaKey = slaSummaryKey(entry.eventType);
      if (slaKey) return t(slaKey);
      return t("activitySlaChanged");
    }

    if (type === "CREATED") return t("activityCreated");
    if (type === "PRIORITY_CHANGED") return t("activityPriorityChanged");
    if (type === "STATUS_CHANGED") return t("activityStatusChanged");
    if (type === "ASSIGNED") {
      const assignee =
        typeof entry.metadata?.assigneeName === "string"
          ? entry.metadata.assigneeName.trim()
          : typeof entry.metadata?.toAssigneeName === "string"
            ? entry.metadata.toAssigneeName.trim()
            : "";
      if (assignee) return t("activityAssignedTo", { name: assignee });
      // Prefer localized label over English API summary ("Assigned to …").
      return t("activityAssigned");
    }

    return t("activityGeneric");
  }

  const [entries, setEntries] = useState<TimelineEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchComplaintTimeline(complaintId);
      // API returns newest-first; keep that order for the UI.
      setEntries(res.data);
    } catch (err) {
      setEntries([]);
      setError(
        err instanceof ApiError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("unableToLoadTimeline"),
      );
    } finally {
      setLoading(false);
    }
  }, [complaintId, t]);

  useEffect(() => {
    void load();
  }, [load, refreshKey]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("timelineCard")}</CardTitle>
      </CardHeader>
      <CardBody>
        {loading ? (
          <Skeleton rows={4} />
        ) : error ? (
          <Alert
            tone="danger"
            title={t("couldNotLoadTimeline")}
            description={error}
            actionLabel={tCommon("retry")}
            onAction={() => void load()}
          />
        ) : entries.length === 0 ? (
          <Empty title={t("timelineCard")} description={t("noActivityYet")} />
        ) : (
          <ol className="space-y-0" aria-label={t("timelineAriaLabel")}>
            {entries.map((entry, index) => {
              const type = activityType(entry);
              const isLast = index === entries.length - 1;
              return (
                <li key={entry.id} className="relative flex gap-3 pb-5 last:pb-0">
                  {!isLast ? (
                    <span
                      aria-hidden="true"
                      className="absolute left-[15px] top-8 bottom-0 w-px bg-ecmp-border"
                    />
                  ) : null}
                  <span
                    aria-hidden="true"
                    className={cn(
                      "relative z-[1] flex size-8 shrink-0 items-center justify-center rounded-full border border-ecmp-border bg-ecmp-surface text-sm font-semibold text-ecmp-text-primary",
                    )}
                    title={t(activityTypeLabelKey(type))}
                  >
                    {activityIcon(type)}
                  </span>
                  <div className="min-w-0 flex-1 space-y-1 border-b border-ecmp-border pb-5 last:border-b-0 last:pb-0">
                    <p className="text-[length:var(--ecmp-font-body-size)] font-medium text-ecmp-text-primary">
                      {activityMessage(entry)}
                    </p>
                    <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                      {entry.actorName?.trim() || t("systemActor")}
                    </p>
                    <p className="text-[length:var(--ecmp-font-caption-size)] text-ecmp-text-secondary">
                      <time dateTime={entry.eventAt || entry.createdAt}>
                        {formatDateTime(entry.eventAt || entry.createdAt, locale)}
                      </time>
                    </p>
                  </div>
                </li>
              );
            })}
          </ol>
        )}
      </CardBody>
    </Card>
  );
}
