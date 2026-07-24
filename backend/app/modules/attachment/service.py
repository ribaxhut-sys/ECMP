"""Attachment Management service (TASK-029).

Generic platform upload/download/soft-delete. Domain-agnostic via
object_type + object_id. All file I/O goes through StorageProvider.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import UTC, datetime
from pathlib import PurePosixPath

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.attachment.models import Attachment
from app.modules.attachment.repository import AttachmentRepository
from app.modules.attachment.schemas import AttachmentResponse
from app.modules.attachment.storage.base import StorageProvider
from app.modules.attachment.storage.local import LocalStorageProvider
from app.modules.settings.service import SettingsService

# Setting keys (seeded by migration 0017; not hardcoded operational values).
SETTING_STORAGE_PROVIDER = "storage.provider"
SETTING_STORAGE_ROOT_PATH = "storage.root.path"
SETTING_MAX_UPLOAD_MB = "storage.max.upload.mb"
SETTING_ALLOWED_MIME = "storage.allowed.mime"

_DEFAULT_PROVIDER = "local"
_DEFAULT_ROOT_PATH = "data/attachments"
_DEFAULT_MAX_UPLOAD_MB = 10
_DEFAULT_ALLOWED_MIME: list[str] = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]

_MIME_EXTENSIONS: dict[str, frozenset[str]] = {
    "application/pdf": frozenset({".pdf"}),
    "image/jpeg": frozenset({".jpg", ".jpeg"}),
    "image/png": frozenset({".png"}),
    "image/gif": frozenset({".gif"}),
    "image/webp": frozenset({".webp"}),
    "text/plain": frozenset({".txt"}),
    "application/msword": frozenset({".doc"}),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": frozenset(
        {".docx"}
    ),
    "application/vnd.ms-excel": frozenset({".xls"}),
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": frozenset(
        {".xlsx"}
    ),
}

_OBJECT_TYPE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,49}$")
_UNSAFE_FILENAME_RE = re.compile(r"[\x00-\x1f\x7f<>:\"|?*]")


def build_storage_provider(settings: SettingsService) -> StorageProvider:
    """Resolve StorageProvider from SettingsService (no hardcoded paths)."""
    provider = settings.get_string(
        SETTING_STORAGE_PROVIDER, default=_DEFAULT_PROVIDER
    ).strip().lower()
    if provider == "local":
        root = settings.get_string(
            SETTING_STORAGE_ROOT_PATH, default=_DEFAULT_ROOT_PATH
        ).strip()
        if not root:
            raise ValidationAppError(
                "storage.root.path must not be empty",
                details={"key": SETTING_STORAGE_ROOT_PATH},
            )
        return LocalStorageProvider(root)
    raise ValidationAppError(
        f"unsupported storage provider: {provider}",
        details={"key": SETTING_STORAGE_PROVIDER, "value": provider},
    )


def sanitize_filename(raw_name: str | None) -> str:
    """Strip path components and unsafe characters from a client filename."""
    if raw_name is None or not raw_name.strip():
        raise ValidationAppError(
            "filename is required",
            details={"filename": raw_name},
        )
    # Collapse path traversal / separators to basename only.
    name = PurePosixPath(raw_name.replace("\\", "/")).name
    name = name.strip().strip(".")
    name = _UNSAFE_FILENAME_RE.sub("_", name)
    name = name.replace("..", "_")
    if not name or name in {".", ".."}:
        raise ValidationAppError(
            "filename is invalid after sanitization",
            details={"filename": raw_name},
        )
    if len(name) > 255:
        stem = PurePosixPath(name).stem[:200]
        suffix = PurePosixPath(name).suffix[:20]
        name = f"{stem}{suffix}"
    return name


def _extension_of(filename: str) -> str | None:
    suffix = PurePosixPath(filename).suffix.lower()
    if not suffix or suffix == ".":
        return None
    if len(suffix) > 20:
        raise ValidationAppError(
            "file extension is too long",
            details={"extension": suffix},
        )
    return suffix


def _to_response(row: Attachment) -> AttachmentResponse:
    return AttachmentResponse.model_validate(row)


class AttachmentService:
    """Upload / metadata / download / soft-delete for platform attachments."""

    def __init__(
        self,
        repository: AttachmentRepository,
        settings: SettingsService,
        storage: StorageProvider | None = None,
    ) -> None:
        self._repo = repository
        self._settings = settings
        self._storage = storage or build_storage_provider(settings)

    def upload(
        self,
        *,
        object_type: str,
        object_id: uuid.UUID,
        filename: str | None,
        content_type: str | None,
        data: bytes,
        uploaded_by: uuid.UUID | None,
    ) -> AttachmentResponse:
        normalized_type = self._validate_object_type(object_type)
        safe_name = sanitize_filename(filename)
        extension = _extension_of(safe_name)
        mime_type = (content_type or "").strip().lower() or "application/octet-stream"

        if not data:
            raise ValidationAppError(
                "file must not be empty",
                details={"sizeBytes": 0},
            )

        max_mb = self._settings.get_int(
            SETTING_MAX_UPLOAD_MB, default=_DEFAULT_MAX_UPLOAD_MB
        )
        if max_mb < 1:
            raise ValidationAppError(
                "storage.max.upload.mb must be >= 1",
                details={"key": SETTING_MAX_UPLOAD_MB, "value": max_mb},
            )
        max_bytes = max_mb * 1024 * 1024
        size_bytes = len(data)
        if size_bytes > max_bytes:
            raise ValidationAppError(
                "file exceeds maximum upload size",
                details={
                    "sizeBytes": size_bytes,
                    "maxBytes": max_bytes,
                    "maxUploadMb": max_mb,
                },
            )

        allowed = self._allowed_mime_types()
        if mime_type not in allowed:
            raise ValidationAppError(
                "mime type is not allowed",
                details={"mimeType": mime_type, "allowed": sorted(allowed)},
            )

        expected_exts = _MIME_EXTENSIONS.get(mime_type)
        if expected_exts is not None:
            if extension is None or extension not in expected_exts:
                raise ValidationAppError(
                    "file extension does not match mime type",
                    details={
                        "extension": extension,
                        "mimeType": mime_type,
                        "expectedExtensions": sorted(expected_exts),
                    },
                )

        checksum = hashlib.sha256(data).hexdigest()
        stored_filename = f"{uuid.uuid4().hex}{extension or ''}"

        try:
            storage_path = self._storage.save(
                stored_filename=stored_filename, data=data
            )
        except Exception:
            self._repo.rollback()
            raise

        row = Attachment(
            id=uuid.uuid4(),
            object_type=normalized_type,
            object_id=object_id,
            filename=safe_name,
            stored_filename=stored_filename,
            mime_type=mime_type,
            extension=extension,
            size_bytes=size_bytes,
            checksum=checksum,
            storage_provider=self._storage.provider_name,
            storage_path=storage_path,
            uploaded_by=uploaded_by,
            created_at=datetime.now(UTC),
        )
        try:
            self._repo.add(row)
            self._repo.commit()
        except Exception:
            # Best-effort cleanup of orphaned blob if DB write fails.
            try:
                self._storage.delete(storage_path)
            except Exception:
                pass
            self._repo.rollback()
            raise

        return _to_response(row)

    def get(self, attachment_id: uuid.UUID) -> AttachmentResponse:
        return _to_response(self._require(attachment_id))

    def download(self, attachment_id: uuid.UUID) -> tuple[Attachment, bytes]:
        row = self._require(attachment_id)
        data = self._storage.read(row.storage_path)
        return row, data

    def soft_delete(self, attachment_id: uuid.UUID) -> None:
        row = self._require(attachment_id)
        self._repo.soft_delete(row)
        self._repo.commit()
        # Physical blob retained for retention / audit; soft delete only.

    def _require(self, attachment_id: uuid.UUID) -> Attachment:
        row = self._repo.get_by_id(attachment_id)
        if row is None:
            raise NotFoundError("Attachment not found")
        return row

    def _allowed_mime_types(self) -> set[str]:
        raw = self._settings.get_json(
            SETTING_ALLOWED_MIME, default=list(_DEFAULT_ALLOWED_MIME)
        )
        if not isinstance(raw, list) or not raw:
            raise ValidationAppError(
                "storage.allowed.mime must be a non-empty JSON array",
                details={"key": SETTING_ALLOWED_MIME},
            )
        allowed: set[str] = set()
        for item in raw:
            if not isinstance(item, str) or not item.strip():
                raise ValidationAppError(
                    "storage.allowed.mime entries must be non-empty strings",
                    details={"key": SETTING_ALLOWED_MIME, "value": item},
                )
            allowed.add(item.strip().lower())
        return allowed

    @staticmethod
    def _validate_object_type(object_type: str) -> str:
        cleaned = object_type.strip()
        if not _OBJECT_TYPE_RE.match(cleaned):
            raise ValidationAppError(
                "objectType must be 1–50 chars starting with a letter "
                "(letters, digits, underscore)",
                details={"objectType": object_type},
            )
        return cleaned
