"""Async SQLAlchemy ComplaintRepository (CAPABILITY-004)."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.complaint.domain.models import Complaint
from app.modules.complaint.domain.repositories import ComplaintRepository
from app.modules.complaint.infrastructure.mappers.complaint_mapper import ComplaintMapper
from app.modules.complaint.infrastructure.orm.models import ComplaintORM


class SqlAlchemyComplaintRepository(ComplaintRepository):
    """Complaint persistence via AsyncSession. No business rules. No Queue imports."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, complaint: Complaint) -> Complaint:
        row = ComplaintMapper.to_orm(complaint)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return ComplaintMapper.to_domain(row)

    async def get_by_id(self, complaint_id: uuid.UUID) -> Complaint | None:
        row = await self._session.get(ComplaintORM, complaint_id)
        if row is None:
            return None
        return ComplaintMapper.to_domain(row)

    async def update(self, complaint: Complaint) -> Complaint:
        row = await self._session.get(ComplaintORM, complaint.complaint_id)
        if row is None:
            raise KeyError(f"complaint not found: {complaint.complaint_id}")
        ComplaintMapper.apply_to_orm(complaint, row)
        await self._session.flush()
        await self._session.refresh(row)
        return ComplaintMapper.to_domain(row)

    async def list_by_organization(
        self, organization_id: uuid.UUID
    ) -> tuple[Complaint, ...]:
        stmt = (
            select(ComplaintORM)
            .where(ComplaintORM.organization_id == organization_id)
            .order_by(
                ComplaintORM.created_at.asc(),
                ComplaintORM.complaint_id.asc(),
            )
        )
        result = await self._session.scalars(stmt)
        return tuple(ComplaintMapper.to_domain(row) for row in result.all())

    async def list_by_queue_ticket(
        self, queue_ticket_id: uuid.UUID
    ) -> tuple[Complaint, ...]:
        stmt = (
            select(ComplaintORM)
            .where(ComplaintORM.queue_ticket_id == queue_ticket_id)
            .order_by(
                ComplaintORM.created_at.asc(),
                ComplaintORM.complaint_id.asc(),
            )
        )
        result = await self._session.scalars(stmt)
        return tuple(ComplaintMapper.to_domain(row) for row in result.all())

    async def delete(self, complaint_id: uuid.UUID) -> bool:
        stmt = delete(ComplaintORM).where(ComplaintORM.complaint_id == complaint_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return bool(result.rowcount)


__all__ = ["SqlAlchemyComplaintRepository"]
