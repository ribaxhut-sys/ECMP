"""CAPABILITY-011 — additional service/storage/router coverage tests."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.auth import Principal
from app.core.errors import NotFoundError, ValidationAppError
from app.core.schemas import PageMeta
from app.modules.attachment.domain.entity import Attachment
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus
from app.modules.attachment.infrastructure.local_storage import LocalStorageProvider
from app.modules.attachment.registration import build_attachment_service
from app.modules.attachment.repository import AttachmentRepository
from app.modules.attachment.router import (
    delete_attachment,
    download_attachment,
    get_attachment,
    list_attachments,
    list_complaint_attachments,
    upload_attachment,
)
from app.modules.attachment.schemas import AttachmentResponse
from app.modules.attachment.service import (
    SETTING_STORAGE_PROVIDER,
    SETTING_STORAGE_ROOT_PATH,
    AttachmentService,
    build_storage_provider,
    sanitize_filename,
)


def _settings(root: str) -> MagicMock:
    settings = MagicMock()
    settings.get_string.side_effect = lambda key, default=None: {
        SETTING_STORAGE_PROVIDER: "local",
        SETTING_STORAGE_ROOT_PATH: root,
    }.get(key, default or "")
    settings.get_int.side_effect = lambda key, default=None: (
        default if default is not None else 10
    )
    settings.get_json.side_effect = lambda key, default=None: default
    return settings


def _entity(**overrides: object) -> Attachment:
    data = b"%PDF"
    base: dict[str, object] = dict(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=uuid.uuid4(),
        file_name=f"{uuid.uuid4().hex}.pdf",
        original_name="evidence.pdf",
        mime_type="application/pdf",
        extension=".pdf",
        size_bytes=len(data),
        storage_provider="local",
        storage_path="2026/07/a.pdf",
        checksum_sha256=hashlib.sha256(data).hexdigest(),
        uploaded_by=uuid.uuid4(),
    )
    base.update(overrides)
    return Attachment.create(**base)  # type: ignore[arg-type]


def _response(entity: Attachment) -> AttachmentResponse:
    return AttachmentResponse(
        id=entity.id,
        aggregateType=entity.aggregate_type,  # type: ignore[arg-type]
        aggregateId=entity.aggregate_id,
        fileName=entity.file_name,
        originalName=entity.original_name,
        mimeType=entity.mime_type,
        extension=entity.extension,
        sizeBytes=entity.size_bytes,
        storageProvider=entity.storage_provider,
        checksumSha256=entity.checksum_sha256,
        uploadedBy=entity.uploaded_by,
        uploadedAt=entity.uploaded_at,
        status=entity.status,  # type: ignore[arg-type]
    )


def test_build_storage_provider_rejects_unknown_and_empty_root(tmp_path: Path) -> None:
    settings = MagicMock()
    settings.get_string.side_effect = lambda key, default=None: {
        SETTING_STORAGE_PROVIDER: "s3",
        SETTING_STORAGE_ROOT_PATH: "x",
    }.get(key, default or "")
    with pytest.raises(ValidationAppError, match="tidak didukung"):
        build_storage_provider(settings)

    settings.get_string.side_effect = lambda key, default=None: {
        SETTING_STORAGE_PROVIDER: "local",
        SETTING_STORAGE_ROOT_PATH: "  ",
    }.get(key, default or "")
    with pytest.raises(ValidationAppError, match="kosong"):
        build_storage_provider(settings)

    settings.get_string.side_effect = lambda key, default=None: {
        SETTING_STORAGE_PROVIDER: "local",
        SETTING_STORAGE_ROOT_PATH: str(tmp_path),
    }.get(key, default or "")
    provider = build_storage_provider(settings)
    assert provider.provider_name == "local"


def test_sanitize_long_filename() -> None:
    long_name = "a" * 300 + ".pdf"
    cleaned = sanitize_filename(long_name)
    assert len(cleaned) <= 255
    assert cleaned.endswith(".pdf")


def test_local_storage_open_absolute_and_missing(tmp_path: Path) -> None:
    storage = LocalStorageProvider(str(tmp_path))
    rel = storage.save(relative_path="2026/07/doc.txt", data=b"abc")
    with storage.open(rel) as fh:
        assert fh.read() == b"abc"
    abs_path = str((tmp_path / "2026" / "07" / "doc.txt").resolve())
    assert storage.read(abs_path) == b"abc"
    with pytest.raises(NotFoundError):
        storage.read("2026/07/missing.txt")
    outside = str((tmp_path.parent / "escape.txt").resolve())
    with pytest.raises(ValidationAppError):
        storage.read(outside)
    storage.delete("2026/07/missing.txt")


def test_local_storage_absolute_root(tmp_path: Path) -> None:
    storage = LocalStorageProvider(str(tmp_path.resolve()))
    path = storage.save(relative_path="2026/07/x.txt", data=b"z")
    assert storage.exists(path)


def test_repository_get_save_and_list_by_aggregate() -> None:
    session = MagicMock()
    repo = AttachmentRepository(session)
    entity = _entity()

    session.scalar.return_value = None
    assert repo.get(entity.id) is None

    row = MagicMock()
    row.id = entity.id
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
    session.get.return_value = row
    entity.mark_deleted()
    saved = repo.save(entity)
    assert saved.status == AttachmentStatus.DELETED.value

    session.scalar.return_value = 1
    session.scalars.return_value.all.return_value = [row]
    rows, total = repo.list_by_aggregate(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=entity.aggregate_id,
    )
    assert total == 1
    assert rows[0].id == entity.id
    repo.commit()
    repo.rollback()
    session.commit.assert_called()
    session.rollback.assert_called()


def test_repository_save_adds_when_missing() -> None:
    session = MagicMock()
    session.get.return_value = None
    repo = AttachmentRepository(session)
    entity = _entity()
    saved = repo.save(entity)
    session.add.assert_called_once()
    assert saved.id == entity.id


def test_service_list_for_complaint_and_db_failure_cleanup(tmp_path: Path) -> None:
    repo = MagicMock()
    storage = LocalStorageProvider(str(tmp_path))
    svc = AttachmentService(repo, _settings(str(tmp_path)), storage=storage)
    entity = _entity()
    repo.list.return_value = ([entity], 1)
    data, meta = svc.list_for_complaint(entity.aggregate_id, page=1, page_size=10)
    assert len(data) == 1
    assert meta.total_items == 1

    with pytest.raises(ValidationAppError, match="agregat"):
        svc.list(aggregate_type="Invoice")

    repo.add.side_effect = RuntimeError("db down")
    with pytest.raises(RuntimeError):
        svc.upload(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=uuid.uuid4(),
            filename="a.pdf",
            content_type="application/pdf",
            data=b"%PDF",
            uploaded_by=None,
        )
    repo.rollback.assert_called()


def test_entity_required_field_guards() -> None:
    checksum = hashlib.sha256(b"x").hexdigest()
    base = dict(
        aggregate_type=AggregateType.QUEUE.value,
        aggregate_id=uuid.uuid4(),
        file_name="a.pdf",
        original_name="a.pdf",
        mime_type="application/pdf",
        extension=".pdf",
        size_bytes=1,
        storage_provider="local",
        storage_path="2026/07/a.pdf",
        checksum_sha256=checksum,
    )
    for field in (
        "file_name",
        "original_name",
        "mime_type",
        "storage_path",
        "storage_provider",
    ):
        bad = dict(base)
        bad[field] = "  "
        with pytest.raises(ValidationAppError):
            Attachment.create(**bad)  # type: ignore[arg-type]
    with pytest.raises(ValidationAppError):
        Attachment.create(**{**base, "status": "NOPE"})  # type: ignore[arg-type]


def test_router_handlers_call_service() -> None:
    import asyncio

    entity = _entity()
    resp = _response(entity)
    svc = MagicMock()
    svc.upload.return_value = resp
    svc.get.return_value = resp
    svc.list.return_value = ([resp], PageMeta(page=1, pageSize=50, totalItems=1))
    svc.list_for_complaint.return_value = (
        [resp],
        PageMeta(page=1, pageSize=100, totalItems=1),
    )
    svc.download.return_value = (entity, b"%PDF")
    principal = Principal(
        user_id=entity.uploaded_by or uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset(),
    )

    upload_file = MagicMock()
    upload_file.filename = "evidence.pdf"
    upload_file.content_type = "application/pdf"

    async def _read() -> bytes:
        return b"%PDF"

    upload_file.read = _read

    batch1 = MagicMock()
    batch1.try_get_by_platform_id.return_value = None
    batch1.try_get.return_value = None
    batch1.resolve_platform_attachment_id.side_effect = lambda aid: aid

    created = asyncio.run(
        upload_attachment(
            service=svc,
            batch1=batch1,
            principal=principal,
            session=MagicMock(),
            settings=MagicMock(),
            aggregate_type="Complaint",
            aggregate_id=entity.aggregate_id,
            file=upload_file,
        )
    )
    assert created.data.id == entity.id

    assert (
        get_attachment(
            entity.id,
            svc,
            batch1,
            principal,
            session=MagicMock(),
            settings=MagicMock(),
        ).data.id
        == entity.id
    )
    listed = list_attachments(
        svc, principal, session=MagicMock(), settings=MagicMock()
    )
    assert listed.meta.total_items == 1
    dl = download_attachment(
        entity.id, svc, batch1, principal, session=MagicMock(), settings=MagicMock()
    )
    assert dl.body == b"%PDF"

    with patch(
        "app.modules.attachment.router.CmBatch1Repository"
    ) as repo_cls:
        repo_cls.return_value.get.return_value = None
        complaint_listed = list_complaint_attachments(
            entity.aggregate_id,
            svc,
            batch1,
            session=MagicMock(),
            principal=principal,
        )
        assert complaint_listed.meta.total_items == 1

    request = MagicMock()
    session = MagicMock()
    with patch("app.modules.attachment.router.write_audit") as audit:
        result = delete_attachment(
            entity.id,
            request,
            session,
            svc,
            batch1,
            principal,
            settings=MagicMock(),
        )
        assert result.status_code == 204
        audit.assert_called_once()
        svc.soft_delete.assert_called_once_with(entity.id)



def test_build_attachment_service_wires_repo(tmp_path: Path) -> None:
    session = MagicMock()
    with (
        patch("app.modules.attachment.registration.SettingsService") as settings_cls,
        patch("app.modules.attachment.registration.SettingsRepository"),
        patch("app.modules.attachment.service.build_storage_provider") as build_storage,
    ):
        settings_cls.return_value = MagicMock()
        build_storage.return_value = LocalStorageProvider(str(tmp_path))
        svc = build_attachment_service(session)
        assert isinstance(svc, AttachmentService)
