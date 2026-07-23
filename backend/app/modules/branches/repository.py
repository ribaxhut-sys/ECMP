"""Branch persistence repository (reference list)."""

from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models import Branch


class BranchRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_page(
        self,
        *,
        page: int,
        page_size: int,
        q: str | None = None,
    ) -> tuple[list[Branch], int]:
        filters = [
            Branch.deleted_at.is_(None),
            Branch.is_active.is_(True),
        ]
        if q:
            term = f"%{q.strip()}%"
            filters.append(
                or_(
                    Branch.code.ilike(term),
                    Branch.name.ilike(term),
                )
            )

        count_stmt = select(func.count()).select_from(Branch).where(*filters)
        total = int(self._session.scalar(count_stmt) or 0)

        stmt: Select[tuple[Branch]] = (
            select(Branch)
            .where(*filters)
            .order_by(Branch.name.asc(), Branch.code.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self._session.scalars(stmt).all())
        return items, total
