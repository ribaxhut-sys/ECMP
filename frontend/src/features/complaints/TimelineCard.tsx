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
  Timeline,
  type BadgeTone,
  type TimelineItem,
} from "@/shared/ui";

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

function activityTone(type: TimelineActivityType): BadgeTone {
  switch (type) {
    case "CREATED":
      return "info";
    case "ASSIGNED":
      return "primary";
    case "STATUS_CHANGED":
      return "warning";
    case "PRIORITY_CHANGED":
      return "warning";
    case "SLA":
      return "danger";
    default:
      return "neutral";
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
          <Empty
            title={t("noActivityYet")}
            description={t("timelineEmptyDescription")}
            primaryAction={{
              label: tCommon("refresh"),
              onClick: () => void load(),
            }}
          />
        ) : (
          <Timeline
            aria-label={t("timelineAriaLabel")}
            items={entries.map((entry): TimelineItem => {
              const type = activityType(entry);
              const when = entry.eventAt || entry.createdAt;
              return {
                id: entry.id,
                title: activityMessage(entry),
                actor: entry.actorName?.trim() || t("systemActor"),
                time: (
                  <time dateTime={when}>{formatDateTime(when, locale)}</time>
                ),
                status: t(activityTypeLabelKey(type)),
                statusTone: activityTone(type),
                icon: (
                  <span
                    className="text-[length:var(--ecmp-font-caption-size)] font-[number:var(--ecmp-font-section-title-weight)]"
                    aria-hidden
                  >
                    {activityIcon(type)}
                  </span>
                ),
              };
            })}
          />
        )}
      </CardBody>
    </Card>
  );
}
