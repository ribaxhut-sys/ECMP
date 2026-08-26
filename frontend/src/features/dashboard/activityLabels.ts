import type { BadgeTone } from "@/shared/ui";

export type ActivityLabelKey =
  | "activityCreated"
  | "activityHandlingContinued"
  | "activityHandlingTakenOver"
  | "activityAssigned"
  | "activityReassigned"
  | "activityUpdated"
  | "activityResolved"
  | "activityClosed"
  | "activityEscalated"
  | "activityEscalationRequested"
  | "activityEscalationApproved"
  | "activityEscalationRejected"
  | "activityEscalationCancelled"
  | "activityHqAccepted"
  | "activityHqReturned"
  | "activityHqArrivalScheduled"
  | "activityCaseCreated"
  | "activityCaseStatusChanged"
  | "activityCaseCancelled"
  | "activityCaseEscalatedToPusat"
  | "activityCaseEscalationToPusatCancelled"
  | "activityCaseEscalationReturned"
  | "activityResolutionUpdated"
  | "activityHandlingUnitAccepted"
  | "activityOwnerAccepted"
  | "activityHandlingUnitRejected"
  | "activityOwnerRejected"
  | "activityAppointmentBooked"
  | "activityAppointmentCheckedIn"
  | "activityAppointmentCompleted"
  | "activityAppointmentNoShow"
  | "activityFinalResolution"
  | "activitySlaBreached"
  | "activitySlaCompleted"
  | "activityOther";

export type ActivityBadgeKey =
  | "activityBadgeNew"
  | "activityBadgeAssigned"
  | "activityBadgeUpdate"
  | "activityBadgeHandling"
  | "activityBadgeResolved"
  | "activityBadgeEscalation"
  | "activityBadgeAppointment"
  | "activityBadgeSla"
  | "activityBadgeOther";

type ActivityMeta = {
  labelKey: ActivityLabelKey;
  badgeKey: ActivityBadgeKey;
  statusTone: BadgeTone;
};

