"""Complaint persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import AuditLog, Branch, Complaint, Customer


class ComplaintRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, complaint_id: uuid.UUID) -> Complaint | None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.deleted_at.is_(None),
        )
        return self._session.scalar(stmt)

    def customer_exists(self, customer_id: uuid.UUID) -> bool:
        stmt = select(Customer.id).where(
            Customer.id == customer_id,
            Customer.deleted_at.is_(None),
        )
        return self._session.scalar(stmt) is not None

    def branch_exists(self, branch_id: uuid.UUID) -> bool:
        stmt = select(Branch.id).where(
            Branch.id == branch_id,
            Branch.deleted_at.is_(None),
        )
        return self._session.scalar(stmt) is not None

    def add(self, complaint: Complaint) -> Complaint:
        self._session.add(complaint)
        self._session.flush()
        return complaint

    def add_audit_log(
        self,
        *,
        actor_user_id: uuid.UUID | None,
        action: str,
        entity_id: uuid.UUID,
        new_value: dict[str, Any],
        old_value: dict[str, Any] | None = None,
        occurred_at: datetime | None = None,
    ) -> AuditLog:
        from datetime import UTC

        when = occurred_at or datetime.now(UTC)
        if when.tzinfo is None:
            when = when.replace(tzinfo=UTC)

        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            entity_type="Complaint",
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            occurred_at=when,
        )
        self._session.add(entry)
        self._session.flush()
        return entry

    def list_page(
        self,
        *,
        page: int,
        page_size: int,
        status: str | None = None,
        priority: str | None = None,
        customer_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
    ) -> tuple[list[Complaint], int]:
        filters = [Complaint.deleted_at.is_(None)]
        if status is not None:
            filters.append(Complaint.status == status)
        if priority is not None:
            filters.append(Complaint.priority == priority)
        if customer_id is not None:
            filters.append(Complaint.customer_id == customer_id)
        if branch_id is not None:
            filters.append(Complaint.branch_id == branch_id)

        count_stmt = select(func.count()).select_from(Complaint).where(*filters)
        total = int(self._session.scalar(count_stmt) or 0)

        stmt: Select[tuple[Complaint]] = (
            select(Complaint)
            .where(*filters)
            .order_by(Complaint.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self._session.scalars(stmt).all())
        return items, total

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, complaint: Complaint) -> Complaint:
        self._session.refresh(complaint)
        return complaint
