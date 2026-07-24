"""Complaint Context Foundation — public exports (TASK-044)."""

from app.modules.complaint_context.models import (
    AssigneeRef,
    AssignmentSnapshot,
    ComplaintContext,
    ComplaintSnapshot,
    SlaSnapshot,
    SourceRef,
    TargetRef,
)
from app.modules.complaint_context.service import ComplaintContextService

__all__ = [
    "AssigneeRef",
    "AssignmentSnapshot",
    "ComplaintContext",
    "ComplaintContextService",
    "ComplaintSnapshot",
    "SlaSnapshot",
    "SourceRef",
    "TargetRef",
]
