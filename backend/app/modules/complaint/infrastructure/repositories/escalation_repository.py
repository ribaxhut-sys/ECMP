"""Async SQLAlchemy EscalationRepository (CAPABILITY-007).

Persistence only — no business rules.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.complaint.domain.models import Escalation
from app.modules.complaint.domain.repositories import EscalationRepository
from app.modules.complaint.infrastructure.mappers.escalation_mapper import (
    EscalationMapper,
)
from app.modules.complaint.infrastructure.orm.models import EscalationORM


class SqlAlchemyEscalationRepository(EscalationRepository):
    """Escalation persistence via AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, escalation: Escalation) -> Escalation:
        row = EscalationMapper.to_orm(escalation)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return EscalationMapper.to_domain(row)

    async def update(self, escalation: Escalation) -> Escalation:
        row = await self._session.get(EscalationORM, escalation.escalation_id)
        if row is None:
            raise KeyError(f"escalation not found: {escalation.escalation_id}")
        EscalationMapper.apply_to_orm(escalation, row)
        await self._session.flush()
        await self._session.refresh(row)
        return EscalationMapper.to_domain(row)

    async def get_by_id(self, escalation_id: uuid.UUID) -> Escalation | None:
        row = await self._session.get(EscalationORM, escalation_id)
        if row is None:
            return None
        return EscalationMapper.to_domain(row)

    async def get_current_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> Escalation | None:
        stmt = (
            select(EscalationORM)
            .where(
                EscalationORM.complaint_id == complaint_id,
                EscalationORM.is_current.is_(True),
            )
            .limit(1)
        )
        result = await self._session.scalars(stmt)
        row = result.first()
        if row is None:
            return None
        return EscalationMapper.to_domain(row)

    async def list_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> tuple[Escalation, ...]:
        stmt = (
            select(EscalationORM)
            .where(EscalationORM.complaint_id == complaint_id)
            .order_by(
                EscalationORM.escalated_at.asc(),
                EscalationORM.escalation_id.asc(),
            )
        )
        result = await self._session.scalars(stmt)
        return tuple(EscalationMapper.to_domain(row) for row in result.all())


__all__ = ["SqlAlchemyEscalationRepository"]
