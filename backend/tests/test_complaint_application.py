"""Complaint application service tests (CAPABILITY-004)."""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

import pytest

from app.core.request_context import RequestContext
from app.modules.complaint.application.services import (
    ComplaintApplicationError,
    ComplaintCrudApplicationService,
    ComplaintDomainService,
    CreateComplaintInput,
    UpdateComplaintInput,
)
from app.modules.complaint.domain.models import (
    Complaint,
    ComplaintPriority,
    ComplaintStatus,
)
from app.modules.complaint.domain.repositories import ComplaintRepository


def _run(coro: Any) -> Any:
    return asyncio.run(coro)


def _ctx() -> RequestContext:
    return RequestContext(
        request_id="test-request-id",
        correlation_id="test-correlation-id",
    )


def _id() -> uuid.UUID:
    return uuid.uuid4()


class InMemoryComplaintRepository(ComplaintRepository):
    def __init__(self) -> None:
        self.rows: dict[uuid.UUID, Complaint] = {}

    async def add(self, complaint: Complaint) -> Complaint:
        self.rows[complaint.complaint_id] = complaint
        return complaint

    async def get_by_id(self, complaint_id: uuid.UUID) -> Complaint | None:
        return self.rows.get(complaint_id)

    async def update(self, complaint: Complaint) -> Complaint:
        if complaint.complaint_id not in self.rows:
            raise KeyError(complaint.complaint_id)
        self.rows[complaint.complaint_id] = complaint
        return complaint

    async def list_by_organization(
        self, organization_id: uuid.UUID
    ) -> tuple[Complaint, ...]:
        items = [
            c for c in self.rows.values() if c.organization_id == organization_id
        ]
        items.sort(key=lambda c: (c.created_at, str(c.complaint_id)))
        return tuple(items)

    async def list_by_queue_ticket(
        self, queue_ticket_id: uuid.UUID
    ) -> tuple[Complaint, ...]:
        items = [
            c for c in self.rows.values() if c.queue_ticket_id == queue_ticket_id
        ]
        items.sort(key=lambda c: (c.created_at, str(c.complaint_id)))
        return tuple(items)

    async def delete(self, complaint_id: uuid.UUID) -> bool:
        return self.rows.pop(complaint_id, None) is not None


def _service() -> ComplaintCrudApplicationService:
    return ComplaintCrudApplicationService(
        complaints=InMemoryComplaintRepository(),
        domain=ComplaintDomainService(),
    )


def test_create_complaint() -> None:
    svc = _service()
    org, branch, ticket = _id(), _id(), _id()

    async def scenario() -> None:
        dto = await svc.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=org,
                branch_id=branch,
                queue_ticket_id=ticket,
                category="Internet",
                title="Slow connection",
                description="Upload speed below SLA",
                priority=ComplaintPriority.HIGH,
            ),
        )
        assert dto.status is ComplaintStatus.OPEN
        assert dto.priority is ComplaintPriority.HIGH
        assert dto.queue_ticket_id == ticket
        assert dto.title == "Slow connection"

    _run(scenario())


def test_get_update_delete_complaint() -> None:
    svc = _service()

    async def scenario() -> None:
        created = await svc.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=_id(),
                category="Sales",
                title="Wrong plan",
                description="Plan upgrade not applied",
            ),
        )
        fetched = await svc.get_complaint(_ctx(), created.complaint_id)
        assert fetched.title == "Wrong plan"

        updated = await svc.update_complaint(
            _ctx(),
            created.complaint_id,
            UpdateComplaintInput(
                title="Plan mismatch", priority=ComplaintPriority.URGENT
            ),
        )
        assert updated.title == "Plan mismatch"
        assert updated.priority is ComplaintPriority.URGENT

        await svc.delete_complaint(_ctx(), created.complaint_id)
        with pytest.raises(ComplaintApplicationError) as exc:
            await svc.get_complaint(_ctx(), created.complaint_id)
        assert exc.value.code == "COMPLAINT_NOT_FOUND"

    _run(scenario())


