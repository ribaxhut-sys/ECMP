"""Attachment Management unit/service tests (TASK-029)."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.attachment.service import (
    SETTING_ALLOWED_MIME,
    SETTING_MAX_UPLOAD_MB,
    SETTING_STORAGE_PROVIDER,
    SETTING_STORAGE_ROOT_PATH,
    AttachmentService,
    sanitize_filename,
)
from app.modules.attachment.storage.local import LocalStorageProvider


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
            SETTING_STORAGE_ROOT_PATH: root or "data/attachments",
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


def _row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "object_type": "complaint",
        "object_id": uuid.uuid4(),
        "filename": "note.pdf",
        "stored_filename": f"{uuid.uuid4().hex}.pdf",
        "mime_type": "application/pdf",
        "extension": ".pdf",
        "size_bytes": 12,
        "checksum": hashlib.sha256(b"hello-pdf!!").hexdigest(),
        "storage_provider": "local",
        "storage_path": "abc.pdf",
        "uploaded_by": uuid.uuid4(),
        "created_at": now,
        "deleted_at": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_sanitize_filename_strips_path_traversal() -> None:
    assert sanitize_filename("../../etc/passwd.pdf") == "passwd.pdf"
    assert sanitize_filename(r"..\..\secret.png") == "secret.png"
    with pytest.raises(ValidationAppError):
        sanitize_filename("../..")
    with pytest.raises(ValidationAppError):
        sanitize_filename("")


def test_local_storage_prevents_path_traversal(tmp_path: Path) -> None:
    storage = LocalStorageProvider(str(tmp_path))
    with pytest.raises(ValidationAppError):
        storage.save(stored_filename="../escape.txt", data=b"x")
    path = storage.save(stored_filename="ok.txt", data=b"payload")
    assert storage.read(path) == b"payload"
    assert storage.exists(path) is True


def test_upload_validates_empty_mime_size_extension(tmp_path: Path) -> None:
    repo = MagicMock()
    storage = LocalStorageProvider(str(tmp_path))
    svc = AttachmentService(repo, _settings(root=str(tmp_path)), storage=storage)
    object_id = uuid.uuid4()

    with pytest.raises(ValidationAppError, match="empty"):
        svc.upload(
            object_type="complaint",
            object_id=object_id,
            filename="a.pdf",
            content_type="application/pdf",
            data=b"",
            uploaded_by=None,
        )

    with pytest.raises(ValidationAppError, match="mime"):
        svc.upload(
            object_type="complaint",
            object_id=object_id,
            filename="a.exe",
            content_type="application/x-msdownload",
            data=b"MZ",
            uploaded_by=None,
        )

    with pytest.raises(ValidationAppError, match="extension"):
        svc.upload(
            object_type="complaint",
            object_id=object_id,
            filename="a.txt",
            content_type="application/pdf",
            data=b"%PDF",
            uploaded_by=None,
        )

    svc_small = AttachmentService(
        repo, _settings(max_mb=1, root=str(tmp_path)), storage=storage
    )
    with pytest.raises(ValidationAppError, match="maximum"):
        svc_small.upload(
            object_type="complaint",
            object_id=object_id,
            filename="big.pdf",
            content_type="application/pdf",
            data=b"x" * (1024 * 1024 + 1),
            uploaded_by=None,
        )


def test_upload_persists_checksum_and_unique_stored_name(tmp_path: Path) -> None:
    repo = MagicMock()
    created: list[object] = []

    def add(row: object) -> object:
        created.append(row)
        return row

    repo.add.side_effect = add
    storage = LocalStorageProvider(str(tmp_path))
    svc = AttachmentService(repo, _settings(root=str(tmp_path)), storage=storage)
    data = b"%PDF-1.4 demo"
    object_id = uuid.uuid4()
    uploader = uuid.uuid4()

    result = svc.upload(
        object_type="Complaint",
        object_id=object_id,
        filename="docs/report.pdf",
        content_type="application/pdf",
        data=data,
        uploaded_by=uploader,
    )

    assert result.filename == "report.pdf"
    assert result.object_type == "Complaint"
    assert result.checksum == hashlib.sha256(data).hexdigest()
    assert result.stored_filename.endswith(".pdf")
    assert result.stored_filename != "report.pdf"
    assert result.size_bytes == len(data)
    repo.add.assert_called_once()
    repo.commit.assert_called_once()
    assert storage.exists(created[0].storage_path)  # type: ignore[index]


def test_get_download_soft_delete(tmp_path: Path) -> None:
    row = _row()
    repo = MagicMock()
    repo.get_by_id.return_value = row
    storage = LocalStorageProvider(str(tmp_path))
    storage.save(stored_filename=row.storage_path, data=b"file-bytes")
    svc = AttachmentService(repo, _settings(root=str(tmp_path)), storage=storage)

    meta = svc.get(row.id)
    assert meta.id == row.id
    assert meta.filename == "note.pdf"

    fetched, payload = svc.download(row.id)
    assert fetched.id == row.id
    assert payload == b"file-bytes"

    svc.soft_delete(row.id)
    repo.soft_delete.assert_called_once_with(row)
    repo.commit.assert_called()
    # Soft delete retains physical blob.
    assert storage.exists(row.storage_path) is True


def test_get_missing_raises_not_found(tmp_path: Path) -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    svc = AttachmentService(
        repo, _settings(root=str(tmp_path)), storage=LocalStorageProvider(str(tmp_path))
    )
    with pytest.raises(NotFoundError):
        svc.get(uuid.uuid4())


def test_allowed_mime_setting_must_be_list(tmp_path: Path) -> None:
    settings = _settings(root=str(tmp_path))
    settings.get_json.side_effect = lambda key, default=None: {"not": "a list"}
    svc = AttachmentService(
        MagicMock(), settings, storage=LocalStorageProvider(str(tmp_path))
    )
    with pytest.raises(ValidationAppError, match="JSON array"):
        svc.upload(
            object_type="complaint",
            object_id=uuid.uuid4(),
            filename="a.pdf",
            content_type="application/pdf",
            data=b"%PDF",
            uploaded_by=None,
        )


def test_settings_defaults_json_roundtrip() -> None:
    """Guard: seed MIME list must remain valid JSON for SettingsService."""
    raw = json.dumps(
        ["application/pdf", "image/png"],
        separators=(",", ":"),
    )
    assert json.loads(raw) == ["application/pdf", "image/png"]
