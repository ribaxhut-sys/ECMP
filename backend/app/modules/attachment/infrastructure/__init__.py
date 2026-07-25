"""CAPABILITY-011 Attachment infrastructure (storage providers)."""

from app.modules.attachment.infrastructure.local_storage import LocalStorageProvider
from app.modules.attachment.infrastructure.storage_provider import StorageProvider

__all__ = ["LocalStorageProvider", "StorageProvider"]
