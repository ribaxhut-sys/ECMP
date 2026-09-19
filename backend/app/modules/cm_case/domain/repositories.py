"""Repository port for Case Aggregate (Epic 3)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
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
        "hq_accepted_at",
        "intake_disposition",
        "hq_accepted_by",
        "hq_destination_set_by",
        "proposed_by",
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
        hq_accepted_at: datetime | None = None,
        intake_disposition: str | None = None,
        hq_accepted_by: str | None = None,
        hq_destination_set_by: str | None = None,
        proposed_by: str | None = None,
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
        self.hq_accepted_at = hq_accepted_at
        self.intake_disposition = intake_disposition
        # Handover actors — who at Pusat took this, who at the branch
        # proposed it. Source for the Case handler column.
        self.hq_accepted_by = hq_accepted_by
        self.hq_destination_set_by = hq_destination_set_by
        self.proposed_by = proposed_by


@dataclass(frozen=True)
class ParentHandoff:
    """Handover actors stamped on the parent Complaint (Batch-1 columns).

    Read model for the Case handler column — see
    ``application.current_handler.resolve_current_handler``.
    """

    intake_disposition: str | None = None
    hq_accepted_by: str | None = None
    hq_destination_set_by: str | None = None
    proposed_by: str | None = None


class CaseRepository(Protocol):
    def get_parent_complaint(self, complaint_id: str) -> ParentComplaintRef | None:
        """Load parent Complaint by UUID or complaint number."""

    def count_cases(self, complaint_id: str) -> int:
        ...

    def next_case_number(self, owning_unit_id: str | None, *, at: datetime | None = None) -> str:
        """Allocate next ``UNIT-YYMM-NNNN`` (BQ-004)."""

    def save(self, case: CaseAggregate) -> CaseAggregate:
        ...

    def get(self, case_id: str, *, for_update: bool = False) -> CaseAggregate | None:
        """Load by UUID or Case Number.

        ``for_update`` locks the row (``SELECT ... FOR UPDATE``) so a
        concurrent claim/reassign cannot read the same pre-claim state
        (BR-005 E4 — double-claim race: only one claim wins).
        """

    def complaint_numbers_by_ids(self, complaint_ids: list[str]) -> dict[str, str]:
        """Map complaint UUID string → human complaint number."""
        ...

    def parent_handoffs_by_ids(
        self, complaint_ids: list[str]
    ) -> dict[str, ParentHandoff]:
        """Map complaint UUID string → handover actors on that Complaint."""
        ...

    def list_summaries(
        self,
        *,
        visibility: str,
        actor_id: str,
        org_unit_id: str | None,
        pusat_unit_codes: frozenset[str],
        complaint_id: str | None = None,
        status: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list, int]:
        """DEC-024 visibility-scoped Case rows (ORM or equivalent) + total."""

    def has_open_escalated_cases(self, complaint_id: str) -> bool:
        """True if any open Case under this parent is still ``escalatedToPusat``."""
        ...

    def mark_parent_returned_to_branch(self, complaint_id: str) -> None:
        """API-521 — set parent ``RETURNED_TO_BRANCH`` and clear HQ accept/slot."""
        ...

    def mark_parent_awaiting_hq_schedule(
        self,
        complaint_id: str,
        *,
        proposed_date: date | None = None,
        proposed_time: str | None = None,
        proposed_by: str | None = None,
    ) -> None:
        """Open the parent HQ schedule door (``ESCALATE_APPROVED``) for this Case."""
        ...

    def close_parent_hq_schedule_door_if_idle(self, complaint_id: str) -> None:
        """If no Case remains at Pusat, drop the unused ``ESCALATE_APPROVED`` door."""
        ...

    def latest_case_escalation_event(
        self, *, case_id: str, complaint_id: str
    ) -> str | None:
        """Latest CaseEscalatedToPusat / Returned / Cancelled event name, if any."""
        ...

    def mark_complaint_in_progress(self, complaint_id: str) -> None:
        """First Case effect: Complaint REGISTERED → IN_PROGRESS; case_created=True."""

    def sync_complaint_status_from_cases(self, complaint_id: str) -> str | None:
        """DEC-025 §3.4 — align Aggregate status to Case set.

        - Any working Case (not CLOSED/CANCELLED, including RESOLVED) → IN_PROGRESS
        - No working Case and at least one CLOSED → CLOSED (BR-009 auto-close)
        - Only CANCELLED remain → IN_PROGRESS (induk tetap buka)
        Returns the Aggregate status after sync, or None if parent missing.
        """

    def commit(self) -> None:
        ...
