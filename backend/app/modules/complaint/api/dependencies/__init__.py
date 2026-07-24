"""FastAPI dependencies for Complaint REST (CAPABILITY-004…008).

RequestContext comes from Core — Complaint does not own execution context.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import RequestContext, get_request_context
from app.db.async_session import get_async_session_factory
from app.modules.complaint.application.services import (
    ComplaintAssignmentApplicationService,
    ComplaintCrudApplicationService,
    ComplaintDomainService,
    ComplaintEscalationApplicationService,
    ComplaintProcessingApplicationService,
    ComplaintSLAApplicationService,
    get_complaint_domain_service,
)
from app.modules.complaint.infrastructure import (
    get_assignment_repository,
    get_complaint_repository,
    get_complaint_sla_repository,
    get_escalation_repository,
    get_sla_policy_repository,
)


async def get_complaint_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield AsyncSession; commit on success, rollback on failure."""
    session = get_async_session_factory()()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def get_complaint_crud_service(
    session: Annotated[AsyncSession, Depends(get_complaint_db_session)],
    domain: Annotated[ComplaintDomainService, Depends(get_complaint_domain_service)],
) -> ComplaintCrudApplicationService:
    """Wire Controllers → Application → Repository Interface → SQLAlchemy."""
    return ComplaintCrudApplicationService(
        complaints=get_complaint_repository(session),
        domain=domain,
    )


def get_complaint_processing_service(
    session: Annotated[AsyncSession, Depends(get_complaint_db_session)],
    domain: Annotated[ComplaintDomainService, Depends(get_complaint_domain_service)],
) -> ComplaintProcessingApplicationService:
    """Wire Controllers → Processing Application → Repository Interface."""
    return ComplaintProcessingApplicationService(
        complaints=get_complaint_repository(session),
        domain=domain,
        slas=get_complaint_sla_repository(session),
    )


def get_complaint_assignment_service(
    session: Annotated[AsyncSession, Depends(get_complaint_db_session)],
    domain: Annotated[ComplaintDomainService, Depends(get_complaint_domain_service)],
) -> ComplaintAssignmentApplicationService:
    """Wire Controllers → Assignment Application → Repository Interfaces."""
    return ComplaintAssignmentApplicationService(
        complaints=get_complaint_repository(session),
        assignments=get_assignment_repository(session),
        domain=domain,
    )


def get_complaint_escalation_service(
    session: Annotated[AsyncSession, Depends(get_complaint_db_session)],
    domain: Annotated[ComplaintDomainService, Depends(get_complaint_domain_service)],
) -> ComplaintEscalationApplicationService:
    """Wire Controllers → Escalation Application → Repository Interfaces."""
    return ComplaintEscalationApplicationService(
        complaints=get_complaint_repository(session),
        escalations=get_escalation_repository(session),
        domain=domain,
    )


def get_complaint_sla_service(
    session: Annotated[AsyncSession, Depends(get_complaint_db_session)],
    domain: Annotated[ComplaintDomainService, Depends(get_complaint_domain_service)],
) -> ComplaintSLAApplicationService:
    """Wire Controllers → SLA Application → Repository Interfaces."""
    return ComplaintSLAApplicationService(
        complaints=get_complaint_repository(session),
        slas=get_complaint_sla_repository(session),
        policies=get_sla_policy_repository(session),
        domain=domain,
    )


__all__ = [
    "RequestContext",
    "get_complaint_assignment_service",
    "get_complaint_crud_service",
    "get_complaint_db_session",
    "get_complaint_escalation_service",
    "get_complaint_processing_service",
    "get_complaint_sla_service",
    "get_request_context",
]
