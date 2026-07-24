"""Complaint domain package (CAPABILITY-004…008)."""

from app.modules.complaint.domain.errors import ComplaintDomainError
from app.modules.complaint.domain.lifecycle import (
    allowed_transitions,
    assert_transition,
    can_transition,
)
from app.modules.complaint.domain.models import (
    AssigneeType,
    Assignment,
    Complaint,
    ComplaintPriority,
    ComplaintSLA,
    ComplaintStatus,
    Escalation,
    EscalationLevel,
    Resolution,
    SLAPolicy,
)
from app.modules.complaint.domain.repositories import (
    AssignmentRepository,
    ComplaintRepository,
    ComplaintSlaRepository,
    EscalationRepository,
    SLAPolicyRepository,
)

__all__ = [
    "AssigneeType",
    "Assignment",
    "AssignmentRepository",
    "Complaint",
    "ComplaintDomainError",
    "ComplaintPriority",
    "ComplaintRepository",
    "ComplaintSLA",
    "ComplaintSlaRepository",
    "ComplaintStatus",
    "Escalation",
    "EscalationLevel",
    "EscalationRepository",
    "Resolution",
    "SLAPolicy",
    "SLAPolicyRepository",
    "allowed_transitions",
    "assert_transition",
    "can_transition",
]
