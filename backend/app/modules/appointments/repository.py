"""Appointment persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, time
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import AppointmentStatus
from app.models import (
    Appointment,
    Complaint,
    ComplaintEscalation,
    ComplaintTimeline,
    User,
)

# Current appointment for an escalation (blocks re-book; shown on Escalation UI).
CURRENT_APPOINTMENT_STATUSES = frozenset(
    {
        AppointmentStatus.BOOKED,
        AppointmentStatus.CHECKED_IN,
        AppointmentStatus.COMPLETED,
    }
)


class AppointmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_escalation(self, escalation_id: uuid.UUID) -> ComplaintEscalation | None:
        stmt = select(ComplaintEscalation).where(
            ComplaintEscalation.id == escalation_id,
            ComplaintEscalation.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def get_complaint(self, complaint_id: uuid.UUID) -> Complaint | None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        stmt = (
            select(Appointment)
            .options(joinedload(Appointment.assigned_engineer))
            .where(
                Appointment.id == appointment_id,
                Appointment.deleted_at.is_(None),
            )
        )
        return self._session.scalar(stmt)

    def get_active_by_escalation(
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

    def find_engineer_overlap(
        self,
        *,
        engineer_id: uuid.UUID,
        on_date: date,
        start: time,
        end: time,
        exclude_id: uuid.UUID | None = None,
    ) -> Appointment | None:
        """Return any BOOKED appointment overlapping [start, end) for engineer/date."""
        stmt = select(Appointment).where(
            Appointment.assigned_engineer_id == engineer_id,
            Appointment.appointment_date == on_date,
            Appointment.deleted_at.is_(None),
            Appointment.status.in_(CURRENT_APPOINTMENT_STATUSES),
            and_(
                Appointment.appointment_start_time < end,
                Appointment.appointment_end_time > start,
            ),
        )
        if exclude_id is not None:
            stmt = stmt.where(Appointment.id != exclude_id)
        return self._session.scalar(stmt)

    def add(self, appointment: Appointment) -> Appointment:
        self._session.add(appointment)
        self._session.flush()
        return appointment

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
