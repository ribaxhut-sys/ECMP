"""CAPABILITY-011 Attachment Management unit/service/storage tests."""

from __future__ import annotations

import hashlib
import io
import json
import uuid
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.attachment.domain.entity import Attachment
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus
from app.modules.attachment.infrastructure.local_storage import LocalStorageProvider
from app.modules.attachment.service import (
    SETTING_ALLOWED_MIME,
    SETTING_MAX_UPLOAD_MB,
    SETTING_STORAGE_PROVIDER,
    SETTING_STORAGE_ROOT_PATH,
    AttachmentService,
    normalize_upload_mime,
    sanitize_filename,
)


def _settings(
    *,
    max_mb: int = 10,
    allowed: list[str] | None = None,
    root: str | None = None,
) -> MagicMock:
    allowed = allowed or ["application/pdf", "image/png", "text/plain"]
    settings = MagicMock()

    def get_string(key: str, *, default: str | None = None) -> str:
        values = {
            SETTING_STORAGE_PROVIDER: "local",
            SETTING_STORAGE_ROOT_PATH: root or "storage/attachments",
        }
        return values.get(key, default if default is not None else "")

    def get_int(key: str, *, default: int | None = None) -> int:
        if key == SETTING_MAX_UPLOAD_MB:
            return max_mb
        if default is not None:
            return default
        raise NotFoundError(key)

    def get_json(key: str, *, default: object | None = None) -> object:
        if key == SETTING_ALLOWED_MIME:
            return list(allowed)
        if default is not None:
            return default
        raise NotFoundError(key)

    settings.get_string.side_effect = get_string
    settings.get_int.side_effect = get_int
    settings.get_json.side_effect = get_json
    return settings


def _entity(**overrides: object) -> Attachment:
    data = b"hello-pdf!!"
    base = dict(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=uuid.uuid4(),
        file_name=f"{uuid.uuid4().hex}.pdf",
        original_name="note.pdf",
        mime_type="application/pdf",
        extension=".pdf",
        size_bytes=len(data),
        storage_provider="local",
        storage_path="2026/07/abc.pdf",
        checksum_sha256=hashlib.sha256(data).hexdigest(),
        uploaded_by=uuid.uuid4(),
        uploaded_at=datetime.now(UTC),
        status=AttachmentStatus.AVAILABLE.value,
    )
    base.update(overrides)
    return Attachment.create(**base)  # type: ignore[arg-type]


def test_sanitize_filename_strips_path_traversal() -> None:
    assert sanitize_filename("../../etc/passwd.pdf") == "passwd.pdf"
    assert sanitize_filename(r"..\..\secret.png") == "secret.png"
    with pytest.raises(ValidationAppError):
        sanitize_filename("../..")
    with pytest.raises(ValidationAppError):
        sanitize_filename("")


def test_local_storage_yyyy_mm_layout_and_traversal(tmp_path: Path) -> None:
    storage = LocalStorageProvider(str(tmp_path))
    with pytest.raises(ValidationAppError):
        storage.save(relative_path="../escape.txt", data=b"x")
    with pytest.raises(ValidationAppError):
        storage.save(relative_path="/abs.txt", data=b"x")
    path = storage.save(relative_path="2026/07/ok.txt", data=b"payload")
    assert path == "2026/07/ok.txt"
    assert (tmp_path / "2026" / "07" / "ok.txt").is_file()
    assert storage.read(path) == b"payload"
    assert storage.exists(path) is True
    storage.delete(path)
    assert storage.exists(path) is False


def test_upload_validates_empty_mime_size_extension(tmp_path: Path) -> None:
    repo = MagicMock()
    storage = LocalStorageProvider(str(tmp_path))
    svc = AttachmentService(repo, _settings(root=str(tmp_path)), storage=storage)
    aggregate_id = uuid.uuid4()

    with pytest.raises(ValidationAppError, match="kosong"):
        svc.upload(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=aggregate_id,
            filename="a.pdf",
            content_type="application/pdf",
            data=b"",
            uploaded_by=None,
        )

    with pytest.raises(ValidationAppError, match="[Mm]IME|[Mm]ime|tipe mime"):
        svc.upload(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=aggregate_id,
            filename="a.exe",
            content_type="application/x-msdownload",
            data=b"MZ",
            uploaded_by=None,
        )

    with pytest.raises(ValidationAppError, match="[Ee]kstensi"):
        svc.upload(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=aggregate_id,
            filename="a.txt",
            content_type="application/pdf",
            data=b"%PDF",
            uploaded_by=None,
        )

    with pytest.raises(ValidationAppError, match="agregat"):
        svc.upload(
            aggregate_type="Invoice",
            aggregate_id=aggregate_id,
            filename="a.pdf",
            content_type="application/pdf",
            data=b"%PDF",
            uploaded_by=None,
        )

    svc_small = AttachmentService(
        repo, _settings(max_mb=1, root=str(tmp_path)), storage=storage
    )
    with pytest.raises(ValidationAppError, match="maksimum"):
        svc_small.upload(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=aggregate_id,
            filename="big.pdf",
            content_type="application/pdf",
            data=b"x" * (1024 * 1024 + 1),
            uploaded_by=None,
        )


