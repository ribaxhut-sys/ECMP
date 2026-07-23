"""Escalation persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Appointment,
    Complaint,
    ComplaintAssignment,
    ComplaintEscalation,
    ComplaintResolution,
    ComplaintTimeline,
    Role,
    User,
)
from app.core.enums import AppointmentStatus

# Active = blocks a new Escalation Request. REQUESTED pending review;
# APPROVED awaiting / with appointment; legacy OPEN.
# REJECTED does not block a new request.
ACTIVE_ESCALATION_STATUSES = frozenset({"REQUESTED", "OPEN", "APPROVED"})
CURRENT_APPOINTMENT_STATUSES = frozenset(
    {
        AppointmentStatus.BOOKED,
        AppointmentStatus.CHECKED_IN,
        AppointmentStatus.COMPLETED,
        AppointmentStatus.NO_SHOW,
    }
)


class EscalationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_complaint(self, complaint_id: uuid.UUID) -> Complaint | None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def get_by_id(self, escalation_id: uuid.UUID) -> ComplaintEscalation | None:
        stmt = (
            select(ComplaintEscalation)
            .options(
                joinedload(ComplaintEscalation.requester),
                joinedload(ComplaintEscalation.reviewer),
            )
            .where(
                ComplaintEscalation.id == escalation_id,
                ComplaintEscalation.deleted_at.is_(None),
            )
        )
        return self._session.scalar(stmt)

    def get_active_appointment(
        self, escalation_id: uuid.UUID
    ) -> Appointment | None:
        stmt = (
            select(Appointment)
            .options(joinedload(Appointment.assigned_engineer))
            .where(
                Appointment.escalation_id == escalation_id,
                Appointment.deleted_at.is_(None),
                Appointment.status.in_(CURRENT_APPOINTMENT_STATUSES),
            )
            .order_by(Appointment.created_at.desc())
        )
        return self._session.scalar(stmt)

    def user_exists(self, user_id: uuid.UUID) -> bool:
        stmt = select(User.id).where(
            User.id == user_id,
            User.deleted_at.is_(None),
            User.is_active.is_(True),
        )
        return self._session.scalar(stmt) is not None

    def get_user(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
            User.is_active.is_(True),
        )
        return self._session.scalar(stmt)

    def role_exists(self, role_id: uuid.UUID) -> bool:
        stmt = select(Role.id).where(
            Role.id == role_id,
            Role.deleted_at.is_(None),
            Role.is_active.is_(True),
        )
        return self._session.scalar(stmt) is not None

    def get_current_assignee_id(self, complaint_id: uuid.UUID) -> uuid.UUID | None:
        stmt = select(ComplaintAssignment.assignee_id).where(
            ComplaintAssignment.complaint_id == complaint_id,
            ComplaintAssignment.is_current.is_(True),
            ComplaintAssignment.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def has_current_resolution(self, complaint_id: uuid.UUID) -> bool:
        stmt = select(ComplaintResolution.id).where(
            ComplaintResolution.complaint_id == complaint_id,
            ComplaintResolution.is_current.is_(True),
            ComplaintResolution.deleted_at.is_(None),
        )
        return self._session.scalar(stmt) is not None

    def get_final_resolution(
        self, complaint_id: uuid.UUID
    ) -> ComplaintResolution | None:
        """Return the resolution row that has Final Resolution submitted."""
        stmt = (
            select(ComplaintResolution)
            .where(
                ComplaintResolution.complaint_id == complaint_id,
                ComplaintResolution.final_resolution_at.is_not(None),
                ComplaintResolution.deleted_at.is_(None),
            )
            .order_by(ComplaintResolution.final_resolution_at.desc())
        )
        return self._session.scalar(stmt)

    def get_active_escalation(
        self, complaint_id: uuid.UUID
    ) -> ComplaintEscalation | None:
        stmt = (
            select(ComplaintEscalation)
            .options(
                joinedload(ComplaintEscalation.requester),
                joinedload(ComplaintEscalation.reviewer),
            )
            .where(
                ComplaintEscalation.complaint_id == complaint_id,
                ComplaintEscalation.deleted_at.is_(None),
                ComplaintEscalation.status.in_(ACTIVE_ESCALATION_STATUSES),
            )
            .order_by(ComplaintEscalation.created_at.desc())
        )
        return self._session.scalar(stmt)

    def get_latest_request_escalation(
        self, complaint_id: uuid.UUID
    ) -> ComplaintEscalation | None:
        """Latest Branch→HO request row (REQUESTED / APPROVED / REJECTED)."""
        stmt = (
            select(ComplaintEscalation)
            .options(
                joinedload(ComplaintEscalation.requester),
                joinedload(ComplaintEscalation.reviewer),
            )
            .where(
                ComplaintEscalation.complaint_id == complaint_id,
                ComplaintEscalation.deleted_at.is_(None),
                ComplaintEscalation.reason_code.is_not(None),
            )
            .order_by(ComplaintEscalation.created_at.desc())
        )
        return self._session.scalar(stmt)

    def next_level(self, complaint_id: uuid.UUID) -> int:
        stmt = select(func.coalesce(func.max(ComplaintEscalation.level), 0)).where(
            ComplaintEscalation.complaint_id == complaint_id,
            ComplaintEscalation.deleted_at.is_(None),
        )
        current_max = int(self._session.scalar(stmt) or 0)
        return current_max + 1

    def list_escalations(self, complaint_id: uuid.UUID) -> list[ComplaintEscalation]:
        stmt = (
            select(ComplaintEscalation)
            .options(
                joinedload(ComplaintEscalation.requester),
                joinedload(ComplaintEscalation.reviewer),
            )
            .where(
                ComplaintEscalation.complaint_id == complaint_id,
                ComplaintEscalation.deleted_at.is_(None),
            )
            .order_by(
                ComplaintEscalation.level.desc(),
                ComplaintEscalation.escalated_at.desc(),
            )
        )
        return list(self._session.scalars(stmt).unique().all())

    def add_escalation(self, escalation: ComplaintEscalation) -> ComplaintEscalation:
        self._session.add(escalation)
        self._session.flush()
        return escalation

    def add_timeline(
        self,
        *,
        complaint_id: uuid.UUID,
        actor_user_id: uuid.UUID,
        event_type: str,
        event_at: datetime,
        from_status: str | None,
        to_status: str | None,
        summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> ComplaintTimeline:
        when = event_at if event_at.tzinfo else event_at.replace(tzinfo=UTC)
        entry = ComplaintTimeline(
            complaint_id=complaint_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            event_at=when,
            from_status=from_status,
            to_status=to_status,
            summary=summary,
            metadata_json=metadata,
            created_at=when,
            updated_at=when,
            created_by=actor_user_id,
            updated_by=actor_user_id,
        )
        self._session.add(entry)
        self._session.flush()
        return entry

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, obj: Any) -> Any:
        self._session.refresh(obj)
        return obj
