"""Complaint multi-source / multi-target unit tests (TASK-042 / DEC-018)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.core.enums import ComplaintSourceType, ComplaintTargetType
from app.core.errors import ValidationAppError
from app.modules.complaints.schemas import ComplaintCreateRequest
from app.modules.complaints.service import ComplaintService


def test_legacy_create_defaults_customer_to_branch() -> None:
    customer_id = uuid.uuid4()
    payload = ComplaintCreateRequest(
        customerId=customer_id,
        subject="Billing",
        description="Double charge",
        priority="HIGH",
    )
    assert payload.source_type == ComplaintSourceType.CUSTOMER
    assert payload.source_id == customer_id
    assert payload.target_type == ComplaintTargetType.BRANCH
    assert payload.target_id is None


def test_legacy_create_with_branch_sets_target_id() -> None:
    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    payload = ComplaintCreateRequest(
        customerId=customer_id,
        branchId=branch_id,
        subject="Billing",
        description="Double charge",
        priority="MEDIUM",
    )
    assert payload.target_id == branch_id
    assert payload.branch_id == branch_id


def test_generalized_requires_all_four_fields() -> None:
    with pytest.raises(ValidationError) as exc:
        ComplaintCreateRequest(
            sourceType="BRANCH",
            sourceId=uuid.uuid4(),
            subject="Ops issue",
            description="Branch raised",
            priority="LOW",
        )
    assert "targetType" in str(exc.value) or "targetId" in str(exc.value)


def test_generalized_customer_complaint() -> None:
    customer_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    payload = ComplaintCreateRequest(
        sourceType="CUSTOMER",
        sourceId=customer_id,
        targetType="BRANCH",
        targetId=branch_id,
        subject="Service",
        description="Slow response",
        priority="HIGH",
    )
    assert payload.customer_id == customer_id
    assert payload.branch_id == branch_id


def test_generalized_branch_and_head_office_source() -> None:
    branch_id = uuid.uuid4()
    ho_id = uuid.uuid4()
    branch_payload = ComplaintCreateRequest(
        sourceType="BRANCH",
        sourceId=branch_id,
        targetType="HEAD_OFFICE",
        targetId=ho_id,
        subject="Policy exception",
        description="Needs HO review",
        priority="CRITICAL",
    )
    assert branch_payload.customer_id is None
    assert branch_payload.branch_id is None
    assert branch_payload.source_type == ComplaintSourceType.BRANCH
    assert branch_payload.target_type == ComplaintTargetType.HEAD_OFFICE

    ho_payload = ComplaintCreateRequest(
        sourceType="HEAD_OFFICE",
        sourceId=ho_id,
        targetType="BRANCH",
        targetId=branch_id,
        subject="Audit finding",
        description="Branch non-compliance",
        priority="HIGH",
    )
    assert ho_payload.customer_id is None
    assert ho_payload.branch_id == branch_id


def test_service_create_branch_complaint_derives_no_customer() -> None:
    actor_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    ho_id = uuid.uuid4()
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

    sla = MagicMock()
    service = ComplaintService(repo, sla_service=sla)
    payload = ComplaintCreateRequest(
        sourceType="BRANCH",
        sourceId=branch_id,
        targetType="HEAD_OFFICE",
        targetId=ho_id,
        subject="Escalation seed",
        description="Branch to HO",
        priority="HIGH",
    )
    result = service.create(payload, actor_user_id=actor_id)

    row = created["row"]
    assert row.customer_id is None
    assert row.branch_id is None
    assert row.source_type == "BRANCH"
    assert row.target_type == "HEAD_OFFICE"
    assert result.source_type == ComplaintSourceType.BRANCH
    assert result.target_type == ComplaintTargetType.HEAD_OFFICE
    sla.create_for_complaint.assert_called_once()
    repo.add_timeline.assert_called_once()


def test_service_create_rejects_unknown_branch_source() -> None:
    repo = MagicMock()
    repo.branch_exists.return_value = False
    service = ComplaintService(repo, sla_service=MagicMock())

    with pytest.raises(ValidationAppError) as exc:
        service.create(
            ComplaintCreateRequest(
                sourceType="BRANCH",
                sourceId=uuid.uuid4(),
                targetType="HEAD_OFFICE",
                targetId=uuid.uuid4(),
                subject="x",
                description="y",
                priority="LOW",
            ),
            actor_user_id=uuid.uuid4(),
        )
    assert "Branch not found" in str(exc.value)


def test_service_create_customer_target_branch_sets_branch_id() -> None:
    """Initial assignment context derived from target_type=BRANCH."""
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
    assert row.customer_id == customer_id
    assert row.branch_id == branch_id