const EVENT_MAP: Record<string, ActivityMeta> = {
  "complaint.created": {
    labelKey: "activityCreated",
    badgeKey: "activityBadgeNew",
    statusTone: "info",
  },
  "complaint.handling_continued": {
    labelKey: "activityHandlingContinued",
    badgeKey: "activityBadgeHandling",
    statusTone: "primary",
  },
  "complaint.handling_taken_over": {
    labelKey: "activityHandlingTakenOver",
    badgeKey: "activityBadgeHandling",
    statusTone: "primary",
  },
  "complaint.assigned": {
    labelKey: "activityAssigned",
    badgeKey: "activityBadgeAssigned",
    statusTone: "primary",
  },
  "complaint.reassigned": {
    labelKey: "activityReassigned",
    badgeKey: "activityBadgeAssigned",
    statusTone: "primary",
  },
  "complaint.updated": {
    labelKey: "activityUpdated",
    badgeKey: "activityBadgeUpdate",
    statusTone: "neutral",
  },
  "complaint.resolved": {
    labelKey: "activityResolved",
    badgeKey: "activityBadgeResolved",
    statusTone: "success",
  },
  "complaint.closed": {
    labelKey: "activityClosed",
    badgeKey: "activityBadgeResolved",
    statusTone: "success",
  },
  "complaint.escalated": {
    labelKey: "activityEscalated",
    badgeKey: "activityBadgeEscalation",
    statusTone: "danger",
  },
  "complaint.escalation_requested": {
    labelKey: "activityEscalationRequested",
    badgeKey: "activityBadgeEscalation",
    statusTone: "warning",
  },
  "complaint.escalation_approved": {
    labelKey: "activityEscalationApproved",
    badgeKey: "activityBadgeEscalation",
    statusTone: "warning",
  },
  "complaint.escalation_rejected": {
    labelKey: "activityEscalationRejected",
    badgeKey: "activityBadgeEscalation",
    statusTone: "neutral",
  },
  "complaint.escalation_cancelled": {
    labelKey: "activityEscalationCancelled",
    badgeKey: "activityBadgeEscalation",
    statusTone: "neutral",
  },
  "complaint.hq_accepted": {
    labelKey: "activityHqAccepted",
    badgeKey: "activityBadgeAssigned",
    statusTone: "info",
  },
  "complaint.hq_returned": {
    labelKey: "activityHqReturned",
    badgeKey: "activityBadgeEscalation",
    statusTone: "warning",
  },
  "complaint.hq_arrival_scheduled": {
    labelKey: "activityHqArrivalScheduled",
    badgeKey: "activityBadgeAppointment",
    statusTone: "info",
  },
  "complaint.escalated_to_pusat": {
    labelKey: "activityCaseEscalatedToPusat",
    badgeKey: "activityBadgeEscalation",
    statusTone: "warning",
  },
  "complaint.escalation_to_pusat_cancelled": {
    labelKey: "activityCaseEscalationToPusatCancelled",
    badgeKey: "activityBadgeEscalation",
    statusTone: "neutral",
  },
  "complaint.escalation_returned": {
    labelKey: "activityCaseEscalationReturned",
    badgeKey: "activityBadgeEscalation",
    statusTone: "warning",
  },
  "complaint.case_created": {
    labelKey: "activityCaseCreated",
    badgeKey: "activityBadgeNew",
    statusTone: "primary",
  },
  "complaint.case_status_changed": {
    labelKey: "activityCaseStatusChanged",
    badgeKey: "activityBadgeUpdate",
    statusTone: "neutral",
  },
  "complaint.case_cancelled": {
    labelKey: "activityCaseCancelled",
    badgeKey: "activityBadgeOther",
    statusTone: "neutral",
  },
  "complaint.resolution_updated": {
    labelKey: "activityResolutionUpdated",
    badgeKey: "activityBadgeResolved",
    statusTone: "success",
  },
  "complaint.handling_unit_accepted": {
    labelKey: "activityHandlingUnitAccepted",
    badgeKey: "activityBadgeResolved",
    statusTone: "success",
  },
  "complaint.owner_accepted": {
    labelKey: "activityOwnerAccepted",
    badgeKey: "activityBadgeResolved",
    statusTone: "success",
  },
  "complaint.handling_unit_rejected": {
    labelKey: "activityHandlingUnitRejected",
    badgeKey: "activityBadgeEscalation",
    statusTone: "danger",
  },
  "complaint.owner_rejected": {
    labelKey: "activityOwnerRejected",
    badgeKey: "activityBadgeEscalation",
    statusTone: "danger",
  },
  "complaint.other": {
    labelKey: "activityOther",
    badgeKey: "activityBadgeOther",
    statusTone: "neutral",
  },
  "complaint.appointment_booked": {
    labelKey: "activityAppointmentBooked",
    badgeKey: "activityBadgeAppointment",
    statusTone: "info",
  },
  "complaint.appointment_checked_in": {
    labelKey: "activityAppointmentCheckedIn",
    badgeKey: "activityBadgeAppointment",
    statusTone: "info",
  },
  "complaint.appointment_completed": {
    labelKey: "activityAppointmentCompleted",
    badgeKey: "activityBadgeAppointment",
    statusTone: "success",
  },
  "complaint.appointment_no_show": {
    labelKey: "activityAppointmentNoShow",
    badgeKey: "activityBadgeAppointment",
    statusTone: "warning",
  },
  "complaint.final_resolution_submitted": {
    labelKey: "activityFinalResolution",
    badgeKey: "activityBadgeResolved",
    statusTone: "success",
  },
  "escalation.closed": {
    labelKey: "activityClosed",
    badgeKey: "activityBadgeResolved",
    statusTone: "success",
  },
  "sla.assignment.breached": {
    labelKey: "activitySlaBreached",
    badgeKey: "activityBadgeSla",
    statusTone: "danger",
  },
  "sla.appointment.breached": {
    labelKey: "activitySlaBreached",
    badgeKey: "activityBadgeSla",
    statusTone: "danger",
  },
  "sla.resolution.breached": {
    labelKey: "activitySlaBreached",
    badgeKey: "activityBadgeSla",
    statusTone: "danger",
  },
  "sla.escalation.breached": {
    labelKey: "activitySlaBreached",
    badgeKey: "activityBadgeSla",
    statusTone: "danger",
  },
  "sla.assignment.completed": {
    labelKey: "activitySlaCompleted",
    badgeKey: "activityBadgeSla",
    statusTone: "success",
  },
  "sla.appointment.completed": {
    labelKey: "activitySlaCompleted",
    badgeKey: "activityBadgeSla",
    statusTone: "success",
  },
  "sla.resolution.completed": {
    labelKey: "activitySlaCompleted",
    badgeKey: "activityBadgeSla",
    statusTone: "success",
  },
  "sla.escalation.completed": {
    labelKey: "activitySlaCompleted",
    badgeKey: "activityBadgeSla",
    statusTone: "success",
  },
};

export function resolveActivityMeta(eventType: string): ActivityMeta {
  if (EVENT_MAP[eventType]) return EVENT_MAP[eventType];
  if (eventType.startsWith("sla.") && eventType.includes("breached")) {
    return {
      labelKey: "activitySlaBreached",
      badgeKey: "activityBadgeSla",
      statusTone: "danger",
    };
  }
  if (eventType.startsWith("sla.")) {
    return {
      labelKey: "activitySlaCompleted",
      badgeKey: "activityBadgeSla",
      statusTone: "success",
    };
  }
  return {
    labelKey: "activityOther",
    badgeKey: "activityBadgeOther",
    statusTone: "neutral",
  };
}