def test_list_by_ticket() -> None:
    svc = _service()
    ticket = _id()
    other = _id()

    async def scenario() -> None:
        await svc.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=ticket,
                category="General",
                title="A",
                description="first",
            ),
        )
        await svc.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=ticket,
                category="Billing",
                title="B",
                description="second",
            ),
        )
        await svc.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=other,
                category="Sales",
                title="C",
                description="other ticket",
            ),
        )
        rows = await svc.list_by_queue_ticket(_ctx(), ticket)
        assert len(rows) == 2
        assert {r.title for r in rows} == {"A", "B"}

    _run(scenario())


def test_invalid_lifecycle_open_to_closed() -> None:
    svc = _service()

    async def scenario() -> None:
        created = await svc.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=_id(),
                category="Billing",
                title="X",
                description="Y",
            ),
        )
        with pytest.raises(ComplaintApplicationError) as exc:
            await svc.update_complaint(
                _ctx(),
                created.complaint_id,
                UpdateComplaintInput(status=ComplaintStatus.CLOSED),
            )
        assert exc.value.code == "INVALID_COMPLAINT_TRANSITION"

    _run(scenario())


def test_valid_lifecycle_full_path() -> None:
    svc = _service()

    async def scenario() -> None:
        created = await svc.create_complaint(
            _ctx(),
            CreateComplaintInput(
                organization_id=_id(),
                branch_id=_id(),
                queue_ticket_id=_id(),
                category="Activation",
                title="SIM issue",
                description="Cannot activate",
            ),
        )
        mid = await svc.update_complaint(
            _ctx(),
            created.complaint_id,
            UpdateComplaintInput(status=ComplaintStatus.IN_PROGRESS),
        )
        assert mid.status is ComplaintStatus.IN_PROGRESS
        resolved = await svc.update_complaint(
            _ctx(),
            created.complaint_id,
            UpdateComplaintInput(status=ComplaintStatus.RESOLVED),
        )
        assert resolved.status is ComplaintStatus.RESOLVED
        closed = await svc.update_complaint(
            _ctx(),
            created.complaint_id,
            UpdateComplaintInput(status=ComplaintStatus.CLOSED),
        )
        assert closed.status is ComplaintStatus.CLOSED

    _run(scenario())


def test_invalid_priority_on_create() -> None:
    svc = _service()

    async def scenario() -> None:
        with pytest.raises(ComplaintApplicationError) as exc:
            await svc.create_complaint(
                _ctx(),
                CreateComplaintInput(
                    organization_id=_id(),
                    branch_id=_id(),
                    queue_ticket_id=_id(),
                    category="Billing",
                    title="X",
                    description="Y",
                    priority="CRITICAL",  # type: ignore[arg-type]
                ),
            )
        assert exc.value.code == "INVALID_PRIORITY"

    _run(scenario())


def test_validation_blank_title() -> None:
    svc = _service()

    async def scenario() -> None:
        with pytest.raises(ComplaintApplicationError) as exc:
            await svc.create_complaint(
                _ctx(),
                CreateComplaintInput(
                    organization_id=_id(),
                    branch_id=_id(),
                    queue_ticket_id=_id(),
                    category="Billing",
                    title="  ",
                    description="ok",
                ),
            )
        assert exc.value.code == "VALIDATION_ERROR"

    _run(scenario())


def test_domain_service_transition() -> None:
    domain = ComplaintDomainService()
    now = datetime(2026, 7, 24, 11, 0, 0, tzinfo=timezone.utc)
    complaint = Complaint(
        complaint_id=_id(),
        organization_id=_id(),
        branch_id=_id(),
        queue_ticket_id=_id(),
        category="General",
        title="T",
        description="D",
        priority=ComplaintPriority.LOW,
        status=ComplaintStatus.OPEN,
        created_at=now,
        updated_at=now,
    )
    moved = domain.transition(complaint, ComplaintStatus.IN_PROGRESS, now=now)
    assert moved.status is ComplaintStatus.IN_PROGRESS
    with pytest.raises(ComplaintApplicationError) as exc:
        domain.transition(complaint, ComplaintStatus.CLOSED, now=now)
    assert exc.value.code == "INVALID_COMPLAINT_TRANSITION"
