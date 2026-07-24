"""SLA policy configuration unit/service tests (TASK-022 / API-315–317)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

from app.core.errors import NotFoundError
from app.modules.sla.schemas import SlaPolicyCreateRequest
from app.modules.sla.service import SlaService


def _policy_row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "name": "Standard SLA",
        "description": "Default targets",
        "assignment_target_minutes": 60,
        "appointment_target_minutes": 1440,
        "resolution_target_minutes": 2880,
        "escalation_target_minutes": 480,
        "overall_target_minutes": 4320,
        "is_active": False,
        "created_at": now,
        "updated_at": now,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _create_payload(**overrides: object) -> SlaPolicyCreateRequest:
    body = {
        "name": "Standard SLA",
        "description": "Default targets",
        "assignmentTargetMinutes": 60,
        "appointmentTargetMinutes": 1440,
        "resolutionTargetMinutes": 2880,
        "escalationTargetMinutes": 480,
        "overallTargetMinutes": 4320,
    }
    body.update(overrides)
    return SlaPolicyCreateRequest.model_validate(body)


def test_create_policy() -> None:
    created = _policy_row(is_active=False)
    repo = MagicMock()
    repo.create_policy.return_value = created

    result = SlaService(repo).create_policy(_create_payload())

    assert result.name == "Standard SLA"
    assert result.is_active is False
    assert result.assignment_target_minutes == 60
    assert result.overall_target_minutes == 4320
    repo.create_policy.assert_called_once()
    kwargs = repo.create_policy.call_args.kwargs
    assert kwargs["is_active"] is False
    assert kwargs["assignment_target_minutes"] == 60
    repo.commit.assert_called_once()


def test_only_one_active_policy() -> None:
    policy_a = _policy_row(name="A", is_active=True)
    policy_b = _policy_row(name="B", is_active=False)
    repo = MagicMock()
    repo.get_policy.return_value = policy_b

    def _activate(policy: SimpleNamespace, *, is_active: bool, now=None):
        _ = now
        policy.is_active = is_active
        return policy

    repo.set_policy_active.side_effect = _activate

    result = SlaService(repo).activate_policy(policy_b.id)

    assert result.is_active is True
    repo.deactivate_all_policies.assert_called_once()
    repo.set_policy_active.assert_called_once()
    assert repo.set_policy_active.call_args == call(
        policy_b, is_active=True
    )
    # Previously active A is not recalculated — only deactivate_all is used.
    assert policy_a.is_active is True  # mock A untouched; DB update via deactivate_all


def test_activate_policy() -> None:
    policy = _policy_row(is_active=False)
    repo = MagicMock()
    repo.get_policy.return_value = policy

    def _activate(row: SimpleNamespace, *, is_active: bool, now=None):
        _ = now
        row.is_active = is_active
        return row

    repo.set_policy_active.side_effect = _activate

    result = SlaService(repo).activate_policy(policy.id)

    assert result.is_active is True
    assert result.id == policy.id
    repo.deactivate_all_policies.assert_called_once()
    repo.commit.assert_called_once()


def test_activate_already_active_is_noop() -> None:
    policy = _policy_row(is_active=True)
    repo = MagicMock()
    repo.get_policy.return_value = policy

    result = SlaService(repo).activate_policy(policy.id)

    assert result.is_active is True
    repo.deactivate_all_policies.assert_not_called()
    repo.set_policy_active.assert_not_called()
    repo.commit.assert_not_called()


def test_activate_policy_not_found() -> None:
    repo = MagicMock()
    repo.get_policy.return_value = None

    with pytest.raises(NotFoundError):
        SlaService(repo).activate_policy(uuid.uuid4())


def test_retrieve_policy_list() -> None:
    active = _policy_row(name="Active", is_active=True)
    inactive = _policy_row(name="Draft", is_active=False)
    repo = MagicMock()
    repo.list_policies.return_value = [active, inactive]

    result = SlaService(repo).list_policies()

    assert len(result) == 2
    assert result[0].name == "Active"
    assert result[0].is_active is True
    assert result[1].name == "Draft"
    assert result[1].is_active is False
    repo.list_policies.assert_called_once()
