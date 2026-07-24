"""Complaint persistence infrastructure wiring (CAPABILITY-004…008).

DI factories for SQLAlchemy repositories. No UnitOfWork.
No REST. Session is supplied by the caller.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.complaint.domain.repositories import (
    AssignmentRepository,
    ComplaintRepository,
    ComplaintSlaRepository,
    EscalationRepository,
    SLAPolicyRepository,
)
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


def get_complaint_repository(session: AsyncSession) -> ComplaintRepository:
    """DI factory — ComplaintRepository bound to the given AsyncSession."""
    return SqlAlchemyComplaintRepository(session)


def get_assignment_repository(session: AsyncSession) -> AssignmentRepository:
    """DI factory — AssignmentRepository bound to the given AsyncSession."""
    return SqlAlchemyAssignmentRepository(session)


def get_escalation_repository(session: AsyncSession) -> EscalationRepository:
    """DI factory — EscalationRepository bound to the given AsyncSession."""
    return SqlAlchemyEscalationRepository(session)


def get_sla_policy_repository(session: AsyncSession) -> SLAPolicyRepository:
    """DI factory — SLAPolicyRepository bound to the given AsyncSession."""
    return SqlAlchemySLAPolicyRepository(session)


def get_complaint_sla_repository(session: AsyncSession) -> ComplaintSlaRepository:
    """DI factory — ComplaintSlaRepository bound to the given AsyncSession."""
    return SqlAlchemyComplaintSlaRepository(session)


__all__ = [
    "get_assignment_repository",
    "get_complaint_repository",
    "get_complaint_sla_repository",
    "get_escalation_repository",
    "get_sla_policy_repository",
]
