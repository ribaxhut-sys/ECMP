"""CAPABILITY-011 Attachment persistence repository."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.attachment.domain.entity import Attachment
from app.modules.attachment.domain.enums import AttachmentStatus
from app.modules.attachment.models import AttachmentORM


def _to_orm(entity: Attachment) -> AttachmentORM:
    return AttachmentORM(
        id=entity.id,
        aggregate_type=entity.aggregate_type,
        aggregate_id=entity.aggregate_id,
        file_name=entity.file_name,
        original_name=entity.original_name,
        mime_type=entity.mime_type,
        extension=entity.extension,
        size_bytes=entity.size_bytes,
        storage_provider=entity.storage_provider,
        storage_path=entity.storage_path,
        checksum_sha256=entity.checksum_sha256,
        uploaded_by=entity.uploaded_by,
        uploaded_at=entity.uploaded_at,
        status=entity.status,
        access_level=entity.access_level,
        uploaded_org_unit_id=entity.uploaded_org_unit_id,
    )


def _to_entity(row: AttachmentORM) -> Attachment:
    return Attachment(
        id=row.id,
        aggregate_type=row.aggregate_type,
        aggregate_id=row.aggregate_id,
        file_name=row.file_name,
        original_name=row.original_name,
        mime_type=row.mime_type,
        extension=row.extension,
        size_bytes=row.size_bytes,
        storage_provider=row.storage_provider,
        storage_path=row.storage_path,
        checksum_sha256=row.checksum_sha256,
        uploaded_by=row.uploaded_by,
        uploaded_at=row.uploaded_at,
        status=row.status,
        access_level=row.access_level,
        uploaded_org_unit_id=row.uploaded_org_unit_id,
    )


class AttachmentRepository:
    """Metadata persistence — no file I/O."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, entity: Attachment) -> Attachment:
        row = _to_orm(entity)
        self._session.add(row)
        self._session.flush()
        return _to_entity(row)

    def get(self, attachment_id: uuid.UUID, *, include_deleted: bool = False) -> Attachment | None:
        stmt = select(AttachmentORM).where(AttachmentORM.id == attachment_id)
        if not include_deleted:
            stmt = stmt.where(AttachmentORM.status != AttachmentStatus.DELETED.value)
        row = self._session.scalar(stmt)
        return _to_entity(row) if row is not None else None

    def list(
        self,
        *,
        aggregate_type: str | None = None,
        aggregate_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False,
    ) -> tuple[list[Attachment], int]:
        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        filters = []
        if not include_deleted:
            filters.append(AttachmentORM.status != AttachmentStatus.DELETED.value)
        if aggregate_type is not None:
            filters.append(AttachmentORM.aggregate_type == aggregate_type)
        if aggregate_id is not None:
            filters.append(AttachmentORM.aggregate_id == aggregate_id)

        count_stmt = select(func.count()).select_from(AttachmentORM)
        list_stmt = select(AttachmentORM).order_by(
            AttachmentORM.uploaded_at.desc(),
            AttachmentORM.id.desc(),
        )
        for f in filters:
            count_stmt = count_stmt.where(f)
            list_stmt = list_stmt.where(f)

        total = int(self._session.scalar(count_stmt) or 0)
        list_stmt = list_stmt.offset((page - 1) * page_size).limit(page_size)
        rows = list(self._session.scalars(list_stmt).all())
        return [_to_entity(r) for r in rows], total

    def list_by_aggregate(
        self,
        *,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        page: int = 1,
        page_size: int = 100,
    ) -> tuple[list[Attachment], int]:
        return self.list(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            page=page,
            page_size=page_size,
        )

    def save(self, entity: Attachment) -> Attachment:
        row = self._session.get(AttachmentORM, entity.id)
        if row is None:
            return self.add(entity)
        row.aggregate_type = entity.aggregate_type
        row.aggregate_id = entity.aggregate_id
        row.file_name = entity.file_name
        row.original_name = entity.original_name
        row.mime_type = entity.mime_type
        row.extension = entity.extension
        row.size_bytes = entity.size_bytes
        row.storage_provider = entity.storage_provider
        row.storage_path = entity.storage_path
        row.checksum_sha256 = entity.checksum_sha256
        row.uploaded_by = entity.uploaded_by
        row.uploaded_at = entity.uploaded_at
        row.status = entity.status
        row.access_level = entity.access_level
        row.uploaded_org_unit_id = entity.uploaded_org_unit_id
        self._session.flush()
        return _to_entity(row)

    def find_by_checksum(
        self, checksum_sha256: str, *, include_deleted: bool = False
    ) -> Attachment | None:
        stmt = select(AttachmentORM).where(
            AttachmentORM.checksum_sha256 == checksum_sha256
        )
        if not include_deleted:
            stmt = stmt.where(AttachmentORM.status != AttachmentStatus.DELETED.value)
        stmt = stmt.order_by(AttachmentORM.uploaded_at.asc()).limit(1)
        row = self._session.scalar(stmt)
        return _to_entity(row) if row is not None else None

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def flush(self) -> None:
        self._session.flush()
