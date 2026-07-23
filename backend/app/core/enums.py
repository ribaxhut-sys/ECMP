"""Global domain enums — single source of truth for complaint lifecycle."""

from __future__ import annotations

from enum import StrEnum


class ComplaintStatus(StrEnum):
    """Valid complaint lifecycle statuses (v1)."""

    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING = "PENDING"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


INITIAL_COMPLAINT_STATUS = ComplaintStatus.NEW


class TimelineEvent(StrEnum):
    """Allowed complaint timeline event names."""

    CREATED = "complaint.created"
    UPDATED = "complaint.updated"
    ASSIGNED = "complaint.assigned"
    REASSIGNED = "complaint.reassigned"
    ESCALATED = "complaint.escalated"
    ESCALATION_REQUESTED = "complaint.escalation_requested"
    ESCALATION_APPROVED = "complaint.escalation_approved"
    ESCALATION_REJECTED = "complaint.escalation_rejected"
    APPOINTMENT_BOOKED = "complaint.appointment_booked"
    APPOINTMENT_CHECKED_IN = "complaint.appointment_checked_in"
    APPOINTMENT_COMPLETED = "complaint.appointment_completed"
    APPOINTMENT_NO_SHOW = "complaint.appointment_no_show"
    FINAL_RESOLUTION_SUBMITTED = "complaint.final_resolution_submitted"
    RESOLVED = "complaint.resolved"
    CLOSED = "complaint.closed"


class FinalResolutionStatus(StrEnum):
    """Submission status for Final Resolution (TASK-018). Not a complaint status."""

    FINAL_RESOLUTION_SUBMITTED = "FINAL_RESOLUTION_SUBMITTED"


class EscalationRequestStatus(StrEnum):
    """Escalation Request lifecycle (TASK-011/012)."""

    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class AppointmentStatus(StrEnum):
    """Appointment lifecycle (book → check-in / no-show → complete)."""

    BOOKED = "BOOKED"
    CHECKED_IN = "CHECKED_IN"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class AppointmentCompletionResult(StrEnum):
    """Allowed completion results (TASK-016)."""

    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"


class EscalationReasonCode(StrEnum):
    """Minimum reason codes for Branch → HO Escalation Request."""

    SPECIALIST_REQUIRED = "SPECIALIST_REQUIRED"
    COMPLEX_CASE = "COMPLEX_CASE"
    POLICY_EXCEPTION = "POLICY_EXCEPTION"
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    OTHER = "OTHER"
