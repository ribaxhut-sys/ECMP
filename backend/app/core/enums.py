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


class ComplaintSourceType(StrEnum):
    """Who originated the complaint (TASK-042 / DEC-018).

    Stored as VARCHAR — new values (e.g. VENDOR) can be added in code
    without a schema migration.
    """

    CUSTOMER = "CUSTOMER"
    BRANCH = "BRANCH"
    HEAD_OFFICE = "HEAD_OFFICE"
    SYSTEM = "SYSTEM"


class ComplaintTargetType(StrEnum):
    """Where the complaint is directed (TASK-042 / DEC-018).

    Stored as VARCHAR — new values (e.g. REGIONAL) can be added in code
    without a schema migration.
    """

    BRANCH = "BRANCH"
    HEAD_OFFICE = "HEAD_OFFICE"


class ComplaintReceiverType(StrEnum):
    """Initial receiver resolved by Complaint Routing (TASK-043).

    Distinct from Assignment assignee — this is the organizational destination
    of the complaint, not a user.
    """

    BRANCH = "BRANCH"
    HEAD_OFFICE = "HEAD_OFFICE"


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
    ESCALATION_CLOSED = "escalation.closed"
    # TASK-025 / DEC-014 — SLA status transitions (SYSTEM actor)
    SLA_ASSIGNMENT_COMPLETED = "sla.assignment.completed"
    SLA_ASSIGNMENT_BREACHED = "sla.assignment.breached"
    SLA_APPOINTMENT_COMPLETED = "sla.appointment.completed"
    SLA_APPOINTMENT_BREACHED = "sla.appointment.breached"
    SLA_RESOLUTION_COMPLETED = "sla.resolution.completed"
    SLA_RESOLUTION_BREACHED = "sla.resolution.breached"
    SLA_ESCALATION_COMPLETED = "sla.escalation.completed"
    SLA_ESCALATION_BREACHED = "sla.escalation.breached"
    SLA_OVERALL_COMPLETED = "sla.overall.completed"
    SLA_OVERALL_BREACHED = "sla.overall.breached"


class FinalResolutionStatus(StrEnum):
    """Submission status for Final Resolution (TASK-018). Not a complaint status."""

    FINAL_RESOLUTION_SUBMITTED = "FINAL_RESOLUTION_SUBMITTED"


class EscalationRequestStatus(StrEnum):
    """Escalation Request lifecycle (TASK-011/012/020)."""

    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


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


class SlaStatus(StrEnum):
    """SLA dimension status (PENDING / COMPLETED / BREACHED; ON_TIME reserved)."""

    PENDING = "PENDING"
    ON_TIME = "ON_TIME"
    BREACHED = "BREACHED"
    COMPLETED = "COMPLETED"


class SettingVisibility(StrEnum):
    """System setting visibility (TASK-028)."""

    PUBLIC = "PUBLIC"
    PROTECTED = "PROTECTED"


class SettingValueType(StrEnum):
    """System setting value types (TASK-028)."""

    STRING = "STRING"
    INTEGER = "INTEGER"
    BOOLEAN = "BOOLEAN"
    JSON = "JSON"
    URL = "URL"
    EMAIL = "EMAIL"


class NotificationChannel(StrEnum):
    """Notification delivery channel (TASK-030). Provider delivery is out of scope."""

    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    PUSH = "PUSH"


class NotificationQueueStatus(StrEnum):
    """Notification queue lifecycle (TASK-030). No send worker in this task."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class AuditAction(StrEnum):
    """Platform audit actions (TASK-031)."""

    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
