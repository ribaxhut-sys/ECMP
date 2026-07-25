"""CAPABILITY-011 Attachment domain package."""

from app.modules.attachment.domain.entity import Attachment
from app.modules.attachment.domain.enums import AggregateType, AttachmentStatus

__all__ = [
    "AggregateType",
    "Attachment",
    "AttachmentStatus",
]
