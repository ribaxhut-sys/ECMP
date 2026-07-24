"""Timeline persistence repository (SQLAlchemy 2.x, read-only)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.enums import TimelineEvent
from app.models import Complaint, ComplaintTimeline

_SUPPORTED_EVENTS = tuple(event.value for event in TimelineEvent)


class TimelineRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_complaint(self, complaint_id: uuid.UUID) -> Complaint | None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def list_by_complaint(self, complaint_id: uuid.UUID) -> list[ComplaintTimeline]:
        """Return timeline rows newest-first (created_at DESC). Immutable read."""
        stmt = (
            select(ComplaintTimeline)
            .options(joinedload(ComplaintTimeline.actor))
            .where(
                ComplaintTimeline.complaint_id == complaint_id,
                ComplaintTimeline.deleted_at.is_(None),
                ComplaintTimeline.event_type.in_(_SUPPORTED_EVENTS),
            )
            .order_by(
                ComplaintTimeline.created_at.desc(),
                ComplaintTimeline.id.desc(),
            )
        )
        return list(self._session.scalars(stmt).unique().all())

    def list_recent(self, *, limit: int = 10) -> list[ComplaintTimeline]:
        """Return latest timeline rows across active complaints (newest-first)."""
        stmt = (
            select(ComplaintTimeline)
            .join(Complaint, Complaint.id == ComplaintTimeline.complaint_id)
            .options(
                joinedload(ComplaintTimeline.actor),
                joinedload(ComplaintTimeline.complaint),
            )
            .where(
                ComplaintTimeline.deleted_at.is_(None),
                Complaint.deleted_at.is_(None),
                ComplaintTimeline.event_type.in_(_SUPPORTED_EVENTS),
            )
            .order_by(
                ComplaintTimeline.event_at.desc(),
                ComplaintTimeline.created_at.desc(),
                ComplaintTimeline.id.desc(),
            )
            .limit(limit)
        )
        return list(self._session.scalars(stmt).unique().all())
