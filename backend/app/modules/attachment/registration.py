"""Wire AttachmentService dependencies (CAPABILITY-011).

No event handler — Attachment is a passive metadata BC.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.attachment.repository import AttachmentRepository
from app.modules.attachment.service import AttachmentService
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.service import SettingsService


def build_attachment_service(session: Session) -> AttachmentService:
    """Build AttachmentService with settings-backed LocalStorageProvider."""
    settings = SettingsService(SettingsRepository(session))
    return AttachmentService(
        repository=AttachmentRepository(session),
        settings=settings,
    )
