"""Repository port for Case Aggregate (Epic 3)."""

from __future__ import annotations

from typing import Protocol

from app.modules.cm_case.domain.aggregate import CaseAggregate


class ParentComplaintRef:
    """Read model for parent Complaint Aggregate (Batch-1)."""

    __slots__ = (
        "complaint_id",
        "complaint_number",
        "customer_id",
        "status",
        "case_created",
        "case_count",
        "owning_unit_id",
        "created_by",
    )

    def __init__(
        self,
        *,
        complaint_id: str,
        complaint_number: str,
        customer_id: str,
        status: str,
        case_created: bool,
        case_count: int,
        owning_unit_id: str | None = None,
        created_by: str | None = None,
    ) -> None:
        self.complaint_id = complaint_id
        self.complaint_number = complaint_number
        self.customer_id = customer_id
        self.status = status
        self.case_created = case_created
        self.case_count = case_count
        # F4 owner rule — Complaint's owning unit (Batch-1, immutable since
        # creation) is snapshotted onto every Case created under it.
        self.owning_unit_id = owning_unit_id
        # F4 creator SoD — user who created the Complaint (not the Case).
        self.created_by = created_by


class CaseRepository(Protocol):
    def get_parent_complaint(self, complaint_id: str) -> ParentComplaintRef | None:
        """Load parent Complaint by UUID or complaint number."""

    def count_cases(self, complaint_id: str) -> int:
        ...

    def next_case_number(self, year: int) -> str:
        """Allocate next ``CASE-YYYY-NNNNNN`` (BQ-004)."""

    def save(self, case: CaseAggregate) -> CaseAggregate:
        ...

    def get(self, case_id: str) -> CaseAggregate | None:
        """Load by UUID or Case Number."""

    def list_summaries(
        self,
        *,
        visibility: str,
        actor_id: str,
        org_unit_id: str | None,
        pusat_unit_codes: frozenset[str],
        complaint_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list, int]:
        """DEC-024 visibility-scoped Case rows (ORM or equivalent) + total."""

    def mark_complaint_in_progress(self, complaint_id: str) -> None:
        """First Case effect: Complaint REGISTERED → IN_PROGRESS; case_created=True."""

    def sync_complaint_status_from_cases(self, complaint_id: str) -> str | None:
        """Align Aggregate status to Case set (Mode A product rule 2026-08-12).

        - Any non-terminal Case → Complaint IN_PROGRESS
        - All Cases terminal (CLOSED/CANCELLED) and at least one Case → CLOSED
          (+ intake_disposition BRANCH_CLOSED when unset / branch path)
        Returns the Aggregate status after sync, or None if parent missing.
        """

    def commit(self) -> None:
        ...
