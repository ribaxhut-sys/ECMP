"""Async SQLAlchemy SLAPolicy + ComplaintSLA repositories (CAPABILITY-008).

Persistence only — no business rules.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.complaint.domain.models import ComplaintSLA, SLAPolicy
from app.modules.complaint.domain.repositories import (
    ComplaintSlaRepository,
    SLAPolicyRepository,
)
from app.modules.complaint.infrastructure.mappers.sla_mapper import (
    ComplaintSlaMapper,
    SLAPolicyMapper,
)
from app.modules.complaint.infrastructure.orm.models import (
    ComplaintSlaORM,
    SLAPolicyORM,
)


class SqlAlchemySLAPolicyRepository(SLAPolicyRepository):
    """SLAPolicy persistence via AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, policy_id: uuid.UUID) -> SLAPolicy | None:
        row = await self._session.get(SLAPolicyORM, policy_id)
        if row is None:
            return None
        return SLAPolicyMapper.to_domain(row)

    async def get_default(self) -> SLAPolicy | None:
        stmt = (
            select(SLAPolicyORM)
            .where(SLAPolicyORM.is_default.is_(True))
            .limit(1)
        )
        result = await self._session.scalars(stmt)
        row = result.first()
        if row is None:
            return None
        return SLAPolicyMapper.to_domain(row)

    async def add(self, policy: SLAPolicy) -> SLAPolicy:
        row = SLAPolicyMapper.to_orm(policy)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return SLAPolicyMapper.to_domain(row)


class SqlAlchemyComplaintSlaRepository(ComplaintSlaRepository):
    """ComplaintSLA persistence via AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, sla: ComplaintSLA) -> ComplaintSLA:
        row = ComplaintSlaMapper.to_orm(sla)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return ComplaintSlaMapper.to_domain(row)

    async def update(self, sla: ComplaintSLA) -> ComplaintSLA:
        row = await self._session.get(ComplaintSlaORM, sla.sla_id)
        if row is None:
            raise KeyError(f"SLA not found: {sla.sla_id}")
        ComplaintSlaMapper.apply_to_orm(sla, row)
        await self._session.flush()
        await self._session.refresh(row)
        return ComplaintSlaMapper.to_domain(row)

    async def get_by_id(self, sla_id: uuid.UUID) -> ComplaintSLA | None:
        row = await self._session.get(ComplaintSlaORM, sla_id)
        if row is None:
            return None
        return ComplaintSlaMapper.to_domain(row)

    async def get_active_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> ComplaintSLA | None:
        stmt = (
            select(ComplaintSlaORM)
            .where(
                ComplaintSlaORM.complaint_id == complaint_id,
                ComplaintSlaORM.is_active.is_(True),
            )
            .limit(1)
        )
        result = await self._session.scalars(stmt)
        row = result.first()
        if row is None:
            return None
        return ComplaintSlaMapper.to_domain(row)

    async def get_latest_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> ComplaintSLA | None:
        stmt = (
            select(ComplaintSlaORM)
            .where(ComplaintSlaORM.complaint_id == complaint_id)
            .order_by(
                ComplaintSlaORM.is_active.desc(),
                ComplaintSlaORM.started_at.desc(),
                ComplaintSlaORM.sla_id.desc(),
            )
            .limit(1)
        )
        result = await self._session.scalars(stmt)
        row = result.first()
        if row is None:
            return None
        return ComplaintSlaMapper.to_domain(row)


__all__ = [
    "SqlAlchemyComplaintSlaRepository",
    "SqlAlchemySLAPolicyRepository",
]