def test_upload_persists_checksum_and_unique_file_name(tmp_path: Path) -> None:
    repo = MagicMock()
    created: list[Attachment] = []

    def add(entity: Attachment) -> Attachment:
        created.append(entity)
        return entity

    repo.add.side_effect = add
    storage = LocalStorageProvider(str(tmp_path))
    svc = AttachmentService(repo, _settings(root=str(tmp_path)), storage=storage)
    data = b"%PDF-1.4 demo"
    aggregate_id = uuid.uuid4()
    uploader = uuid.uuid4()

    result = svc.upload(
        aggregate_type=AggregateType.COMPLAINT.value,
        aggregate_id=aggregate_id,
        filename="docs/report.pdf",
        content_type="application/pdf",
        data=data,
        uploaded_by=uploader,
    )

    assert result.original_name == "report.pdf"
    assert result.aggregate_type == AggregateType.COMPLAINT.value
    assert result.checksum_sha256 == hashlib.sha256(data).hexdigest()
    assert result.file_name.endswith(".pdf")
    assert result.file_name != "report.pdf"
    assert result.size_bytes == len(data)
    assert result.status == AttachmentStatus.AVAILABLE.value
    assert "/" in created[0].storage_path  # yyyy/mm/...
    repo.add.assert_called_once()
    repo.commit.assert_called_once()
    assert storage.exists(created[0].storage_path)


def test_get_download_logical_delete(tmp_path: Path) -> None:
    entity = _entity()
    repo = MagicMock()
    repo.get.return_value = entity
    storage = LocalStorageProvider(str(tmp_path))
    storage.save(relative_path=entity.storage_path, data=b"file-bytes")
    svc = AttachmentService(repo, _settings(root=str(tmp_path)), storage=storage)

    meta = svc.get(entity.id)
    assert meta.id == entity.id
    assert meta.original_name == "note.pdf"

    fetched, payload = svc.download(entity.id)
    assert fetched.id == entity.id
    assert payload == b"file-bytes"

    svc.soft_delete(entity.id)
    repo.save.assert_called_once()
    repo.commit.assert_called()
    assert entity.status == AttachmentStatus.DELETED.value
    assert storage.exists(entity.storage_path) is True


def test_list_and_missing(tmp_path: Path) -> None:
    repo = MagicMock()
    repo.get.return_value = None
    repo.list.return_value = ([], 0)
    svc = AttachmentService(
        repo, _settings(root=str(tmp_path)), storage=LocalStorageProvider(str(tmp_path))
    )
    with pytest.raises(NotFoundError):
        svc.get(uuid.uuid4())
    data, meta = svc.list(page=1, page_size=10)
    assert data == []
    assert meta.total_items == 0


def test_allowed_mime_setting_must_be_list(tmp_path: Path) -> None:
    settings = _settings(root=str(tmp_path))
    settings.get_json.side_effect = lambda key, default=None: {"not": "a list"}
    svc = AttachmentService(
        MagicMock(), settings, storage=LocalStorageProvider(str(tmp_path))
    )
    with pytest.raises(ValidationAppError, match="array JSON"):
        svc.upload(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=uuid.uuid4(),
            filename="a.pdf",
            content_type="application/pdf",
            data=b"%PDF",
            uploaded_by=None,
        )


def test_settings_defaults_json_roundtrip() -> None:
    raw = json.dumps(
        ["application/pdf", "image/png"],
        separators=(",", ":"),
    )
    assert json.loads(raw) == ["application/pdf", "image/png"]


def _minimal_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archive:
        archive.writestr("note.txt", "ok")
    return buf.getvalue()


def test_normalize_upload_mime_zip_aliases() -> None:
    data = _minimal_zip()
    assert (
        normalize_upload_mime(
            content_type="application/x-zip-compressed",
            filename="bukti.zip",
            data=data,
        )
        == "application/zip"
    )
    assert (
        normalize_upload_mime(
            content_type="application/octet-stream",
            filename="bukti.zip",
            data=data,
        )
        == "application/zip"
    )


def test_normalize_upload_mime_rejects_fake_zip() -> None:
    with pytest.raises(ValidationAppError, match="ZIP"):
        normalize_upload_mime(
            content_type="application/zip",
            filename="bukti.zip",
            data=b"not-a-zip",
        )


def test_upload_zip_as_opaque_blob(tmp_path: Path) -> None:
    repo = MagicMock()
    created: list[Attachment] = []
    repo.add.side_effect = lambda entity: created.append(entity) or entity
    storage = LocalStorageProvider(str(tmp_path))
    svc = AttachmentService(
        repo,
        _settings(root=str(tmp_path), allowed=["application/zip", "image/png"]),
        storage=storage,
    )
    data = _minimal_zip()
    result = svc.upload(
        aggregate_type=AggregateType.INTERNAL_COMPLAINT.value,
        aggregate_id=uuid.uuid4(),
        filename="bukti.zip",
        content_type="application/x-zip-compressed",
        data=data,
        uploaded_by=None,
    )
    assert result.mime_type == "application/zip"
    assert result.extension == ".zip"
    assert result.original_name == "bukti.zip"
    assert created[0].size_bytes == len(data)
    assert storage.read(created[0].storage_path) == data
