"""Announcement ↔ Attachment relation persistence.

Reuses the generic ``attachments`` table for storage/metadata (CAPABILITY-011)
— this repository only owns the join row (which platform attachment belongs
to which announcement, and its visibility choice).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session

from app.models import User
from app.modules.announcement.models import AnnouncementAttachmentORM
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus
from app.modules.attachment.models import AttachmentORM


@dataclass(slots=True)
class AnnouncementAttachmentRow:
    """Join row + platform attachment metadata, combined for API responses."""

    id: uuid.UUID
    announcement_id: uuid.UUID
    attachment_id: uuid.UUID
    visibility: str
    created_by: uuid.UUID | None
    created_at: datetime
    file_name: str
    original_name: str
    mime_type: str
    extension: str | None
    size_bytes: int
    status: str


@dataclass(slots=True)
class AnnouncementAttachmentLibraryRow:
    """Distinct platform attachment eligible for catalog / link picker."""

    id: uuid.UUID
    file_name: str
    original_name: str
    mime_type: str
    size_bytes: int
    created_at: datetime
    access_level: str | None
    uploaded_org_unit_id: str | None
    uploaded_by: uuid.UUID | None
    uploaded_by_name: str | None
    usage_count: int


_ROW_COLUMNS = (
    AnnouncementAttachmentORM.id,
    AnnouncementAttachmentORM.announcement_id,
    AnnouncementAttachmentORM.attachment_id,
    AnnouncementAttachmentORM.visibility,
    AnnouncementAttachmentORM.created_by,
    AnnouncementAttachmentORM.created_at,
    AttachmentORM.file_name,
    AttachmentORM.original_name,
    AttachmentORM.mime_type,
    AttachmentORM.extension,
    AttachmentORM.size_bytes,
    AttachmentORM.status,
)


class AnnouncementAttachmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        announcement_id: uuid.UUID,
        attachment_id: uuid.UUID,
        visibility: str,
        created_by: uuid.UUID | None,
    ) -> AnnouncementAttachmentORM:
        row = AnnouncementAttachmentORM(
            announcement_id=announcement_id,
            attachment_id=attachment_id,
            visibility=visibility,
            created_by=created_by,
            updated_by=created_by,
        )
        self._session.add(row)
        self._session.flush()
        return row

    def get(
        self, announcement_id: uuid.UUID, attachment_id: uuid.UUID
    ) -> AnnouncementAttachmentORM | None:
        stmt = select(AnnouncementAttachmentORM).where(
            AnnouncementAttachmentORM.announcement_id == announcement_id,
            AnnouncementAttachmentORM.attachment_id == attachment_id,
        )
        return self._session.scalar(stmt)

    def get_by_attachment_id(
        self, attachment_id: uuid.UUID
    ) -> AnnouncementAttachmentORM | None:
        """Reverse lookup — first join for an attachment (legacy callers).

        Prefer ``list_by_attachment_id`` when access depends on *any* join.
        """
        joins = self.list_by_attachment_id(attachment_id)
        return joins[0] if joins else None

    def list_by_attachment_id(
        self, attachment_id: uuid.UUID
    ) -> list[AnnouncementAttachmentORM]:
        """All announcement joins for a platform attachment (multi-reuse)."""
        stmt = (
            select(AnnouncementAttachmentORM)
            .where(AnnouncementAttachmentORM.attachment_id == attachment_id)
            .order_by(AnnouncementAttachmentORM.created_at.asc())
        )
        return list(self._session.scalars(stmt).all())

    def count_for_attachment(self, attachment_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(AnnouncementAttachmentORM).where(
            AnnouncementAttachmentORM.attachment_id == attachment_id
        )
        return int(self._session.scalar(stmt) or 0)

    def is_announcement_domain_attachment(self, attachment_id: uuid.UUID) -> bool:
        """True when the file is (or was) bound into the announcement domain."""
        if self.count_for_attachment(attachment_id) > 0:
            return True
        stmt = select(AttachmentORM.id).where(
            AttachmentORM.id == attachment_id,
            AttachmentORM.aggregate_type == AggregateType.ANNOUNCEMENT.value,
            AttachmentORM.status != AttachmentStatus.DELETED.value,
        )
        return self._session.scalar(stmt) is not None

    def list_reusable(
        self,
        *,
        q: str | None = None,
        exclude_announcement_id: uuid.UUID | None = None,
        include_orphans: bool = False,
    ) -> list[AnnouncementAttachmentLibraryRow]:
        """Distinct non-deleted announcement-domain attachments for catalog/picker.

        ``include_orphans`` — also include Announcement aggregate rows with no
        join (still in catalog after unlink-all).
        """
        usage = (
            select(
                AnnouncementAttachmentORM.attachment_id.label("aid"),
                func.count().label("usage_count"),
            )
            .group_by(AnnouncementAttachmentORM.attachment_id)
            .subquery()
        )
        has_announcement_join = exists().where(
            AnnouncementAttachmentORM.attachment_id == AttachmentORM.id
        )
        domain_filter = has_announcement_join
        if include_orphans:
            domain_filter = or_(
                has_announcement_join,
                AttachmentORM.aggregate_type == AggregateType.ANNOUNCEMENT.value,
            )
        stmt = (
            select(
                AttachmentORM.id,
                AttachmentORM.file_name,
                AttachmentORM.original_name,
                AttachmentORM.mime_type,
                AttachmentORM.size_bytes,
                AttachmentORM.uploaded_at,
                AttachmentORM.access_level,
                AttachmentORM.uploaded_org_unit_id,
                AttachmentORM.uploaded_by,
                User.full_name,
                func.coalesce(usage.c.usage_count, 0),
            )
            .outerjoin(usage, usage.c.aid == AttachmentORM.id)
            .outerjoin(
                User,
                (User.id == AttachmentORM.uploaded_by) & (User.deleted_at.is_(None)),
            )
            .where(
                domain_filter,
                AttachmentORM.status != AttachmentStatus.DELETED.value,
            )
        )
        if exclude_announcement_id is not None:
            already_linked = select(AnnouncementAttachmentORM.attachment_id).where(
                AnnouncementAttachmentORM.announcement_id == exclude_announcement_id
            )
            stmt = stmt.where(AttachmentORM.id.notin_(already_linked))
        if q and q.strip():
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    AttachmentORM.original_name.ilike(pattern),
                    AttachmentORM.file_name.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )
        stmt = stmt.order_by(AttachmentORM.uploaded_at.desc())
        return [
            AnnouncementAttachmentLibraryRow(
                id=row[0],
                file_name=row[1],
                original_name=row[2],
                mime_type=row[3],
                size_bytes=row[4],
                created_at=row[5],
                access_level=row[6],
                uploaded_org_unit_id=row[7],
                uploaded_by=row[8],
                uploaded_by_name=row[9],
                usage_count=int(row[10] or 0),
            )
            for row in self._session.execute(stmt).all()
        ]

    def delete_all_joins_for_attachment(self, attachment_id: uuid.UUID) -> int:
        joins = self.list_by_attachment_id(attachment_id)
        for join in joins:
            self._session.delete(join)
        self._session.flush()
        return len(joins)

    def update_visibility(
        self,
        row: AnnouncementAttachmentORM,
        *,
        visibility: str,
        updated_by: uuid.UUID | None,
    ) -> AnnouncementAttachmentORM:
        row.visibility = visibility
        row.updated_by = updated_by
        self._session.flush()
        return row

    def delete(self, row: AnnouncementAttachmentORM) -> None:
        self._session.delete(row)
        self._session.flush()

    def list_for_announcement(
        self, announcement_id: uuid.UUID
    ) -> list[AnnouncementAttachmentRow]:
        rows = self.list_for_announcements([announcement_id])
        return rows.get(announcement_id, [])

    def list_for_announcements(
        self, announcement_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[AnnouncementAttachmentRow]]:
        """Bulk variant — avoids N+1 across the management/active list endpoints."""
        if not announcement_ids:
            return {}
        stmt = (
            select(*_ROW_COLUMNS)
            .join(
                AttachmentORM,
                AttachmentORM.id == AnnouncementAttachmentORM.attachment_id,
            )
            .where(
                AnnouncementAttachmentORM.announcement_id.in_(announcement_ids),
                AttachmentORM.status != AttachmentStatus.DELETED.value,
            )
            .order_by(AnnouncementAttachmentORM.created_at.asc())
        )
        result: dict[uuid.UUID, list[AnnouncementAttachmentRow]] = {
            aid: [] for aid in announcement_ids
        }
        for record in self._session.execute(stmt).all():
            row = AnnouncementAttachmentRow(**record._mapping)
            result.setdefault(row.announcement_id, []).append(row)
        return result

    def commit(self) -> None:
        self._session.commit()
