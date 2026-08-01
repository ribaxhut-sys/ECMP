"""CAPABILITY-011 Attachment domain entity (metadata only; no business rules)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.core.errors import ValidationAppError
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus
from app.core.user_messages import m


@dataclass(slots=True)
class Attachment:
    """Generic attachment metadata bound to any aggregate.

    Bytes live behind StorageProvider. Entity holds metadata only —
    no Complaint / Queue / Notification business logic.
    """

    id: uuid.UUID
    aggregate_type: str
    aggregate_id: uuid.UUID
    file_name: str
    original_name: str
    mime_type: str
    extension: str | None
    size_bytes: int
    storage_provider: str
    storage_path: str
    checksum_sha256: str
    uploaded_by: uuid.UUID | None
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: str = AttachmentStatus.AVAILABLE.value

    @classmethod
    def create(
        cls,
        *,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        file_name: str,
        original_name: str,
        mime_type: str,
        extension: str | None,
        size_bytes: int,
        storage_provider: str,
        storage_path: str,
        checksum_sha256: str,
        uploaded_by: uuid.UUID | None = None,
        attachment_id: uuid.UUID | None = None,
        uploaded_at: datetime | None = None,
        status: str = AttachmentStatus.AVAILABLE.value,
    ) -> Attachment:
        try:
            AggregateType(aggregate_type)
        except ValueError as exc:
            raise ValidationAppError(
                f"tipe agregat tidak didukung: {aggregate_type}",
                details={
                    "aggregateType": aggregate_type,
                    "allowed": [a.value for a in AggregateType],
                },
            ) from exc

        try:
            AttachmentStatus(status)
        except ValueError as exc:
            raise ValidationAppError(
                f"status lampiran tidak didukung: {status}",
                details={
                    "status": status,
                    "allowed": [s.value for s in AttachmentStatus],
                },
            ) from exc

        cleaned_file = (file_name or "").strip()
        if not cleaned_file:
            raise ValidationAppError(
                m("storage.file_name_required"),
                details={"fileName": file_name},
            )
        cleaned_original = (original_name or "").strip()
        if not cleaned_original:
            raise ValidationAppError(
                m("storage.original_name_required"),
                details={"originalName": original_name},
            )
        cleaned_mime = (mime_type or "").strip().lower()
        if not cleaned_mime:
            raise ValidationAppError(
                m("storage.mime_type_required"),
                details={"mimeType": mime_type},
            )
        if size_bytes < 1:
            raise ValidationAppError(
                m("storage.size_bytes_min"),
                details={"sizeBytes": size_bytes},
            )
        cleaned_checksum = (checksum_sha256 or "").strip().lower()
        if len(cleaned_checksum) != 64:
            raise ValidationAppError(
                m("storage.checksum_sha256_format"),
                details={"checksumSha256": checksum_sha256},
            )
        cleaned_path = (storage_path or "").strip()
        if not cleaned_path:
            raise ValidationAppError(
                m("storage.storage_path_required"),
                details={"storagePath": storage_path},
            )
        cleaned_provider = (storage_provider or "").strip()
        if not cleaned_provider:
            raise ValidationAppError(
                m("storage.storage_provider_required"),
                details={"storageProvider": storage_provider},
            )

        created = uploaded_at or datetime.now(UTC)
        if created.tzinfo is None:
            created = created.replace(tzinfo=UTC)

        return cls(
            id=attachment_id or uuid.uuid4(),
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            file_name=cleaned_file,
            original_name=cleaned_original,
            mime_type=cleaned_mime,
            extension=extension,
            size_bytes=size_bytes,
            storage_provider=cleaned_provider,
            storage_path=cleaned_path,
            checksum_sha256=cleaned_checksum,
            uploaded_by=uploaded_by,
            uploaded_at=created,
            status=status,
        )

    def mark_available(self) -> None:
        if self.status == AttachmentStatus.DELETED.value:
            raise ValidationAppError(
                m("attachment.deleted_cannot_become_available"),
                details={"id": str(self.id), "status": self.status},
            )
        self.status = AttachmentStatus.AVAILABLE.value

    def mark_failed(self) -> None:
        if self.status == AttachmentStatus.DELETED.value:
            raise ValidationAppError(
                m("attachment.deleted_cannot_become_failed"),
                details={"id": str(self.id), "status": self.status},
            )
        self.status = AttachmentStatus.FAILED.value

    def mark_deleted(self) -> None:
        """Logical delete — metadata retained; bytes retained on disk."""
        if self.status == AttachmentStatus.DELETED.value:
            return
        self.status = AttachmentStatus.DELETED.value

    @property
    def is_active(self) -> bool:
        return self.status != AttachmentStatus.DELETED.value
