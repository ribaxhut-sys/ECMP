"""Attachment storage providers (TASK-029)."""

from __future__ import annotations

from app.modules.attachment.storage.base import StorageProvider
from app.modules.attachment.storage.local import LocalStorageProvider

__all__ = ["LocalStorageProvider", "StorageProvider"]
