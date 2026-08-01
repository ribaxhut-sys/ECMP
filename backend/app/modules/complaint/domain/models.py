"""Complaint Domain — Aggregate Root + Resolution VO + Assignment + Escalation + SLA.

CAPABILITY-004…008. Persistence-independent — no SQLAlchemy, no ORM, no
repository imports. No Queue domain imports — only ``queue_ticket_id`` as a
visit-context reference. No Workflow / Auth / Timeline / Notification.
Assignment, Escalation, and ComplaintSLA are child entities; none change
Complaint status. Escalation determines handling level only. SLA calculates
due/remaining/breach only — no scheduler, notification, or auto-escalation.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from app.modules.complaint.domain.errors import ComplaintDomainError
from app.core.user_messages import m


class ComplaintStatus(StrEnum):
    """Complaint processing lifecycle statuses."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class ComplaintPriority(StrEnum):
    """Complaint priority classes."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    URGENT = "URGENT"


class AssigneeType(StrEnum):
    """Who an assignment targets. CAPABILITY-006 implements USER only.

    TEAM / QUEUE / SYSTEM are reserved for future capabilities (design-ready).
    """

    USER = "USER"
    TEAM = "TEAM"
    QUEUE = "QUEUE"
    SYSTEM = "SYSTEM"


# CAPABILITY-006 — only USER is permitted for assign/reassign today.
_SUPPORTED_ASSIGNEE_TYPES = frozenset({AssigneeType.USER})


class EscalationLevel(StrEnum):
    """Handling level for Complaint Escalation (CAPABILITY-007)."""

    LEVEL_1 = "LEVEL_1"
    LEVEL_2 = "LEVEL_2"
    LEVEL_3 = "LEVEL_3"
    LEVEL_4 = "LEVEL_4"


_ESCALATION_LEVEL_RANK: Mapping[EscalationLevel, int] = MappingProxyType(
    {
        EscalationLevel.LEVEL_1: 1,
        EscalationLevel.LEVEL_2: 2,
        EscalationLevel.LEVEL_3: 3,
        EscalationLevel.LEVEL_4: 4,
    }
)


def _require_non_empty(value: str, field_name: str) -> str:
    token = (value or "").strip()
    if not token:
        raise ValueError(f"{field_name} must be a non-empty string")
    return token


def _require_uuid(value: uuid.UUID, field_name: str) -> uuid.UUID:
    if not isinstance(value, uuid.UUID):
        raise TypeError(f"{field_name} must be uuid.UUID, got {type(value).__name__}")
    return value


def _ensure_utc(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be datetime, got {type(value).__name__}")
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _now_utc(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    return _ensure_utc(now, "now")


@dataclass(frozen=True, slots=True)
class Resolution:
    """Value object — captured only when a complaint becomes RESOLVED."""

    summary: str
    resolved_by: str
    resolved_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "summary", _require_non_empty(self.summary, "summary")
        )
        object.__setattr__(
            self, "resolved_by", _require_non_empty(self.resolved_by, "resolved_by")
        )
        object.__setattr__(
            self, "resolved_at", _ensure_utc(self.resolved_at, "resolved_at")
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "summary": self.summary,
                "resolvedBy": self.resolved_by,
                "resolvedAt": self.resolved_at.isoformat(),
            }
        )


@dataclass(frozen=True, slots=True)
class Assignment:
    """Child entity of Complaint — responsibility only; append-only history.

    At most one Assignment may be ``is_active=True`` per Complaint (Rule 1).
    Reassignment releases the prior row and appends a new active row (Rule 3).
    Assignment never mutates Complaint lifecycle status (Rule 6).
    """

    assignment_id: uuid.UUID
    complaint_id: uuid.UUID
    assignee_type: AssigneeType
    assignee_id: str
    assigned_at: datetime
    assigned_by: str
    released_at: datetime | None = None
    release_reason: str | None = None
    is_active: bool = True

    def __post_init__(self) -> None:
        _require_uuid(self.assignment_id, "assignment_id")
        _require_uuid(self.complaint_id, "complaint_id")
        if not isinstance(self.assignee_type, AssigneeType):
            raise TypeError(
                f"assignee_type must be AssigneeType, got {type(self.assignee_type).__name__}"
            )
        object.__setattr__(
            self, "assignee_id", _require_non_empty(self.assignee_id, "assignee_id")
        )
        object.__setattr__(
            self, "assigned_by", _require_non_empty(self.assigned_by, "assigned_by")
        )
        object.__setattr__(
            self, "assigned_at", _ensure_utc(self.assigned_at, "assigned_at")
        )
        if self.released_at is not None:
            object.__setattr__(
                self, "released_at", _ensure_utc(self.released_at, "released_at")
            )
        if self.release_reason is not None:
            cleaned = self.release_reason.strip()
            object.__setattr__(
                self, "release_reason", cleaned if cleaned else None
            )
        if self.is_active and self.released_at is not None:
            raise ComplaintDomainError(
                "INVALID_ASSIGNMENT_STATE",
                m("assignment.active_cannot_have_released_at"),
            )
        if not self.is_active and self.released_at is None:
            raise ComplaintDomainError(
                "INVALID_ASSIGNMENT_STATE",
                m("assignment.inactive_requires_released_at"),
            )

    def release(
        self,
        *,
        reason: str | None = None,
        now: datetime | None = None,
    ) -> Assignment:
        """Mark this assignment inactive (Rule 5). Does not mutate history fields."""
        if not self.is_active:
            raise ComplaintDomainError(
                "NO_ACTIVE_ASSIGNMENT",
                m("assignment.already_inactive"),
            )
        stamp = _now_utc(now)
        cleaned: str | None = None
        if reason is not None:
            token = reason.strip()
            cleaned = token if token else None
        return replace(
            self,
            is_active=False,
            released_at=stamp,
            release_reason=cleaned,
        )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "assignmentId": str(self.assignment_id),
                "complaintId": str(self.complaint_id),
                "assigneeType": self.assignee_type.value,
                "assigneeId": self.assignee_id,
                "assignedAt": self.assigned_at.isoformat(),
                "assignedBy": self.assigned_by,
                "releasedAt": (
                    None if self.released_at is None else self.released_at.isoformat()
                ),
                "releaseReason": self.release_reason,
                "isActive": self.is_active,
            }
        )


@dataclass(frozen=True, slots=True)
class Escalation:
    """Child entity of Complaint — handling level only; append-only history.

    At most one Escalation may be ``is_current=True`` per Complaint (Rule 2–3).
    Escalation never mutates Complaint lifecycle status (Rule 6) or Assignment
    (Rule 5). Level may only increase (Rule 7).
    """

    escalation_id: uuid.UUID
    complaint_id: uuid.UUID
    level: EscalationLevel
    reason: str
    escalated_by: str
    escalated_at: datetime
    released_at: datetime | None = None
    is_current: bool = True

    def __post_init__(self) -> None:
        _require_uuid(self.escalation_id, "escalation_id")
        _require_uuid(self.complaint_id, "complaint_id")
        if not isinstance(self.level, EscalationLevel):
            raise TypeError(
                f"level must be EscalationLevel, got {type(self.level).__name__}"
            )
        object.__setattr__(self, "reason", _require_non_empty(self.reason, "reason"))
        object.__setattr__(
            self, "escalated_by", _require_non_empty(self.escalated_by, "escalated_by")
        )
        object.__setattr__(
            self, "escalated_at", _ensure_utc(self.escalated_at, "escalated_at")
        )
        if self.released_at is not None:
            object.__setattr__(
                self, "released_at", _ensure_utc(self.released_at, "released_at")
            )
        if self.is_current and self.released_at is not None:
            raise ComplaintDomainError(
                "INVALID_ESCALATION_STATE",
                m("escalation.current_cannot_have_released_at"),
            )
        if not self.is_current and self.released_at is None:
            raise ComplaintDomainError(
                "INVALID_ESCALATION_STATE",
                m("escalation.historical_requires_released_at"),
            )

    def release(self, *, now: datetime | None = None) -> Escalation:
        """Mark this escalation historical (Rule 3). Does not rewrite level/reason."""
        if not self.is_current:
            raise ComplaintDomainError(
                "NO_CURRENT_ESCALATION",
                m("escalation.already_historical"),
            )
        stamp = _now_utc(now)
        return replace(self, is_current=False, released_at=stamp)

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "escalationId": str(self.escalation_id),
                "complaintId": str(self.complaint_id),
                "level": self.level.value,
                "reason": self.reason,
                "escalatedBy": self.escalated_by,
                "escalatedAt": self.escalated_at.isoformat(),
                "releasedAt": (
                    None if self.released_at is None else self.released_at.isoformat()
                ),
                "isCurrent": self.is_current,
            }
        )


@dataclass(frozen=True, slots=True)
class SLAPolicy:
    """SLA target configuration. Shared by many Complaints (CAPABILITY-008)."""

    policy_id: uuid.UUID
    name: str
    target_minutes: int
    is_default: bool = False
    description: str | None = None

    def __post_init__(self) -> None:
        _require_uuid(self.policy_id, "policy_id")
        object.__setattr__(self, "name", _require_non_empty(self.name, "name"))
        if not isinstance(self.target_minutes, int):
            raise TypeError(
                f"target_minutes must be int, got {type(self.target_minutes).__name__}"
            )
        if self.target_minutes <= 0:
            raise ComplaintDomainError(
                "VALIDATION_ERROR",
                m("sla.target_minutes_positive"),
            )
        if self.description is not None:
            cleaned = self.description.strip()
            object.__setattr__(
                self, "description", cleaned if cleaned else None
            )

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "policyId": str(self.policy_id),
                "name": self.name,
                "targetMinutes": self.target_minutes,
                "isDefault": self.is_default,
                "description": self.description,
            }
        )


@dataclass(frozen=True, slots=True)
class ComplaintSLA:
    """Child entity of Complaint — due-time / remaining / breach only.

    At most one ComplaintSLA may be ``is_active=True`` per Complaint (Rule 1).
    SLA never mutates Complaint status (Rule 6), never creates Escalation
    (Rule 7), and never sends Notification (Rule 8).
    """

    sla_id: uuid.UUID
    complaint_id: uuid.UUID
    policy_id: uuid.UUID
    started_at: datetime
    due_at: datetime
    completed_at: datetime | None = None
    breached_at: datetime | None = None
    is_active: bool = True
    is_breached: bool = False

    def __post_init__(self) -> None:
        _require_uuid(self.sla_id, "sla_id")
        _require_uuid(self.complaint_id, "complaint_id")
        _require_uuid(self.policy_id, "policy_id")
        object.__setattr__(
            self, "started_at", _ensure_utc(self.started_at, "started_at")
        )
        object.__setattr__(self, "due_at", _ensure_utc(self.due_at, "due_at"))
        if self.completed_at is not None:
            object.__setattr__(
                self, "completed_at", _ensure_utc(self.completed_at, "completed_at")
            )
        if self.breached_at is not None:
            object.__setattr__(
                self, "breached_at", _ensure_utc(self.breached_at, "breached_at")
            )
        if self.is_active and self.completed_at is not None:
            raise ComplaintDomainError(
                "INVALID_SLA_STATE",
                m("sla.active_cannot_have_completed_at"),
            )
        if not self.is_active and self.completed_at is None:
            raise ComplaintDomainError(
                "INVALID_SLA_STATE",
                m("sla.inactive_requires_completed_at"),
            )
        if self.is_breached and self.breached_at is None:
            raise ComplaintDomainError(
                "INVALID_SLA_STATE",
                m("sla.breached_requires_breached_at"),
            )
        if not self.is_breached and self.breached_at is not None:
            raise ComplaintDomainError(
                "INVALID_SLA_STATE",
                m("sla.non_breached_cannot_have_breached_at"),
            )

    def remaining_minutes(self, *, current_time: datetime | None = None) -> int:
        """Minutes until due (negative when overdue). Completed SLA → 0."""
        if not self.is_active:
            return 0
        stamp = _now_utc(current_time)
        delta = self.due_at - stamp
        return int(delta.total_seconds() // 60)

    def detect_breach(self, *, current_time: datetime | None = None) -> ComplaintSLA:
        """Rule 5 — if current_time > due_at, mark breached once."""
        if not self.is_active:
            return self
        stamp = _now_utc(current_time)
        if stamp <= self.due_at:
            return self
        if self.is_breached:
            return self
        return replace(self, is_breached=True, breached_at=stamp)

    def complete(self, *, now: datetime | None = None) -> ComplaintSLA:
        """Mark SLA inactive with completed_at (Rule 4 companion)."""
        if not self.is_active:
            raise ComplaintDomainError(
                "NO_ACTIVE_SLA",
                m("sla.already_inactive"),
            )
        stamp = _now_utc(now)
        return replace(self, is_active=False, completed_at=stamp)

    def as_dict(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "slaId": str(self.sla_id),
                "complaintId": str(self.complaint_id),
                "policyId": str(self.policy_id),
                "startedAt": self.started_at.isoformat(),
                "dueAt": self.due_at.isoformat(),
                "completedAt": (
                    None
                    if self.completed_at is None
                    else self.completed_at.isoformat()
                ),
                "breachedAt": (
                    None if self.breached_at is None else self.breached_at.isoformat()
                ),
                "isActive": self.is_active,
                "isBreached": self.is_breached,
            }
        )


@dataclass(frozen=True, slots=True)
class Complaint:
    """Complaint aggregate root. Visit context via ``queue_ticket_id`` only."""

    complaint_id: uuid.UUID
    organization_id: uuid.UUID
    branch_id: uuid.UUID
    queue_ticket_id: uuid.UUID
    category: str
    title: str
    description: str
    priority: ComplaintPriority
    status: ComplaintStatus
    created_at: datetime
    updated_at: datetime
    resolution: Resolution | None = None

    def __post_init__(self) -> None:
        _require_uuid(self.complaint_id, "complaint_id")
        _require_uuid(self.organization_id, "organization_id")
        _require_uuid(self.branch_id, "branch_id")
        _require_uuid(self.queue_ticket_id, "queue_ticket_id")
        object.__setattr__(
            self, "category", _require_non_empty(self.category, "category")
        )
        object.__setattr__(self, "title", _require_non_empty(self.title, "title"))
        object.__setattr__(
            self, "description", _require_non_empty(self.description, "description")
        )
        if not isinstance(self.priority, ComplaintPriority):
            raise TypeError(
                f"priority must be ComplaintPriority, got {type(self.priority).__name__}"
            )
        if not isinstance(self.status, ComplaintStatus):
            raise TypeError(
                f"status must be ComplaintStatus, got {type(self.status).__name__}"
            )
        if self.resolution is not None and not isinstance(self.resolution, Resolution):
            raise TypeError(
                f"resolution must be Resolution | None, got {type(self.resolution).__name__}"
            )
        if self.resolution is not None and self.status is not ComplaintStatus.RESOLVED:
            # CLOSED may retain an immutable resolution snapshot.
            if self.status is not ComplaintStatus.CLOSED:
                raise ComplaintDomainError(
                    "INVALID_RESOLUTION_STATE",
                    m("resolution.only_when_resolved_or_closed"),
                )
        object.__setattr__(self, "created_at", _ensure_utc(self.created_at, "created_at"))
        object.__setattr__(self, "updated_at", _ensure_utc(self.updated_at, "updated_at"))

    def start_processing(self, *, now: datetime | None = None) -> Complaint:
        """OPEN → IN_PROGRESS."""
        from app.modules.complaint.domain.lifecycle import assert_transition

        assert_transition(self.status, ComplaintStatus.IN_PROGRESS)
        stamp = _now_utc(now)
        return replace(
            self,
            status=ComplaintStatus.IN_PROGRESS,
            updated_at=stamp,
        )

    def resolve(
        self,
        summary: str,
        resolved_by: str,
        *,
        now: datetime | None = None,
    ) -> Complaint:
        """IN_PROGRESS → RESOLVED with a Resolution value object."""
        from app.modules.complaint.domain.lifecycle import assert_transition

        assert_transition(self.status, ComplaintStatus.RESOLVED)
        stamp = _now_utc(now)
        try:
            resolution = Resolution(
                summary=summary,
                resolved_by=resolved_by,
                resolved_at=stamp,
            )
        except ValueError as exc:
            raise ComplaintDomainError("VALIDATION_ERROR", str(exc)) from exc
        return replace(
            self,
            status=ComplaintStatus.RESOLVED,
            resolution=resolution,
            updated_at=stamp,
        )

    def close(self, *, now: datetime | None = None) -> Complaint:
        """RESOLVED → CLOSED. Resolution becomes immutable."""
        from app.modules.complaint.domain.lifecycle import assert_transition

        assert_transition(self.status, ComplaintStatus.CLOSED)
        stamp = _now_utc(now)
        return replace(
            self,
            status=ComplaintStatus.CLOSED,
            updated_at=stamp,
        )

    def reopen(
        self,
        *,
        reason: str | None = None,
        now: datetime | None = None,
    ) -> Complaint:
        """RESOLVED → IN_PROGRESS. Clears resolution so a new resolve may be recorded.

        ``reason`` is accepted for API/contract completeness but is not persisted
        (Timeline is out of scope for CAPABILITY-005).
        """
        from app.modules.complaint.domain.lifecycle import assert_transition

        _ = reason
        if self.status is not ComplaintStatus.RESOLVED:
            raise ComplaintDomainError(
                "INVALID_COMPLAINT_TRANSITION",
                f"reopen memerlukan status RESOLVED, saat ini {self.status.value}",
            )
        assert_transition(self.status, ComplaintStatus.IN_PROGRESS)
        stamp = _now_utc(now)
        return replace(
            self,
            status=ComplaintStatus.IN_PROGRESS,
            resolution=None,
            updated_at=stamp,
        )

    def assert_resolution_mutable(self) -> None:
        """Raise when resolution must not change (CLOSED)."""
        if self.status is ComplaintStatus.CLOSED:
            raise ComplaintDomainError(
                "RESOLUTION_IMMUTABLE",
                m("resolution.cannot_change_after_closed"),
            )

    def assign(
        self,
        *,
        assignee_type: AssigneeType,
        assignee_id: str,
        assigned_by: str,
        active: Assignment | None,
        assignment_id: uuid.UUID | None = None,
        now: datetime | None = None,
    ) -> Assignment:
        """First assign — create an active Assignment (Rule 2).

        Rejects when an active assignment already exists (Rule 1).
        Does not change Complaint status (Rule 6).
        """
        if active is not None and active.is_active:
            raise ComplaintDomainError(
                "ACTIVE_ASSIGNMENT_EXISTS",
                m("assignment.already_has_active"),
            )
        return self._new_active_assignment(
            assignee_type=assignee_type,
            assignee_id=assignee_id,
            assigned_by=assigned_by,
            assignment_id=assignment_id,
            now=now,
        )

    def reassign(
        self,
        *,
        assignee_type: AssigneeType,
        assignee_id: str,
        assigned_by: str,
        active: Assignment | None,
        assignment_id: uuid.UUID | None = None,
        now: datetime | None = None,
    ) -> tuple[Assignment, Assignment]:
        """Release active assignment and append a new active one (Rule 3).

        History rows are not rewritten — prior assignee/assigned_at stay intact.
        Does not change Complaint status (Rule 6).
        """
        if active is None or not active.is_active:
            raise ComplaintDomainError(
                "NO_ACTIVE_ASSIGNMENT",
                m("assignment.no_active_to_reassign"),
            )
        if active.complaint_id != self.complaint_id:
            raise ComplaintDomainError(
                "VALIDATION_ERROR",
                m("assignment.active_not_belong_complaint"),
            )
        stamp = _now_utc(now)
        released = active.release(reason="reassigned", now=stamp)
        created = self._new_active_assignment(
            assignee_type=assignee_type,
            assignee_id=assignee_id,
            assigned_by=assigned_by,
            assignment_id=assignment_id,
            now=stamp,
        )
        return released, created

    def unassign(
        self,
        *,
        active: Assignment | None,
        reason: str | None = None,
        now: datetime | None = None,
    ) -> Assignment:
        """Release the active assignment; complaint has no assignee (Rule 5).

        Does not change Complaint status (Rule 6).
        """
        if active is None or not active.is_active:
            raise ComplaintDomainError(
                "NO_ACTIVE_ASSIGNMENT",
                m("assignment.no_active_to_unassign"),
            )
        if active.complaint_id != self.complaint_id:
            raise ComplaintDomainError(
                "VALIDATION_ERROR",
                m("assignment.active_not_belong_complaint"),
            )
        return active.release(reason=reason, now=now)

    def _new_active_assignment(
        self,
        *,
        assignee_type: AssigneeType,
        assignee_id: str,
        assigned_by: str,
        assignment_id: uuid.UUID | None,
        now: datetime | None,
    ) -> Assignment:
        if assignee_type not in _SUPPORTED_ASSIGNEE_TYPES:
            raise ComplaintDomainError(
                "UNSUPPORTED_ASSIGNEE_TYPE",
                f"tipe assignee {assignee_type.value} belum didukung",
            )
        stamp = _now_utc(now)
        try:
            return Assignment(
                assignment_id=assignment_id or uuid.uuid4(),
                complaint_id=self.complaint_id,
                assignee_type=assignee_type,
                assignee_id=assignee_id,
                assigned_at=stamp,
                assigned_by=assigned_by,
                released_at=None,
                release_reason=None,
                is_active=True,
            )
        except (TypeError, ValueError) as exc:
            raise ComplaintDomainError("VALIDATION_ERROR", str(exc)) from exc

    def escalate(
        self,
        *,
        level: EscalationLevel,
        reason: str,
        escalated_by: str,
        current: Escalation | None,
        escalation_id: uuid.UUID | None = None,
        now: datetime | None = None,
    ) -> tuple[Escalation | None, Escalation]:
        """Append a new current Escalation; prior current becomes historical.

        New complaints have no escalation (Rule 1). The new row becomes current
        (Rule 2); previous current is released (Rule 3). History is append-only
        (Rule 4). Does not change Assignment (Rule 5) or Complaint status
        (Rule 6). Level must strictly increase when a current escalation exists
        (Rule 7).
        """
        if not isinstance(level, EscalationLevel):
            raise TypeError(
                f"level must be EscalationLevel, got {type(level).__name__}"
            )
        stamp = _now_utc(now)
        released: Escalation | None = None
        if current is not None:
            if not current.is_current:
                raise ComplaintDomainError(
                    "NO_CURRENT_ESCALATION",
                    m("escalation.not_current"),
                )
            if current.complaint_id != self.complaint_id:
                raise ComplaintDomainError(
                    "VALIDATION_ERROR",
                    m("escalation.current_not_belong_complaint"),
                )
            if _ESCALATION_LEVEL_RANK[level] <= _ESCALATION_LEVEL_RANK[current.level]:
                raise ComplaintDomainError(
                    "ESCALATION_LEVEL_REGRESSION",
                    (
                        f"cannot escalate from {current.level.value} "
                        f"to {level.value}; level must increase"
                    ),
                )
            released = current.release(now=stamp)
        created = self._new_current_escalation(
            level=level,
            reason=reason,
            escalated_by=escalated_by,
            escalation_id=escalation_id,
            now=stamp,
        )
        return released, created

    def _new_current_escalation(
        self,
        *,
        level: EscalationLevel,
        reason: str,
        escalated_by: str,
        escalation_id: uuid.UUID | None,
        now: datetime | None,
    ) -> Escalation:
        stamp = _now_utc(now)
        try:
            return Escalation(
                escalation_id=escalation_id or uuid.uuid4(),
                complaint_id=self.complaint_id,
                level=level,
                reason=reason,
                escalated_by=escalated_by,
                escalated_at=stamp,
                released_at=None,
                is_current=True,
            )
        except (TypeError, ValueError) as exc:
            raise ComplaintDomainError("VALIDATION_ERROR", str(exc)) from exc

    def start_sla(
        self,
        *,
        policy: SLAPolicy,
        active: ComplaintSLA | None,
        sla_id: uuid.UUID | None = None,
        now: datetime | None = None,
    ) -> ComplaintSLA:
        """Start SLA from SLAPolicy (Rules 1–3). Does not change status (Rule 6)."""
        if not isinstance(policy, SLAPolicy):
            raise TypeError(f"policy must be SLAPolicy, got {type(policy).__name__}")
        if active is not None and active.is_active:
            raise ComplaintDomainError(
                "ACTIVE_SLA_EXISTS",
                m("sla.already_has_active"),
            )
        if self.status is ComplaintStatus.CLOSED:
            raise ComplaintDomainError(
                "INVALID_SLA_STATE",
                m("sla.cannot_start_on_closed"),
            )
        stamp = _now_utc(now)
        due_at = stamp + timedelta(minutes=policy.target_minutes)
        try:
            return ComplaintSLA(
                sla_id=sla_id or uuid.uuid4(),
                complaint_id=self.complaint_id,
                policy_id=policy.policy_id,
                started_at=stamp,
                due_at=due_at,
                completed_at=None,
                breached_at=None,
                is_active=True,
                is_breached=False,
            )
        except (TypeError, ValueError) as exc:
            raise ComplaintDomainError("VALIDATION_ERROR", str(exc)) from exc

    def complete_sla(
        self,
        *,
        active: ComplaintSLA | None,
        now: datetime | None = None,
    ) -> ComplaintSLA:
        """Complete active SLA (Rule 4 companion). Does not change status (Rule 6)."""
        if active is None or not active.is_active:
            raise ComplaintDomainError(
                "NO_ACTIVE_SLA",
                m("sla.no_active_to_complete"),
            )
        if active.complaint_id != self.complaint_id:
            raise ComplaintDomainError(
                "VALIDATION_ERROR",
                m("sla.active_not_belong_complaint"),
            )
        return active.complete(now=now)

    def as_dict(self) -> Mapping[str, object]:
        """Diagnostic serialization (not an HTTP / persistence contract)."""
        payload: dict[str, object] = {
            "complaintId": str(self.complaint_id),
            "organizationId": str(self.organization_id),
            "branchId": str(self.branch_id),
            "queueTicketId": str(self.queue_ticket_id),
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "resolution": None if self.resolution is None else dict(self.resolution.as_dict()),
        }
        return MappingProxyType(payload)


__all__ = [
    "AssigneeType",
    "Assignment",
    "Complaint",
    "ComplaintPriority",
    "ComplaintSLA",
    "ComplaintStatus",
    "Escalation",
    "EscalationLevel",
    "Resolution",
    "SLAPolicy",
]
