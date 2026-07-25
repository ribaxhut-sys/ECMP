"""Local filesystem StorageProvider (CAPABILITY-011).

Layout under configured root (default ``storage/attachments``)::

    yyyy/mm/<uuid>.<ext>
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import BinaryIO

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.attachment.infrastructure.storage_provider import StorageProvider


class LocalStorageProvider(StorageProvider):
    """Store blobs under a configured root with path-traversal guards."""

    def __init__(self, root_path: str) -> None:
        root = Path(root_path).expanduser()
        if not root.is_absolute():
            root = (Path.cwd() / root).resolve()
        else:
            root = root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        self._root = root

    @property
    def provider_name(self) -> str:
        return "local"

    def save(self, *, relative_path: str, data: bytes) -> str:
        safe = self._require_safe_relative(relative_path)
        target = self._resolve_under_root(safe)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return safe

    def open(self, storage_path: str) -> BinaryIO:
        path = self._resolved_existing(storage_path)
        return path.open("rb")

    def read(self, storage_path: str) -> bytes:
        path = self._resolved_existing(storage_path)
        return path.read_bytes()

    def exists(self, storage_path: str) -> bool:
        try:
            self._resolved_existing(storage_path)
            return True
        except (NotFoundError, ValidationAppError):
            return False

    def delete(self, storage_path: str) -> None:
        try:
            path = self._resolved_existing(storage_path)
        except NotFoundError:
            return
        path.unlink(missing_ok=True)

    def _require_safe_relative(self, relative_path: str) -> str:
        raw = (relative_path or "").strip().replace("\\", "/")
        if not raw:
            raise ValidationAppError(
                "storage path is required",
                details={"storagePath": relative_path},
            )
        posix = PurePosixPath(raw)
        if posix.is_absolute() or raw.startswith("/"):
            raise ValidationAppError(
                "storage path must be relative",
                details={"storagePath": relative_path},
            )
        parts = posix.parts
        if not parts or any(p in {"", ".", ".."} for p in parts):
            raise ValidationAppError(
                "storage path must not contain path traversal",
                details={"storagePath": relative_path},
            )
        # Normalize to posix relative (yyyy/mm/uuid.ext).
        return "/".join(parts)

    def _resolve_under_root(self, relative: str) -> Path:
        candidate = (self._root / relative).resolve()
        try:
            candidate.relative_to(self._root)
        except ValueError as exc:
            raise ValidationAppError(
                "storage path escapes storage root",
                details={"storagePath": relative},
            ) from exc
        return candidate

    def _resolved_existing(self, storage_path: str) -> Path:
        raw = (storage_path or "").strip()
        if not raw:
            raise ValidationAppError(
                "storage path is required",
                details={"storagePath": storage_path},
            )
        # Accept legacy absolute paths that still live under root.
        if Path(raw).is_absolute():
            candidate = Path(raw).resolve()
            try:
                candidate.relative_to(self._root)
            except ValueError as exc:
                raise ValidationAppError(
                    "storage path escapes storage root",
                    details={"storagePath": storage_path},
                ) from exc
        else:
            safe = self._require_safe_relative(raw)
            candidate = self._resolve_under_root(safe)
        if not candidate.is_file():
            raise NotFoundError("Attachment file not found in storage")
        return candidate
