"""CAPABILITY-012 Complaint search provider (SQLAlchemy / PostgreSQL).

Reuses ``Complaint`` / related ORM models — does not duplicate ComplaintRepository
write paths and does not mutate domain state.
"""

from __future__ import annotations

from sqlalchemy import Select, and_, exists, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.core.enums import ComplaintStatus
from app.models import (
    Complaint,
    ComplaintAssignment,
    ComplaintEscalation,
    Customer,
    SlaRecord,
)
from app.modules.search.domain.enums import ComplaintSortField, SortOrder
from app.modules.search.domain.filters import ComplaintSearchFilters
from app.modules.search.providers.base import SearchProvider


class ComplaintSearchProvider(SearchProvider[ComplaintSearchFilters, Complaint]):
    """Filter / sort / paginate complaints with joins (no N+1)."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def search(self, filters: ComplaintSearchFilters) -> tuple[list[Complaint], int]:
        page = max(1, filters.page)
        page_size = max(1, min(filters.page_size, 100))

        base = self._filtered_query(filters)
        count_stmt = select(func.count()).select_from(base.subquery())
        total = int(self._session.scalar(count_stmt) or 0)

        ordered = self._apply_sort(base, filters.sort, filters.order)
        stmt = ordered.offset((page - 1) * page_size).limit(page_size)
        items = list(self._session.scalars(stmt).unique().all())
        return items, total

    def _filtered_query(self, filters: ComplaintSearchFilters) -> Select[tuple[Complaint]]:
        stmt: Select[tuple[Complaint]] = select(Complaint).where(
            Complaint.deleted_at.is_(None)
        )

        if filters.status is not None:
            stmt = stmt.where(Complaint.status == filters.status)
        if filters.priority is not None:
            stmt = stmt.where(Complaint.priority == filters.priority)
        if filters.category is not None:
            stmt = stmt.where(Complaint.category == filters.category)
        if filters.branch_id is not None:
            stmt = stmt.where(Complaint.branch_id == filters.branch_id)
        if filters.created_by is not None:
            stmt = stmt.where(Complaint.created_by == filters.created_by)
        if filters.created_from is not None:
            stmt = stmt.where(Complaint.created_at >= filters.created_from)
        if filters.created_to is not None:
            stmt = stmt.where(Complaint.created_at <= filters.created_to)

        if filters.assigned_to is not None:
            assignment = aliased(ComplaintAssignment)
            stmt = stmt.join(
                assignment,
                and_(
                    assignment.complaint_id == Complaint.id,
                    assignment.is_current.is_(True),
                    assignment.deleted_at.is_(None),
                    assignment.assignee_id == filters.assigned_to,
                ),
            )

        if filters.sla_status is not None:
            sla = aliased(SlaRecord)
            stmt = stmt.join(
                sla,
                and_(
                    sla.complaint_id == Complaint.id,
                    sla.overall_status == filters.sla_status,
                ),
            )

        if filters.escalated is True:
            esc_exists = exists(
                select(1).where(
                    ComplaintEscalation.complaint_id == Complaint.id,
                    ComplaintEscalation.deleted_at.is_(None),
                )
            )
            stmt = stmt.where(
                or_(
                    Complaint.status == ComplaintStatus.ESCALATED.value,
                    esc_exists,
                )
            )
        elif filters.escalated is False:
            esc_exists = exists(
                select(1).where(
                    ComplaintEscalation.complaint_id == Complaint.id,
                    ComplaintEscalation.deleted_at.is_(None),
                )
            )
            stmt = stmt.where(
                and_(
                    Complaint.status != ComplaintStatus.ESCALATED.value,
                    ~esc_exists,
                )
            )

        if filters.keyword:
            keyword = filters.keyword.strip()
            if keyword:
                pattern = f"%{keyword}%"
                customer = aliased(Customer)
                # Outer join customer for reporter-name match; keep complaints
                # without customer when other keyword fields match.
                stmt = stmt.outerjoin(
                    customer,
                    and_(
                        customer.id == Complaint.customer_id,
                        customer.deleted_at.is_(None),
                    ),
                ).where(
                    or_(
                        Complaint.complaint_number.ilike(pattern),
                        Complaint.subject.ilike(pattern),
                        Complaint.description.ilike(pattern),
                        customer.full_name.ilike(pattern),
                    )
                )

        return stmt.distinct()

    def _apply_sort(
        self,
        stmt: Select[tuple[Complaint]],
        sort: ComplaintSortField,
        order: SortOrder,
    ) -> Select[tuple[Complaint]]:
        descending = order == SortOrder.DESC

        if sort == ComplaintSortField.SLA_DUE_DATE:
            sla = aliased(SlaRecord)
            stmt = stmt.outerjoin(sla, sla.complaint_id == Complaint.id)
            col = sla.overall_due_at
            # Nulls last for both directions keeps pages stable.
            ordered = col.desc().nulls_last() if descending else col.asc().nulls_last()
            return stmt.order_by(ordered, Complaint.id.asc())

        column_map = {
            ComplaintSortField.CREATED_AT: Complaint.created_at,
            ComplaintSortField.UPDATED_AT: Complaint.updated_at,
            ComplaintSortField.PRIORITY: Complaint.priority,
            ComplaintSortField.STATUS: Complaint.status,
        }
        col = column_map[sort]
        ordered = col.desc() if descending else col.asc()
        return stmt.order_by(ordered, Complaint.id.asc())
