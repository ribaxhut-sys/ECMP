"""Assignment persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Complaint, ComplaintAssignment, ComplaintTimeline, User


class AssignmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

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

    def get_user_full_name(self, user_id: uuid.UUID) -> str | None:
        stmt = select(User.full_name).where(
            User.id == user_id,
            User.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def get_current_assignment(
        self, complaint_id: uuid.UUID
    ) -> ComplaintAssignment | None:
        stmt = (
            select(ComplaintAssignment)
            .options(joinedload(ComplaintAssignment.assignee))
            .where(
                ComplaintAssignment.complaint_id == complaint_id,
                ComplaintAssignment.is_current.is_(True),
                ComplaintAssignment.deleted_at.is_(None),
            )
        )
        return self._session.scalar(stmt)

    def list_assignments(self, complaint_id: uuid.UUID) -> list[ComplaintAssignment]:
        stmt = (
            select(ComplaintAssignment)
            .options(joinedload(ComplaintAssignment.assignee))
            .where(
                ComplaintAssignment.complaint_id == complaint_id,
                ComplaintAssignment.deleted_at.is_(None),
            )
            .order_by(ComplaintAssignment.assigned_at.desc())
        )
        return list(self._session.scalars(stmt).unique().all())

    def add_assignment(self, assignment: ComplaintAssignment) -> ComplaintAssignment:
        self._session.add(assignment)
        self._session.flush()
        return assignment

    def close_assignment(
        self,
        assignment: ComplaintAssignment,
        *,
        unassigned_at: datetime,
        actor_user_id: uuid.UUID,
    ) -> None:
        assignment.is_current = False
        assignment.unassigned_at = unassigned_at
        assignment.updated_at = unassigned_at
        assignment.updated_by = actor_user_id
        self._session.flush()

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
        if isinstance(obj, ComplaintAssignment):
            if "assignee" not in obj.__dict__ or obj.__dict__.get("assignee") is None:
                assignee = self._session.get(User, obj.assignee_id)
                if assignee is not None:
                    obj.assignee = assignee
        return obj
