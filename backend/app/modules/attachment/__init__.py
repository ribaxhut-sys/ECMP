"""CAPABILITY-011 reusable Attachment Management.

Generic metadata BC — attach files to any aggregate (Complaint, Queue,
Notification, …). Physical bytes behind replaceable StorageProvider.
"""

from app.modules.attachment.domain import AggregateType, Attachment, AttachmentStatus
from app.modules.attachment.registration import build_attachment_service

__all__ = [
    "AggregateType",
    "Attachment",
    "AttachmentStatus",
    "build_attachment_service",
]
