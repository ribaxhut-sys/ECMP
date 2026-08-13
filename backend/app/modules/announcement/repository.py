"""Announcement persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, func, not_, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.modules.announcement.models import (
    AnnouncementNumberCounterORM,
    AnnouncementORM,
    AnnouncementReadORM,
)
from app.modules.announcement.reference_number import (
    counter_name as announcement_counter_name,
)
from app.modules.announcement.reference_number import (
    next_reference_number,
)


def is_scheduled_announcement(
    status: str,
    start_at: datetime | None,
    *,
    now: datetime | None = None,
) -> bool:
    """True when PUBLISHED but start_at is still in the future (derived SCHEDULED)."""
    when = now or datetime.now(UTC)
    return status == "PUBLISHED" and start_at is not None and start_at > when


class AnnouncementRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, announcement_id: uuid.UUID) -> AnnouncementORM | None:
        stmt = select(AnnouncementORM).where(
            AnnouncementORM.id == announcement_id,
            AnnouncementORM.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def list_all(self) -> list[AnnouncementORM]:
        """Management list — every status, newest created first."""
        stmt = (
            select(AnnouncementORM)
            .where(AnnouncementORM.deleted_at.is_(None))
            .order_by(AnnouncementORM.created_at.desc())
        )
        return list(self._session.scalars(stmt).all())

    @staticmethod
    def _active_conditions(*, now: datetime) -> tuple[Any, ...]:
        """Single definition of "active" (PUBLISHED, in-window) — shared by
        list_active and count_unread_active so the sidebar badge never
        drifts from what /active actually returns. Announcements are
        global (no audience/target) — every announcement:read holder sees
        the same set."""
        return (
            AnnouncementORM.deleted_at.is_(None),
            AnnouncementORM.status == "PUBLISHED",
            or_(
                AnnouncementORM.start_at.is_(None),
                AnnouncementORM.start_at <= now,
            ),
            or_(
                AnnouncementORM.end_at.is_(None),
                AnnouncementORM.end_at > now,
            ),
        )

    def list_active(self, *, now: datetime | None = None) -> list[AnnouncementORM]:
        """Public/landing list — PUBLISHED, in-window.

        Newest published first; pinned handling (priority) is a presentation
        concern left to the caller/frontend, matching the existing landing
        page's sort convention.
        """
        when = now or datetime.now(UTC)
        stmt = (
            select(AnnouncementORM)
            .where(*self._active_conditions(now=when))
            .order_by(AnnouncementORM.published_at.desc())
        )
        return list(self._session.scalars(stmt).all())

    def count_unread_active(
        self,
        *,
        user_id: uuid.UUID,
        now: datetime | None = None,
    ) -> int:
        """COUNT of active announcements with no read record for this user.
        Same "active" window as list_active — sidebar badge only nags on
        currently visible items, not the expired archive.
        """
        when = now or datetime.now(UTC)
        read_exists = (
            select(AnnouncementReadORM.id)
            .where(
                AnnouncementReadORM.announcement_id == AnnouncementORM.id,
                AnnouncementReadORM.user_id == user_id,
            )
            .correlate(AnnouncementORM)
            .exists()
        )
        stmt = (
            select(func.count())
            .select_from(AnnouncementORM)
            .where(*self._active_conditions(now=when), ~read_exists)
        )
        return int(self._session.scalar(stmt) or 0)

    def list_read_ids(
        self,
        *,
        user_id: uuid.UUID,
        announcement_ids: list[uuid.UUID],
    ) -> set[uuid.UUID]:
        """Which of the given announcements this user has already opened."""
        if not announcement_ids:
            return set()
        stmt = select(AnnouncementReadORM.announcement_id).where(
            AnnouncementReadORM.user_id == user_id,
            AnnouncementReadORM.announcement_id.in_(announcement_ids),
        )
        return set(self._session.scalars(stmt).all())

    def mark_read(
        self,
        *,
        announcement_id: uuid.UUID,
        user_id: uuid.UUID,
        now: datetime | None = None,
    ) -> None:
        """Idempotent — ON CONFLICT DO NOTHING on the (announcement_id,
        user_id) unique pair, so opening the detail page twice still leaves
        exactly one read record (§19)."""
        when = now or datetime.now(UTC)
        stmt = (
            pg_insert(AnnouncementReadORM)
            .values(announcement_id=announcement_id, user_id=user_id, read_at=when)
            .on_conflict_do_nothing(index_elements=["announcement_id", "user_id"])
        )
        self._session.execute(stmt)
        self._session.flush()

    def list_history(self, *, now: datetime | None = None) -> list[AnnouncementORM]:
        """Reader archive — PUBLISHED (incl. EXPIRED) + ARCHIVED.

        Not filtered by end_at (expired stays visible), but SCHEDULED rows
        (PUBLISHED with start_at in the future) are excluded — same as DRAFT
        for cabang/readers until visibility starts.
        """
        when = now or datetime.now(UTC)
        stmt = (
            select(AnnouncementORM)
            .where(
                AnnouncementORM.deleted_at.is_(None),
                AnnouncementORM.status.in_(("PUBLISHED", "ARCHIVED")),
                not_(
                    and_(
                        AnnouncementORM.status == "PUBLISHED",
                        AnnouncementORM.start_at.is_not(None),
                        AnnouncementORM.start_at > when,
                    )
                ),
            )
            .order_by(
                AnnouncementORM.published_at.desc().nulls_last(),
                AnnouncementORM.created_at.desc(),
            )
        )
        return list(self._session.scalars(stmt).all())

    def _next_reference_number(self, *, at: datetime | None = None) -> str:
        """Allocate ``PGM-YYMM-NNNN``; counter per calendar month (global)."""
        when = at or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)
        name = announcement_counter_name(year=when.year, month=when.month)
        row = self._session.scalar(
            select(AnnouncementNumberCounterORM)
            .where(AnnouncementNumberCounterORM.name == name)
            .with_for_update()
        )
        if row is None:
            row = AnnouncementNumberCounterORM(name=name, value=0)
            self._session.add(row)
            self._session.flush()
            row = self._session.scalar(
                select(AnnouncementNumberCounterORM)
                .where(AnnouncementNumberCounterORM.name == name)
                .with_for_update()
            )
            assert row is not None
        row.value += 1
        self._session.flush()
        return next_reference_number(sequence=row.value, at=when)

    def create(
        self,
        *,
        title: str,
        body: str,
        priority: str,
        end_at: datetime | None,
        created_by: uuid.UUID,
        now: datetime | None = None,
    ) -> AnnouncementORM:
        when = now or datetime.now(UTC)
        row = AnnouncementORM(
            reference_number=self._next_reference_number(at=when),
            title=title,
            body=body,
            priority=priority,
            status="DRAFT",
            end_at=end_at,
            created_by=created_by,
            updated_by=created_by,
            created_at=when,
            updated_at=when,
        )
        self._session.add(row)
        self._session.flush()
        return row

    def update_fields(
        self,
        row: AnnouncementORM,
        *,
        title: str,
        body: str,
        priority: str,
        end_at: datetime | None,
        updated_by: uuid.UUID,
        start_at: datetime | None = None,
        update_start_at: bool = False,
        now: datetime | None = None,
    ) -> AnnouncementORM:
        when = now or datetime.now(UTC)
        row.title = title
        row.body = body
        row.priority = priority
        row.end_at = end_at
        if update_start_at:
            row.start_at = start_at
        row.updated_by = updated_by
        row.updated_at = when
        self._session.flush()
        return row

    def publish(
        self,
        row: AnnouncementORM,
        *,
        published_by: uuid.UUID,
        start_at: datetime | None = None,
        now: datetime | None = None,
    ) -> AnnouncementORM:
        """Publish — start_at defaults to now; a future value schedules visibility.

        published_at is always the admin action time. Visibility uses start_at
        at read/query time (DEC: no scheduler).
        """
        when = now or datetime.now(UTC)
        row.status = "PUBLISHED"
        row.start_at = start_at if start_at is not None else when
        row.published_at = when
        row.published_by = published_by
        row.updated_by = published_by
        row.updated_at = when
        self._session.flush()
        return row

    def unpublish(
        self,
        row: AnnouncementORM,
        *,
        updated_by: uuid.UUID,
        now: datetime | None = None,
    ) -> AnnouncementORM:
        when = now or datetime.now(UTC)
        row.status = "ARCHIVED"
        row.updated_by = updated_by
        row.updated_at = when
        self._session.flush()
        return row

    def soft_delete(
        self,
        row: AnnouncementORM,
        *,
        deleted_by: uuid.UUID,
        now: datetime | None = None,
    ) -> None:
        when = now or datetime.now(UTC)
        row.deleted_at = when
        row.updated_by = deleted_by
        row.updated_at = when
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, obj: Any) -> Any:
        self._session.refresh(obj)
        return obj
