"""Complaint repository adapters (CAPABILITY-004…008)."""

from app.modules.complaint.infrastructure.repositories.assignment_repository import (
    SqlAlchemyAssignmentRepository,
)
from app.modules.complaint.infrastructure.repositories.complaint_repository import (
    SqlAlchemyComplaintRepository,
)
from app.modules.complaint.infrastructure.repositories.escalation_repository import (
    SqlAlchemyEscalationRepository,
)
from app.modules.complaint.infrastructure.repositories.sla_repository import (
    SqlAlchemyComplaintSlaRepository,
    SqlAlchemySLAPolicyRepository,
)

__all__ = [
    "SqlAlchemyAssignmentRepository",
    "SqlAlchemyComplaintRepository",
    "SqlAlchemyComplaintSlaRepository",
    "SqlAlchemyEscalationRepository",
    "SqlAlchemySLAPolicyRepository",
]
