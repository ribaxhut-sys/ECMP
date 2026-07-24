"""Complaint Context Foundation unit tests (TASK-044)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.enums import (
    ComplaintReceiverType,
    ComplaintSourceType,
    ComplaintStatus,
    ComplaintTargetType,
)
from app.core.errors import NotFoundError
from app.modules.complaint_context import ComplaintContext, ComplaintContextService
from app.modules.complaints.service import ComplaintService
from app.modules.routing import ComplaintRoutingService


def _complaint(
    *,
    source_type: str = ComplaintSourceType.CUSTOMER.value,
    source_id: uuid.UUID | None = None,
    target_type: str = ComplaintTargetType.BRANCH.value,
    target_id: uuid.UUID | None = None,
    status: str = ComplaintStatus.NEW.value,
    priority: str = "HIGH",
) -> SimpleNamespace:
    now = datetime.now(UTC)
    sid = source_id or uuid.uuid4()
    tid = target_id if target_id is not None else uuid.uuid4()
    return SimpleNamespace(
        id=uuid.uuid4(),
        complaint_number="CMP-TEST0001",
        subject="Context test",
        description="Operational context assembly",
        channel="EMAIL",
        category="SERVICE",
        reported_at=now,
        customer_id=sid if source_type == ComplaintSourceType.CUSTOMER.value else None,
        branch_id=tid if target_type == ComplaintTargetType.BRANCH.value else None,
        source_type=source_type,
        source_id=sid,
        target_type=target_type,
        target_id=tid,
        status=status,
        priority=priority,
        created_at=now,
        updated_at=now,
    )


def _sla_row(complaint_id: uuid.UUID) -> SimpleNamespace:
    now = datetime.now(UTC)
    return SimpleNamespace(
        id=uuid.uuid4(),
        complaint_id=complaint_id,
        overall_status="PENDING",
        overall_due_at=now,
        assignment_status="PENDING",
        assignment_due_at=now,
        resolution_status="PENDING",
        resolution_due_at=now,
        appointment_status="PENDING",
        appointment_due_at=None,
        escalation_status="PENDING",
        escalation_due_at=None,
    )


def _assignment(complaint_id: uuid.UUID, assignee_id: uuid.UUID) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        complaint_id=complaint_id,
        assignee_id=assignee_id,
        assigned_by=uuid.uuid4(),
        assigned_at=datetime.now(UTC),
        is_current=True,
        notes=None,
        assignee=SimpleNamespace(full_name="Handler One"),
    )


def _service_with(
    complaint: SimpleNamespace,
    *,
    assignment: SimpleNamespace | None = None,
    sla: SimpleNamespace | None = None,
) -> ComplaintContextService:
    complaints = MagicMock()
    complaints.get_by_id.return_value = complaint
    assignments = MagicMock()
    assignments.get_current_assignment.return_value = assignment
    sla_repo = MagicMock()
    sla_repo.get_by_complaint_id.return_value = sla
    return ComplaintContextService(
        MagicMock(),
        routing_service=ComplaintRoutingService(),
        complaint_repository=complaints,
        assignment_repository=assignments,
        sla_repository=sla_repo,
    )


def test_build_context_pass() -> None:
    complaint = _complaint()
    svc = _service_with(complaint, sla=_sla_row(complaint.id))
    ctx = svc.build_context(complaint.id)

    assert isinstance(ctx, ComplaintContext)
    assert ctx.complaint.id == complaint.id
    assert ctx.current_status == ComplaintStatus.NEW.value
    assert ctx.priority == "HIGH"
    assert ctx.source.source_type == ComplaintSourceType.CUSTOMER.value
    assert ctx.target.target_type == ComplaintTargetType.BRANCH.value
    assert ctx.routing.receiver_type == ComplaintReceiverType.BRANCH
    assert ctx.current_assignment is None
    assert ctx.current_assignee is None
    assert ctx.current_sla is not None
    assert ctx.current_sla.overall_status == "PENDING"
    assert ctx.created_at == complaint.created_at
    assert ctx.updated_at == complaint.updated_at


def test_customer_complaint_context() -> None:
    branch_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    complaint = _complaint(
        source_type=ComplaintSourceType.CUSTOMER.value,
        source_id=customer_id,
        target_type=ComplaintTargetType.BRANCH.value,
        target_id=branch_id,
    )
    ctx = _service_with(complaint).build_context(complaint.id)

    assert ctx.source.source_id == customer_id
    assert ctx.target.target_id == branch_id
    assert ctx.routing.receiver_type == ComplaintReceiverType.BRANCH
    assert ctx.routing.receiver_id == branch_id
    assert ctx.routing.assignment_context["branchId"] == str(branch_id)


def test_branch_complaint_context() -> None:
    branch_id = uuid.uuid4()
    ho_id = uuid.uuid4()
    complaint = _complaint(
        source_type=ComplaintSourceType.BRANCH.value,
        source_id=branch_id,
        target_type=ComplaintTargetType.HEAD_OFFICE.value,
        target_id=ho_id,
    )
    ctx = _service_with(complaint).build_context(complaint.id)

    assert ctx.source.source_type == ComplaintSourceType.BRANCH.value
    assert ctx.target.target_type == ComplaintTargetType.HEAD_OFFICE.value
    assert ctx.routing.receiver_type == ComplaintReceiverType.HEAD_OFFICE
    assert ctx.routing.receiver_id == ho_id
    assert ctx.routing.assignment_context["branchId"] is None


def test_head_office_complaint_context() -> None:
    branch_id = uuid.uuid4()
    ho_id = uuid.uuid4()
    complaint = _complaint(
        source_type=ComplaintSourceType.HEAD_OFFICE.value,
        source_id=ho_id,
        target_type=ComplaintTargetType.BRANCH.value,
        target_id=branch_id,
    )
    ctx = _service_with(complaint).build_context(complaint.id)

    assert ctx.source.source_type == ComplaintSourceType.HEAD_OFFICE.value
    assert ctx.routing.receiver_type == ComplaintReceiverType.BRANCH
    assert ctx.routing.receiver_id == branch_id


def test_routing_included_in_context() -> None:
    complaint = _complaint()
    ctx = _service_with(complaint).build_context(complaint.id)
    assert ctx.routing.routing_reason
    assert "receiverType" in ctx.as_dict()["routing"]  # type: ignore[index]


def test_assignment_included_in_context() -> None:
    complaint = _complaint(status=ComplaintStatus.ASSIGNED.value)
    assignee_id = uuid.uuid4()
    assignment = _assignment(complaint.id, assignee_id)
    ctx = _service_with(complaint, assignment=assignment).build_context(complaint.id)

    assert ctx.current_assignment is not None
    assert ctx.current_assignment.assignee_id == assignee_id
    assert ctx.current_assignment.assignee_name == "Handler One"
    assert ctx.current_assignee is not None
    assert ctx.current_assignee.user_id == assignee_id
    assert ctx.current_assignee.full_name == "Handler One"


def test_refresh_context_reassembles() -> None:
    complaint = _complaint()
    svc = _service_with(complaint)
    first = svc.build_context(complaint.id)
    refreshed = svc.refresh_context(complaint.id)
    assert refreshed.complaint.id == first.complaint.id
    assert refreshed.current_status == first.current_status
    assert refreshed.routing.receiver_type == first.routing.receiver_type


def test_context_is_immutable() -> None:
    complaint = _complaint()
    ctx = _service_with(complaint).build_context(complaint.id)
    with pytest.raises(Exception):
        ctx.priority = "LOW"  # type: ignore[misc]


def test_build_context_not_found() -> None:
    complaints = MagicMock()
    complaints.get_by_id.return_value = None
    svc = ComplaintContextService(
        MagicMock(),
        complaint_repository=complaints,
        assignment_repository=MagicMock(),
        sla_repository=MagicMock(),
    )
    with pytest.raises(NotFoundError):
        svc.build_context(uuid.uuid4())


def test_complaint_service_may_build_context() -> None:
    """ComplaintService exposes get_context / refresh_context (no API change)."""
    complaint = _complaint()
    ctx_svc = _service_with(complaint, sla=_sla_row(complaint.id))
    repo = MagicMock()
    repo.session = MagicMock()
    service = ComplaintService(repository=repo, context_service=ctx_svc)

    ctx = service.get_context(complaint.id)
    assert ctx.complaint.id == complaint.id

    refreshed = service.refresh_context(complaint.id)
    assert refreshed.complaint.id == complaint.id


def test_system_complaint_routing_in_context() -> None:
    ho_id = uuid.uuid4()
    complaint = _complaint(
        source_type=ComplaintSourceType.SYSTEM.value,
        source_id=uuid.uuid4(),
        target_type=ComplaintTargetType.HEAD_OFFICE.value,
        target_id=ho_id,
    )
    ctx = _service_with(complaint).build_context(complaint.id)
    assert ctx.routing.receiver_type == ComplaintReceiverType.HEAD_OFFICE
    assert ctx.routing.receiver_id == ho_id
