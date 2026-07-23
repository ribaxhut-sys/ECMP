"""Resolution persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import (
    Appointment,
    AuditLog,
    Complaint,
    ComplaintEscalation,
    ComplaintResolution,
    ComplaintTimeline,
    User,
)


class ResolutionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_complaint(self, complaint_id: uuid.UUID) -> Complaint | None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def get_user(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
            User.is_active.is_(True),
        )
        return self._session.scalar(stmt)

    def get_current_resolution(
        self, complaint_id: uuid.UUID
    ) -> ComplaintResolution | None:
        stmt = (
            select(ComplaintResolution)
            .options(joinedload(ComplaintResolution.resolver))
            .where(
                ComplaintResolution.complaint_id == complaint_id,
                ComplaintResolution.is_current.is_(True),
                ComplaintResolution.deleted_at.is_(None),
            )
        )
        return self._session.scalar(stmt)

    def get_final_resolution(
        self, complaint_id: uuid.UUID
    ) -> ComplaintResolution | None:
        """Return the resolution row that has Final Resolution submitted."""
        stmt = (
            select(ComplaintResolution)
            .options(joinedload(ComplaintResolution.final_resolver))
            .where(
                ComplaintResolution.complaint_id == complaint_id,
                ComplaintResolution.final_resolution_at.is_not(None),
                ComplaintResolution.deleted_at.is_(None),
            )
            .order_by(ComplaintResolution.final_resolution_at.desc())
        )
        return self._session.scalar(stmt)

    def get_latest_appointment_for_complaint(
        self, complaint_id: uuid.UUID
    ) -> Appointment | None:
        """Latest appointment linked via escalation for the complaint."""
        stmt = (
            select(Appointment)
            .join(
                ComplaintEscalation,
                Appointment.escalation_id == ComplaintEscalation.id,
            )
            .where(
                ComplaintEscalation.complaint_id == complaint_id,
                ComplaintEscalation.deleted_at.is_(None),
                Appointment.deleted_at.is_(None),
            )
            .order_by(Appointment.created_at.desc())
        )
        return self._session.scalar(stmt)

    def get_escalation(
        self, escalation_id: uuid.UUID
    ) -> ComplaintEscalation | None:
        stmt = select(ComplaintEscalation).where(
            ComplaintEscalation.id == escalation_id,
            ComplaintEscalation.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def close_current_resolution(
        self,
        resolution: ComplaintResolution,
        *,
        actor_user_id: uuid.UUID,
        when: datetime,
    ) -> None:
        resolution.is_current = False
        resolution.updated_at = when
        resolution.updated_by = actor_user_id
        self._session.flush()

    def add_resolution(self, resolution: ComplaintResolution) -> ComplaintResolution:
        self._session.add(resolution)
        self._session.flush()
        return resolution

    def add_audit_log(
        self,
        *,
        actor_user_id: uuid.UUID | None,
        action: str,
        entity_id: uuid.UUID,
        new_value: dict[str, Any],
        old_value: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> AuditLog:
        when = occurred_at or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)

        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type="Complaint",
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            occurred_at=when,
        )
        self._session.add(entry)
        self._session.flush()
        return entry

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

    def refresh(self, entity: ComplaintResolution) -> ComplaintResolution:
        self._session.refresh(entity)
        return entity
