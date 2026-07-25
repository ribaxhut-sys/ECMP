"""CAPABILITY-011 — Attachment domain entity tests."""

from __future__ import annotations

import hashlib
import uuid

import pytest

from app.core.errors import ValidationAppError
from app.modules.attachment.domain.entity import Attachment
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus


def _checksum(data: bytes = b"payload") -> str:
    return hashlib.sha256(data).hexdigest()


def test_create_available_attachment() -> None:
    entity = Attachment.create(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=uuid.uuid4(),
        file_name=f"{uuid.uuid4().hex}.pdf",
        original_name="evidence.pdf",
        mime_type="application/pdf",
        extension=".pdf",
        size_bytes=12,
        storage_provider="local",
        storage_path="2026/07/abc.pdf",
        checksum_sha256=_checksum(),
    )
    assert entity.status == AttachmentStatus.AVAILABLE.value
    assert entity.is_active is True
    assert entity.uploaded_at.tzinfo is not None


def test_rejects_unknown_aggregate() -> None:
    with pytest.raises(ValidationAppError):
        Attachment.create(
            aggregate_type="Invoice",
            aggregate_id=uuid.uuid4(),
            file_name="a.pdf",
            original_name="a.pdf",
            mime_type="application/pdf",
            extension=".pdf",
            size_bytes=1,
            storage_provider="local",
            storage_path="2026/07/a.pdf",
            checksum_sha256=_checksum(),
        )


def test_rejects_invalid_checksum_and_empty_size() -> None:
    aid = uuid.uuid4()
    with pytest.raises(ValidationAppError, match="checksum"):
        Attachment.create(
            aggregate_type=AggregateType.QUEUE.value,
            aggregate_id=aid,
            file_name="a.pdf",
            original_name="a.pdf",
            mime_type="application/pdf",
            extension=".pdf",
            size_bytes=1,
            storage_provider="local",
            storage_path="2026/07/a.pdf",
            checksum_sha256="short",
        )
    with pytest.raises(ValidationAppError, match="size_bytes"):
        Attachment.create(
            aggregate_type=AggregateType.NOTIFICATION.value,
            aggregate_id=aid,
            file_name="a.pdf",
            original_name="a.pdf",
            mime_type="application/pdf",
            extension=".pdf",
            size_bytes=0,
            storage_provider="local",
            storage_path="2026/07/a.pdf",
            checksum_sha256=_checksum(),
        )


def test_logical_delete_and_failed_transitions() -> None:
    entity = Attachment.create(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=uuid.uuid4(),
        file_name="a.pdf",
        original_name="a.pdf",
        mime_type="application/pdf",
        extension=".pdf",
        size_bytes=1,
        storage_provider="local",
        storage_path="2026/07/a.pdf",
        checksum_sha256=_checksum(),
        status=AttachmentStatus.UPLOADED.value,
    )
    entity.mark_available()
    assert entity.status == AttachmentStatus.AVAILABLE.value
    entity.mark_failed()
    assert entity.status == AttachmentStatus.FAILED.value
    entity.mark_deleted()
    assert entity.status == AttachmentStatus.DELETED.value
    assert entity.is_active is False
    entity.mark_deleted()  # idempotent
    with pytest.raises(ValidationAppError):
        entity.mark_available()
    with pytest.raises(ValidationAppError):
        entity.mark_failed()
