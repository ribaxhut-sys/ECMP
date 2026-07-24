"""Local filesystem StorageProvider implementation (TASK-029)."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.attachment.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    """Store blobs under a configured root directory with path-traversal guards."""

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

    def save(self, *, stored_filename: str, data: bytes) -> str:
        safe_name = self._require_safe_filename(stored_filename)
        target = self._resolve_under_root(safe_name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        # Persist relative path so relocating root still resolves.
        return safe_name

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

    def _require_safe_filename(self, stored_filename: str) -> str:
        name = stored_filename.strip()
        if not name:
            raise ValidationAppError(
                "stored filename is required",
                details={"storedFilename": stored_filename},
            )
        if name in {".", ".."} or "/" in name or "\\" in name:
            raise ValidationAppError(
                "stored filename must not contain path separators",
                details={"storedFilename": stored_filename},
            )
        if Path(name).name != name:
            raise ValidationAppError(
                "stored filename must be a basename",
                details={"storedFilename": stored_filename},
            )
        return name

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
        # Accept both basename handles and legacy absolute paths under root.
        raw = storage_path.strip()
        if not raw:
            raise ValidationAppError(
                "storage path is required",
                details={"storagePath": storage_path},
            )
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
            safe = self._require_safe_filename(raw)
            candidate = self._resolve_under_root(safe)
        if not candidate.is_file():
            raise NotFoundError("Attachment file not found in storage")
        return candidate
