"""Async SQLAlchemy AssignmentRepository (CAPABILITY-006).

Persistence only — no business rules.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.complaint.domain.models import Assignment
from app.modules.complaint.domain.repositories import AssignmentRepository
from app.modules.complaint.infrastructure.mappers.assignment_mapper import (
    AssignmentMapper,
)
from app.modules.complaint.infrastructure.orm.models import AssignmentORM


class SqlAlchemyAssignmentRepository(AssignmentRepository):
    """Assignment persistence via AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, assignment: Assignment) -> Assignment:
        row = AssignmentMapper.to_orm(assignment)
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return AssignmentMapper.to_domain(row)

    async def update(self, assignment: Assignment) -> Assignment:
        row = await self._session.get(AssignmentORM, assignment.assignment_id)
        if row is None:
            raise KeyError(f"assignment not found: {assignment.assignment_id}")
        AssignmentMapper.apply_to_orm(assignment, row)
        await self._session.flush()
        await self._session.refresh(row)
        return AssignmentMapper.to_domain(row)

    async def get_by_id(self, assignment_id: uuid.UUID) -> Assignment | None:
        row = await self._session.get(AssignmentORM, assignment_id)
        if row is None:
            return None
        return AssignmentMapper.to_domain(row)

    async def get_active_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> Assignment | None:
        stmt = (
            select(AssignmentORM)
            .where(
                AssignmentORM.complaint_id == complaint_id,
                AssignmentORM.is_active.is_(True),
            )
            .limit(1)
        )
        result = await self._session.scalars(stmt)
        row = result.first()
        if row is None:
            return None
        return AssignmentMapper.to_domain(row)

    async def list_by_complaint(
        self, complaint_id: uuid.UUID
    ) -> tuple[Assignment, ...]:
        stmt = (
            select(AssignmentORM)
            .where(AssignmentORM.complaint_id == complaint_id)
            .order_by(
                AssignmentORM.assigned_at.asc(),
                AssignmentORM.assignment_id.asc(),
            )
        )
        result = await self._session.scalars(stmt)
        return tuple(AssignmentMapper.to_domain(row) for row in result.all())


__all__ = ["SqlAlchemyAssignmentRepository"]
