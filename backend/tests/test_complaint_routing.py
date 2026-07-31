"""Complaint Routing Foundation unit tests (TASK-043)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.core.enums import (
    ComplaintReceiverType,
    ComplaintSourceType,
    ComplaintTargetType,
)
from app.core.errors import ValidationAppError
from app.modules.complaints.schemas import ComplaintCreateRequest
from app.modules.complaints.service import ComplaintService
from app.modules.routing import ComplaintRoutingService


@pytest.fixture()
def routing() -> ComplaintRoutingService:
    return ComplaintRoutingService()


def test_customer_to_branch(routing: ComplaintRoutingService) -> None:
    branch_id = uuid.uuid4()
    route = routing.resolve_route(
        source_type=ComplaintSourceType.CUSTOMER,
        source_id=uuid.uuid4(),
        target_type=ComplaintTargetType.BRANCH,
        target_id=branch_id,
    )
    assert route.receiver_type == ComplaintReceiverType.BRANCH
    assert route.receiver_id == branch_id
    assert route.assignment_context["branchId"] == str(branch_id)
    assert "Branch" in route.routing_reason


def test_branch_to_head_office(routing: ComplaintRoutingService) -> None:
    ho_id = uuid.uuid4()
    route = routing.resolve_route(
        source_type=ComplaintSourceType.BRANCH,
        source_id=uuid.uuid4(),
        target_type=ComplaintTargetType.HEAD_OFFICE,
        target_id=ho_id,
    )
    assert route.receiver_type == ComplaintReceiverType.HEAD_OFFICE
    assert route.receiver_id == ho_id
    assert route.assignment_context["branchId"] is None
    assert route.assignment_context["headOfficeId"] == str(ho_id)


def test_head_office_to_branch(routing: ComplaintRoutingService) -> None:
    branch_id = uuid.uuid4()
    route = routing.resolve_route(
        source_type=ComplaintSourceType.HEAD_OFFICE,
        source_id=uuid.uuid4(),
        target_type=ComplaintTargetType.BRANCH,
        target_id=branch_id,
    )
    assert route.receiver_type == ComplaintReceiverType.BRANCH
    assert route.receiver_id == branch_id


def test_system_to_head_office(routing: ComplaintRoutingService) -> None:
    ho_id = uuid.uuid4()
    route = routing.resolve_route(
        source_type=ComplaintSourceType.SYSTEM,
        source_id=uuid.uuid4(),
        target_type=ComplaintTargetType.HEAD_OFFICE,
        target_id=ho_id,
    )
    assert route.receiver_type == ComplaintReceiverType.HEAD_OFFICE
    assert route.receiver_id == ho_id


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (ComplaintSourceType.CUSTOMER, ComplaintTargetType.HEAD_OFFICE),
        (ComplaintSourceType.BRANCH, ComplaintTargetType.BRANCH),
        (ComplaintSourceType.HEAD_OFFICE, ComplaintTargetType.HEAD_OFFICE),
        (ComplaintSourceType.SYSTEM, ComplaintTargetType.BRANCH),
    ],
)
def test_invalid_routes_rejected(
    routing: ComplaintRoutingService,
    source: ComplaintSourceType,
    target: ComplaintTargetType,
) -> None:
    with pytest.raises(ValidationAppError) as exc:
        routing.validate_route(
            source_type=source,
            source_id=uuid.uuid4(),
            target_type=target,
            target_id=uuid.uuid4(),
        )
    assert "Invalid complaint route" in str(exc.value)


def test_legacy_customer_branch_null_target_allowed(
    routing: ComplaintRoutingService,
) -> None:
    """Backward compatible: CUSTOMER→BRANCH without branchId."""
    route = routing.resolve_route(
        source_type=ComplaintSourceType.CUSTOMER,
        source_id=uuid.uuid4(),
        target_type=ComplaintTargetType.BRANCH,
        target_id=None,
    )
    assert route.receiver_type == ComplaintReceiverType.BRANCH
    assert route.receiver_id is None
    assert route.assignment_context["branchId"] is None


def test_non_legacy_route_requires_target_id(
    routing: ComplaintRoutingService,
) -> None:
    with pytest.raises(ValidationAppError) as exc:
        routing.validate_route(
            source_type=ComplaintSourceType.BRANCH,
            source_id=uuid.uuid4(),
            target_type=ComplaintTargetType.HEAD_OFFICE,
            target_id=None,
        )
    assert "targetId is required" in str(exc.value)


def test_complaint_route_is_immutable(routing: ComplaintRoutingService) -> None:
    route = routing.resolve_route(
        source_type=ComplaintSourceType.CUSTOMER,
        source_id=uuid.uuid4(),
        target_type=ComplaintTargetType.BRANCH,
        target_id=uuid.uuid4(),
    )
    with pytest.raises(Exception):
        route.receiver_type = ComplaintReceiverType.HEAD_OFFICE  # type: ignore[misc]


def test_complaint_service_uses_routing_not_inline_rules() -> None:
    actor_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    now = datetime.now(UTC)
    created: dict[str, object] = {}

    def _add(complaint: object) -> None:
        complaint.id = uuid.uuid4()  # type: ignore[attr-defined]
        complaint.created_at = now  # type: ignore[attr-defined]
        complaint.updated_at = now  # type: ignore[attr-defined]
        created["row"] = complaint

    repo = MagicMock()
    repo.customer_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.add.side_effect = _add
    repo.refresh.side_effect = lambda c: None

    service = ComplaintService(repo, sla_service=MagicMock())
    service.create(
        ComplaintCreateRequest(
            sourceType="CUSTOMER",
            sourceId=customer_id,
            targetType="BRANCH",
            targetId=branch_id,
            subject="x",
            description="y",
            priority="MEDIUM",
        ),
        actor_user_id=actor_id,
    )
    row = created["row"]
    assert row.branch_id == branch_id
    assert row.customer_id == customer_id
    # Timeline metadata must include routing result (consumes route only).
    meta = repo.add_timeline.call_args.kwargs["metadata"]
    assert meta["receiverType"] == "BRANCH"
    assert meta["receiverId"] == str(branch_id)


def test_complaint_service_rejects_invalid_route() -> None:
    repo = MagicMock()
    repo.customer_exists.return_value = True
    service = ComplaintService(repo, sla_service=MagicMock())
    with pytest.raises(ValidationAppError) as exc:
        service.create(
            ComplaintCreateRequest(
                sourceType="CUSTOMER",
                sourceId=uuid.uuid4(),
                targetType="HEAD_OFFICE",
                targetId=uuid.uuid4(),
                subject="x",
                description="y",
                priority="LOW",
            ),
            actor_user_id=uuid.uuid4(),
        )
    assert "Invalid complaint route" in str(exc.value)
