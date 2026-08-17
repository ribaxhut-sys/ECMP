"""CAPABILITY-011 Attachment Management service.

Generic platform upload / metadata / download / logical delete.
Aggregate-agnostic via aggregate_type + aggregate_id.
All file I/O goes through StorageProvider.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from datetime import UTC, datetime
from pathlib import PurePosixPath

from app.core.errors import NotFoundError, ValidationAppError
from app.core.schemas import PageMeta
from app.core.user_messages import m
from app.modules.attachment.domain.entity import Attachment
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus
from app.modules.attachment.infrastructure.local_storage import LocalStorageProvider
from app.modules.attachment.infrastructure.storage_provider import StorageProvider
from app.modules.attachment.repository import AttachmentRepository
from app.modules.attachment.schemas import AttachmentResponse
from app.modules.settings.service import SettingsService

# Setting keys (seeded by migration 0017; root path updated in 0035).
SETTING_STORAGE_PROVIDER = "storage.provider"
SETTING_STORAGE_ROOT_PATH = "storage.root.path"
SETTING_MAX_UPLOAD_MB = "storage.max.upload.mb"
SETTING_ALLOWED_MIME = "storage.allowed.mime"

_DEFAULT_PROVIDER = "local"
_DEFAULT_ROOT_PATH = "storage/attachments"
_DEFAULT_MAX_UPLOAD_MB = 50
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
    "application/zip",
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
    "application/zip": frozenset({".zip"}),
}

# ZIP is stored as an opaque blob — never extracted (zip-bomb / path traversal).
_ZIP_MAGIC_PREFIXES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
_ZIP_MIME_ALIASES = frozenset(
    {
        "application/zip",
        "application/x-zip",
        "application/x-zip-compressed",
        "application/zip-compressed",
    }
)

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
                m("storage.root_path_not_empty"),
                details={"key": SETTING_STORAGE_ROOT_PATH},
            )
        # Lab guard: pytest fixtures must not leave /tmp/pytest-* in shared DB.
        normalized = root.replace("\\", "/")
        if "/pytest-" in normalized or normalized.startswith("/tmp/pytest"):
            root = _DEFAULT_ROOT_PATH
        return LocalStorageProvider(root)
    raise ValidationAppError(
        f"penyedia storage tidak didukung: {provider}",
        details={"key": SETTING_STORAGE_PROVIDER, "value": provider},
    )


def sanitize_filename(raw_name: str | None) -> str:
    """Strip path components and unsafe characters from a client filename."""
    if raw_name is None or not raw_name.strip():
        raise ValidationAppError(
            m("storage.filename_required"),
            details={"filename": raw_name},
        )
    name = PurePosixPath(raw_name.replace("\\", "/")).name
    name = name.strip().strip(".")
    name = _UNSAFE_FILENAME_RE.sub("_", name)
    name = name.replace("..", "_")
    if not name or name in {".", ".."}:
        raise ValidationAppError(
            m("storage.filename_invalid_sanitized"),
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
            m("storage.file_extension_too_long"),
            details={"extension": suffix},
        )
    return suffix


def looks_like_zip(data: bytes) -> bool:
    """True when bytes start with a ZIP local/empty/spanned header (PK)."""
    return any(data.startswith(prefix) for prefix in _ZIP_MAGIC_PREFIXES)


def normalize_upload_mime(
    *,
    content_type: str | None,
    filename: str | None,
    data: bytes,
) -> str:
    """Canonical MIME for upload allowlists.

    ZIP aliases (Windows ``x-zip-compressed``, empty/octet-stream + ``.zip``)
    become ``application/zip``. ZIP is never extracted — only magic-checked.
    """
    mime = (content_type or "").strip().lower() or "application/octet-stream"
    extension = _extension_of(filename) if filename else None
    zip_claimed = mime in _ZIP_MIME_ALIASES or (
        mime == "application/octet-stream" and extension == ".zip"
    )
    if zip_claimed:
        if not looks_like_zip(data):
            raise ValidationAppError(
                m("storage.zip_invalid"),
                details={"mimeType": mime, "extension": extension},
            )
        return "application/zip"
    return mime


def _storage_relative_path(*, file_name: str, uploaded_at: datetime) -> str:
    """Build ``yyyy/mm/<uuid.ext>`` relative path under storage root."""
    return f"{uploaded_at.year:04d}/{uploaded_at.month:02d}/{file_name}"


def _to_response(entity: Attachment) -> AttachmentResponse:
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
        accessLevel=entity.access_level,  # type: ignore[arg-type]
        uploadedOrgUnitId=entity.uploaded_org_unit_id,
    )


class AttachmentService:
    """Upload / metadata / download / logical delete for platform attachments."""

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
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        filename: str | None,
        content_type: str | None,
        data: bytes,
        uploaded_by: uuid.UUID | None,
        allowed_mime_types: set[str] | None = None,
        max_bytes: int | None = None,
        commit: bool = True,
    ) -> AttachmentResponse:
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

        safe_name = sanitize_filename(filename)
        extension = _extension_of(safe_name)

        if not data:
            raise ValidationAppError(
                m("storage.file_empty"),
                details={"sizeBytes": 0},
            )

        mime_type = normalize_upload_mime(
            content_type=content_type, filename=safe_name, data=data
        )

        if max_bytes is None:
            max_mb = self._settings.get_int(
                SETTING_MAX_UPLOAD_MB, default=_DEFAULT_MAX_UPLOAD_MB
            )
            if max_mb < 1:
                raise ValidationAppError(
                    m("storage.max_upload_mb_min"),
                    details={"key": SETTING_MAX_UPLOAD_MB, "value": max_mb},
                )
            max_bytes = max_mb * 1024 * 1024
        elif max_bytes < 1:
            raise ValidationAppError(
                m("storage.max_bytes_min"),
                details={"maxBytes": max_bytes},
            )
        size_bytes = len(data)
        if size_bytes > max_bytes:
            raise ValidationAppError(
                m("storage.file_exceeds_max_size"),
                details={
                    "sizeBytes": size_bytes,
                    "maxBytes": max_bytes,
                },
            )

        allowed = allowed_mime_types or self._allowed_mime_types()
        if mime_type not in allowed:
            raise ValidationAppError(
                m("storage.mime_not_allowed"),
                details={"mimeType": mime_type, "allowed": sorted(allowed)},
            )

        expected_exts = _MIME_EXTENSIONS.get(mime_type)
        if expected_exts is not None:
            if extension is None or extension not in expected_exts:
                raise ValidationAppError(
                    m("storage.file_extension_mismatch"),
                    details={
                        "extension": extension,
                        "mimeType": mime_type,
                        "expectedExtensions": sorted(expected_exts),
                    },
                )

        checksum = hashlib.sha256(data).hexdigest()
        file_name = f"{uuid.uuid4().hex}{extension or ''}"
        uploaded_at = datetime.now(UTC)
        relative_path = _storage_relative_path(
            file_name=file_name, uploaded_at=uploaded_at
        )

        try:
            storage_path = self._storage.save(relative_path=relative_path, data=data)
        except Exception:
            self._repo.rollback()
            raise

        entity = Attachment.create(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            file_name=file_name,
            original_name=safe_name,
            mime_type=mime_type,
            extension=extension,
            size_bytes=size_bytes,
            storage_provider=self._storage.provider_name,
            storage_path=storage_path,
            checksum_sha256=checksum,
            uploaded_by=uploaded_by,
            uploaded_at=uploaded_at,
            status=AttachmentStatus.AVAILABLE.value,
        )
        try:
            self._repo.add(entity)
            if commit:
                self._repo.commit()
            else:
                self._repo.flush()
        except Exception:
            try:
                self._storage.delete(storage_path)
            except Exception:
                pass
            self._repo.rollback()
            raise

        return _to_response(entity)

    def rebind(
        self,
        attachment_id: uuid.UUID,
        *,
        aggregate_type: str,
        aggregate_id: uuid.UUID,
        commit: bool = True,
    ) -> AttachmentResponse:
        """Move metadata bind to a new aggregate (Batch 1 staging → Complaint)."""
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
        entity = self._require(attachment_id, include_deleted=False)
        entity.aggregate_type = aggregate_type
        entity.aggregate_id = aggregate_id
        self._repo.save(entity)
        if commit:
            self._repo.commit()
        else:
            self._repo.flush()
        return _to_response(entity)

    def find_by_checksum(
        self, checksum_sha256: str, *, include_deleted: bool = False
    ) -> AttachmentResponse | None:
        entity = self._repo.find_by_checksum(
            checksum_sha256.strip().lower(), include_deleted=include_deleted
        )
        return _to_response(entity) if entity is not None else None

    def get(self, attachment_id: uuid.UUID) -> AttachmentResponse:
        return _to_response(self._require(attachment_id))

    def list(
        self,
        *,
        aggregate_type: str | None = None,
        aggregate_id: uuid.UUID | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AttachmentResponse], PageMeta]:
        if aggregate_type is not None:
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
        rows, total = self._repo.list(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            page=page,
            page_size=page_size,
        )
        return (
            [_to_response(r) for r in rows],
            PageMeta(page=page, pageSize=page_size, totalItems=total),
        )

    def list_for_complaint(
        self,
        complaint_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 100,
    ) -> tuple[list[AttachmentResponse], PageMeta]:
        return self.list(
            aggregate_type=AggregateType.COMPLAINT.value,
            aggregate_id=complaint_id,
            page=page,
            page_size=page_size,
        )

    def download(self, attachment_id: uuid.UUID) -> tuple[Attachment, bytes]:
        entity = self._require(attachment_id)
        data = self._storage.read(entity.storage_path)
        return entity, data

    def soft_delete(
        self, attachment_id: uuid.UUID, *, commit: bool = True
    ) -> None:
        """Logical delete (status=DELETED). Physical blob retained."""
        entity = self._require(attachment_id)
        entity.mark_deleted()
        self._repo.save(entity)
        if commit:
            self._repo.commit()
        else:
            self._repo.flush()

    def _require(
        self, attachment_id: uuid.UUID, *, include_deleted: bool = False
    ) -> Attachment:
        entity = self._repo.get(attachment_id, include_deleted=include_deleted)
        if entity is None:
            raise NotFoundError(m("attachment.not_found"))
        return entity

    def _allowed_mime_types(self) -> set[str]:
        raw = self._settings.get_json(
            SETTING_ALLOWED_MIME, default=list(_DEFAULT_ALLOWED_MIME)
        )
        if not isinstance(raw, list) or not raw:
            raise ValidationAppError(
                m("storage.allowed_mime_non_empty_array"),
                details={"key": SETTING_ALLOWED_MIME},
            )
        allowed: set[str] = set()
        for item in raw:
            if not isinstance(item, str) or not item.strip():
                raise ValidationAppError(
                    m("storage.allowed_mime_empty_strings"),
                    details={"key": SETTING_ALLOWED_MIME, "value": item},
                )
            allowed.add(item.strip().lower())
        return allowed
