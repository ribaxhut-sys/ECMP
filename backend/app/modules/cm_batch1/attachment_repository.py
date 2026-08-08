"""Repository for CM Batch 1 attachment business metadata (FR-004)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.cm_batch1.entities import (
    Batch1AttachmentHistoryRecord,
    Batch1AttachmentRecord,
    Batch1StagingSession,
)
from app.modules.cm_batch1.models import (
    CmBatch1AttachmentHistoryORM,
    CmBatch1AttachmentORM,
    CmBatch1AttachmentStagingORM,
)


def _to_attachment(row: CmBatch1AttachmentORM) -> Batch1AttachmentRecord:
    return Batch1AttachmentRecord(
        id=str(row.id),
        platform_attachment_id=str(row.platform_attachment_id),
        status=row.status,
        classification=row.classification,
        staging_token=row.staging_token,
        complaint_id=str(row.complaint_id) if row.complaint_id else None,
        customer_id=row.customer_id,
        original_name=row.original_name,
        mime_type=row.mime_type,
        size_bytes=row.size_bytes,
        checksum_sha256=row.checksum_sha256,
        supersedes_id=str(row.supersedes_id) if row.supersedes_id else None,
        void_reason=row.void_reason,
        uploaded_by=row.uploaded_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class CmBatch1AttachmentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def commit(self) -> None:
        self._session.commit()

    def create_staging_session(
        self,
        *,
        staging_token: str,
        expires_at: datetime,
        created_by: str | None,
    ) -> Batch1StagingSession:
        orm = CmBatch1AttachmentStagingORM(
            id=uuid.uuid4(),
            staging_token=staging_token,
            status="OPEN",
            created_by=created_by,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
        )
        self._session.add(orm)
        self._session.flush()
        return Batch1StagingSession(
            staging_token=staging_token,
            status="OPEN",
            expires_at=expires_at,
            created_by=created_by,
            created_at=orm.created_at,
        )

    def get_staging(self, staging_token: str) -> Batch1StagingSession | None:
        row = self._session.scalar(
            select(CmBatch1AttachmentStagingORM).where(
                CmBatch1AttachmentStagingORM.staging_token == staging_token
            )
        )
        if row is None:
            return None
        return Batch1StagingSession(
            staging_token=row.staging_token,
            status=row.status,
            expires_at=row.expires_at,
            created_by=row.created_by,
            created_at=row.created_at,
        )

    def close_staging(
        self, staging_token: str, *, status: str
    ) -> Batch1StagingSession | None:
        row = self._session.scalar(
            select(CmBatch1AttachmentStagingORM).where(
                CmBatch1AttachmentStagingORM.staging_token == staging_token
            )
        )
        if row is None:
            return None
        row.status = status
        row.closed_at = datetime.now(UTC)
        self._session.flush()
        return self.get_staging(staging_token)

    def list_expired_open_staging(self, *, now: datetime) -> list[Batch1StagingSession]:
        rows = self._session.scalars(
            select(CmBatch1AttachmentStagingORM)
            .where(CmBatch1AttachmentStagingORM.status == "OPEN")
            .where(CmBatch1AttachmentStagingORM.expires_at < now)
        ).all()
        return [
            Batch1StagingSession(
                staging_token=r.staging_token,
                status=r.status,
                expires_at=r.expires_at,
                created_by=r.created_by,
                created_at=r.created_at,
            )
            for r in rows
        ]

    def upload(
        self,
        *,
        platform_attachment_id: uuid.UUID,
        status: str,
        classification: str,
        staging_token: str | None,
        complaint_id: uuid.UUID | None,
        customer_id: str | None,
        original_name: str,
        mime_type: str,
        size_bytes: int,
        checksum_sha256: str,
        supersedes_id: uuid.UUID | None,
        uploaded_by: str | None,
    ) -> Batch1AttachmentRecord:
        now = datetime.now(UTC)
        orm = CmBatch1AttachmentORM(
            id=uuid.uuid4(),
            platform_attachment_id=platform_attachment_id,
            staging_token=staging_token,
            complaint_id=complaint_id,
            customer_id=(customer_id or "").strip() or None,
            classification=classification,
            status=status,
            original_name=original_name,
            mime_type=mime_type,
            size_bytes=size_bytes,
            checksum_sha256=checksum_sha256,
            supersedes_id=supersedes_id,
            uploaded_by=uploaded_by,
            created_at=now,
            updated_at=now,
        )
        self._session.add(orm)
        self._session.flush()
        return _to_attachment(orm)

    def get(self, attachment_id: str) -> Batch1AttachmentRecord | None:
        try:
            aid = uuid.UUID(attachment_id)
        except ValueError:
            return None
        row = self._session.get(CmBatch1AttachmentORM, aid)
        return _to_attachment(row) if row is not None else None

    def get_by_platform_id(
        self, platform_attachment_id: uuid.UUID
    ) -> Batch1AttachmentRecord | None:
        row = self._session.scalar(
            select(CmBatch1AttachmentORM).where(
                CmBatch1AttachmentORM.platform_attachment_id == platform_attachment_id
            )
        )
        return _to_attachment(row) if row is not None else None

    def find_by_checksum(
        self, checksum_sha256: str
    ) -> Batch1AttachmentRecord | None:
        row = self._session.scalar(
            select(CmBatch1AttachmentORM)
            .where(CmBatch1AttachmentORM.checksum_sha256 == checksum_sha256)
            .where(CmBatch1AttachmentORM.status.in_(["STAGED", "ACTIVE", "TRANSFERRED"]))
            .order_by(CmBatch1AttachmentORM.created_at.asc())
            .limit(1)
        )
        return _to_attachment(row) if row is not None else None

    def list_by_complaint(
        self, complaint_id: str, *, include_void: bool = False
    ) -> list[Batch1AttachmentRecord]:
        try:
            cid = uuid.UUID(complaint_id)
        except ValueError:
            return []
        stmt = select(CmBatch1AttachmentORM).where(
            CmBatch1AttachmentORM.complaint_id == cid
        )
        if not include_void:
            stmt = stmt.where(CmBatch1AttachmentORM.status != "VOID")
        stmt = stmt.order_by(CmBatch1AttachmentORM.created_at.asc())
        return [_to_attachment(r) for r in self._session.scalars(stmt).all()]

    def list_by_staging_token(
        self, staging_token: str
    ) -> list[Batch1AttachmentRecord]:
        rows = self._session.scalars(
            select(CmBatch1AttachmentORM)
            .where(CmBatch1AttachmentORM.staging_token == staging_token)
            .order_by(CmBatch1AttachmentORM.created_at.asc())
        ).all()
        return [_to_attachment(r) for r in rows]

    def bind(
        self,
        attachment_id: str,
        *,
        complaint_id: str,
        status: str,
        customer_id: str | None = None,
    ) -> Batch1AttachmentRecord:
        row = self._session.get(CmBatch1AttachmentORM, uuid.UUID(attachment_id))
        assert row is not None
        row.complaint_id = uuid.UUID(complaint_id)
        row.status = status
        if customer_id and customer_id.strip():
            row.customer_id = customer_id.strip()
        row.updated_at = datetime.now(UTC)
        self._session.flush()
        return _to_attachment(row)

    def transfer(
        self,
        attachment_id: str,
        *,
        complaint_id: str,
        status: str = "TRANSFERRED",
        customer_id: str | None = None,
    ) -> Batch1AttachmentRecord:
        return self.bind(
            attachment_id,
            complaint_id=complaint_id,
            status=status,
            customer_id=customer_id,
        )

    def void(
        self, attachment_id: str, *, reason: str
    ) -> Batch1AttachmentRecord:
        row = self._session.get(CmBatch1AttachmentORM, uuid.UUID(attachment_id))
        assert row is not None
        row.status = "VOID"
        row.void_reason = reason
        row.updated_at = datetime.now(UTC)
        self._session.flush()
        return _to_attachment(row)

    def supersede(
        self, prior_id: str, *, successor_id: str
    ) -> Batch1AttachmentRecord:
        prior = self._session.get(CmBatch1AttachmentORM, uuid.UUID(prior_id))
        assert prior is not None
        prior.status = "SUPERSEDED"
        prior.updated_at = datetime.now(UTC)
        successor = self._session.get(CmBatch1AttachmentORM, uuid.UUID(successor_id))
        assert successor is not None
        successor.supersedes_id = prior.id
        successor.updated_at = datetime.now(UTC)
        self._session.flush()
        return _to_attachment(prior)

    def append_history(
        self,
        *,
        attachment_id: str,
        event_type: str,
        from_status: str | None,
        to_status: str | None,
        reason: str | None,
        actor_id: str | None,
        details: str | None = None,
    ) -> Batch1AttachmentHistoryRecord:
        hid = uuid.uuid4()
        now = datetime.now(UTC)
        self._session.add(
            CmBatch1AttachmentHistoryORM(
                id=hid,
                attachment_id=uuid.UUID(attachment_id),
                event_type=event_type,
                from_status=from_status,
                to_status=to_status,
                reason=reason,
                actor_id=actor_id,
                details=details,
                created_at=now,
            )
        )
        self._session.flush()
        return Batch1AttachmentHistoryRecord(
            id=str(hid),
            attachment_id=attachment_id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            reason=reason,
            actor_id=actor_id,
            created_at=now,
            details=details,
        )

    def history(
        self, attachment_id: str
    ) -> list[Batch1AttachmentHistoryRecord]:
        rows = self._session.scalars(
            select(CmBatch1AttachmentHistoryORM)
            .where(CmBatch1AttachmentHistoryORM.attachment_id == uuid.UUID(attachment_id))
            .order_by(CmBatch1AttachmentHistoryORM.created_at.asc())
        ).all()
        return [
            Batch1AttachmentHistoryRecord(
                id=str(r.id),
                attachment_id=str(r.attachment_id),
                event_type=r.event_type,
                from_status=r.from_status,
                to_status=r.to_status,
                reason=r.reason,
                actor_id=r.actor_id,
                created_at=r.created_at,
                details=r.details,
            )
            for r in rows
        ]
