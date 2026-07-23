"""Escalation persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Complaint,
    ComplaintAssignment,
    ComplaintEscalation,
    ComplaintTimeline,
    Role,
    User,
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

    def user_exists(self, user_id: uuid.UUID) -> bool:
        stmt = select(User.id).where(
            User.id == user_id,
            User.deleted_at.is_(None),
            User.is_active.is_(True),
        )
        return self._session.scalar(stmt) is not None

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
            .where(
                ComplaintEscalation.complaint_id == complaint_id,
                ComplaintEscalation.deleted_at.is_(None),
            )
            .order_by(
                ComplaintEscalation.level.desc(),
                ComplaintEscalation.escalated_at.desc(),
            )
        )
        return list(self._session.scalars(stmt).all())

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
