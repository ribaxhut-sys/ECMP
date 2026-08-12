"""Knowledge persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.modules.attachment.domain.enums import AttachmentStatus
from app.modules.attachment.models import AttachmentORM
from app.modules.knowledge.models import KnowledgeFileORM, KnowledgeORM


def within_effective_window(
    row: KnowledgeORM, *, now: datetime | None = None
) -> bool:
    """True when ``now`` falls inside [effective_from, effective_to] (both
    optional/open-ended). Used only to narrow the reader-facing default
    search — never gates detail access (ARCHIVED/ACTIVE records stay openable
    regardless of window, per business decision, LOCKED)."""
    when = now or datetime.now(UTC)
    if row.effective_from is not None and row.effective_from > when:
        return False
    if row.effective_to is not None and row.effective_to < when:
        return False
    return True


class KnowledgeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, knowledge_id: uuid.UUID) -> KnowledgeORM | None:
        stmt = select(KnowledgeORM).where(
            KnowledgeORM.id == knowledge_id,
            KnowledgeORM.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def search(
        self,
        *,
        q: str | None = None,
        knowledge_type: str | None = None,
        status: str,
    ) -> list[KnowledgeORM]:
        """Search by title / document_number / summary / primary file name.

        ``status`` is always an explicit single value here — callers decide
        default ("ACTIVE") and the DRAFT-manager gate before calling.
        """
        stmt = (
            select(KnowledgeORM)
            .where(
                KnowledgeORM.deleted_at.is_(None),
                KnowledgeORM.status == status,
            )
            .order_by(KnowledgeORM.created_at.desc(), KnowledgeORM.id.desc())
        )
        if knowledge_type:
            stmt = stmt.where(KnowledgeORM.knowledge_type == knowledge_type)
        if q and q.strip():
            pattern = f"%{q.strip()}%"
            primary_file_match = (
                select(KnowledgeFileORM.knowledge_id)
                .join(AttachmentORM, AttachmentORM.id == KnowledgeFileORM.attachment_id)
                .where(
                    KnowledgeFileORM.knowledge_id == KnowledgeORM.id,
                    AttachmentORM.original_name.ilike(pattern),
                    AttachmentORM.status != AttachmentStatus.DELETED.value,
                )
                .correlate(KnowledgeORM)
                .exists()
            )
            stmt = stmt.where(
                or_(
                    KnowledgeORM.title.ilike(pattern),
                    KnowledgeORM.document_number.ilike(pattern),
                    KnowledgeORM.summary.ilike(pattern),
                    primary_file_match,
                )
            )
        return list(self._session.scalars(stmt).all())

    def create(
        self,
        *,
        title: str,
        knowledge_type: str,
        document_number: str | None,
        summary: str | None,
        version_label: str | None,
        effective_from: datetime | None,
        effective_to: datetime | None,
        owner_org_unit_id: str | None,
        created_by: uuid.UUID,
        now: datetime | None = None,
    ) -> KnowledgeORM:
        when = now or datetime.now(UTC)
        row = KnowledgeORM(
            title=title,
            knowledge_type=knowledge_type,
            status="DRAFT",
            document_number=document_number,
            summary=summary,
            version_label=version_label,
            effective_from=effective_from,
            effective_to=effective_to,
            owner_org_unit_id=owner_org_unit_id,
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
        row: KnowledgeORM,
        *,
        title: str,
        knowledge_type: str,
        document_number: str | None,
        summary: str | None,
        version_label: str | None,
        effective_from: datetime | None,
        effective_to: datetime | None,
        updated_by: uuid.UUID,
        now: datetime | None = None,
    ) -> KnowledgeORM:
        when = now or datetime.now(UTC)
        row.title = title
        row.knowledge_type = knowledge_type
        row.document_number = document_number
        row.summary = summary
        row.version_label = version_label
        row.effective_from = effective_from
        row.effective_to = effective_to
        row.updated_by = updated_by
        row.updated_at = when
        self._session.flush()
        return row

    def publish(
        self,
        row: KnowledgeORM,
        *,
        published_by: uuid.UUID,
        now: datetime | None = None,
    ) -> KnowledgeORM:
        when = now or datetime.now(UTC)
        row.status = "ACTIVE"
        row.published_at = when
        row.published_by = published_by
        row.updated_by = published_by
        row.updated_at = when
        self._session.flush()
        return row

    def archive(
        self,
        row: KnowledgeORM,
        *,
        updated_by: uuid.UUID,
        now: datetime | None = None,
    ) -> KnowledgeORM:
        when = now or datetime.now(UTC)
        row.status = "ARCHIVED"
        row.updated_by = updated_by
        row.updated_at = when
        self._session.flush()
        return row

    def unarchive(
        self,
        row: KnowledgeORM,
        *,
        updated_by: uuid.UUID,
        now: datetime | None = None,
    ) -> KnowledgeORM:
        """ARCHIVED -> ACTIVE. Preserves original published_at/published_by."""
        when = now or datetime.now(UTC)
        row.status = "ACTIVE"
        row.updated_by = updated_by
        row.updated_at = when
        self._session.flush()
        return row

    def soft_delete(
        self,
        row: KnowledgeORM,
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
