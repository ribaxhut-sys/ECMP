"""Repository port for Pengaduan Internal."""

from __future__ import annotations

from typing import Protocol

from app.modules.internal_complaint.domain.aggregate import InternalComplaintAggregate


class InternalComplaintRepository(Protocol):
    def next_number(self, *, owner_unit_id: str) -> str: ...

    def save(self, complaint: InternalComplaintAggregate) -> InternalComplaintAggregate: ...

    def get(self, complaint_id: str) -> InternalComplaintAggregate | None: ...

    def list_summaries(
        self,
        *,
        visibility: str,
        actor_id: str,
        org_unit_id: str | None,
        pusat_unit_codes: frozenset[str],
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
        pending_transfer_request: bool | None = None,
        pending_withdraw_request: bool | None = None,
        needs_receive: bool | None = None,
        needs_action: bool | None = None,
    ) -> tuple[list, int]: ...

    def commit(self) -> None: ...
