"""Knowledge ↔ Attachment relation persistence.

Reuses the generic ``attachments`` table for storage/metadata (CAPABILITY-011)
— this repository only owns the join row (which platform attachment belongs
to which Knowledge, and its role: PRIMARY or SUPPORTING). Mirrors
app.modules.announcement.attachment_repository.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.attachment.models import AttachmentORM
from app.modules.knowledge.models import KnowledgeFileORM


@dataclass(slots=True)
class KnowledgeFileRow:
    """Join row + platform attachment metadata, combined for API responses."""

    id: uuid.UUID
    knowledge_id: uuid.UUID
    attachment_id: uuid.UUID
    role: str
    created_at: datetime
    file_name: str
    original_name: str
    mime_type: str
    size_bytes: int


_ROW_COLUMNS = (
    KnowledgeFileORM.id,
    KnowledgeFileORM.knowledge_id,
    KnowledgeFileORM.attachment_id,
    KnowledgeFileORM.role,
    KnowledgeFileORM.created_at,
    AttachmentORM.file_name,
    AttachmentORM.original_name,
    AttachmentORM.mime_type,
    AttachmentORM.size_bytes,
)


def _to_row(record: tuple) -> KnowledgeFileRow:
    return KnowledgeFileRow(
        id=record[0],
        knowledge_id=record[1],
        attachment_id=record[2],
        role=record[3],
        created_at=record[4],
        file_name=record[5],
        original_name=record[6],
        mime_type=record[7],
        size_bytes=record[8],
    )


class KnowledgeFileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        knowledge_id: uuid.UUID,
        attachment_id: uuid.UUID,
        role: str,
        created_by: uuid.UUID | None,
    ) -> KnowledgeFileORM:
        row = KnowledgeFileORM(
            knowledge_id=knowledge_id,
            attachment_id=attachment_id,
            role=role,
            created_by=created_by,
            updated_by=created_by,
        )
        self._session.add(row)
        self._session.flush()
        return row

    def get(
        self, knowledge_id: uuid.UUID, attachment_id: uuid.UUID
    ) -> KnowledgeFileORM | None:
        stmt = select(KnowledgeFileORM).where(
            KnowledgeFileORM.knowledge_id == knowledge_id,
            KnowledgeFileORM.attachment_id == attachment_id,
        )
        return self._session.scalar(stmt)

    def get_primary(self, knowledge_id: uuid.UUID) -> KnowledgeFileORM | None:
        stmt = select(KnowledgeFileORM).where(
            KnowledgeFileORM.knowledge_id == knowledge_id,
            KnowledgeFileORM.role == "PRIMARY",
        )
        return self._session.scalar(stmt)

    def is_knowledge_domain_attachment(self, attachment_id: uuid.UUID) -> bool:
        stmt = select(KnowledgeFileORM.id).where(
            KnowledgeFileORM.attachment_id == attachment_id
        )
        return self._session.scalar(stmt) is not None

    def get_by_attachment_id(
        self, attachment_id: uuid.UUID
    ) -> KnowledgeFileORM | None:
        """Reverse lookup — a file belongs to exactly one Knowledge (direct
        1:1 bind, unlike the announcement catalog's many-to-many reuse)."""
        stmt = select(KnowledgeFileORM).where(
            KnowledgeFileORM.attachment_id == attachment_id
        )
        return self._session.scalar(stmt)

    def list_for_knowledge(self, knowledge_id: uuid.UUID) -> list[KnowledgeFileRow]:
        stmt = (
            select(*_ROW_COLUMNS)
            .select_from(KnowledgeFileORM)
            .join(AttachmentORM, AttachmentORM.id == KnowledgeFileORM.attachment_id)
            .where(KnowledgeFileORM.knowledge_id == knowledge_id)
            .order_by(
                # PRIMARY first, then newest.
                KnowledgeFileORM.role.asc(),
                KnowledgeFileORM.created_at.desc(),
            )
        )
        return [_to_row(r) for r in self._session.execute(stmt).all()]

    def list_for_knowledge_ids(
        self, knowledge_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[KnowledgeFileRow]]:
        if not knowledge_ids:
            return {}
        stmt = (
            select(*_ROW_COLUMNS)
            .select_from(KnowledgeFileORM)
            .join(AttachmentORM, AttachmentORM.id == KnowledgeFileORM.attachment_id)
            .where(KnowledgeFileORM.knowledge_id.in_(knowledge_ids))
            .order_by(
                KnowledgeFileORM.role.asc(),
                KnowledgeFileORM.created_at.desc(),
            )
        )
        result: dict[uuid.UUID, list[KnowledgeFileRow]] = {}
        for record in self._session.execute(stmt).all():
            row = _to_row(record)
            result.setdefault(row.knowledge_id, []).append(row)
        return result

    def clear_primary(self, knowledge_id: uuid.UUID, *, updated_by: uuid.UUID) -> None:
        current = self.get_primary(knowledge_id)
        if current is None:
            return
        current.role = "SUPPORTING"
        current.updated_by = updated_by
        self._session.flush()

    def set_primary(self, row: KnowledgeFileORM, *, updated_by: uuid.UUID) -> None:
        """Exactly one PRIMARY per Knowledge — clear any existing first."""
        self.clear_primary(row.knowledge_id, updated_by=updated_by)
        row.role = "PRIMARY"
        row.updated_by = updated_by
        self._session.flush()

    def delete(self, row: KnowledgeFileORM) -> None:
        self._session.delete(row)
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()
