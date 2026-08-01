"""Data Scope Foundation unit/service tests (TASK-037)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.iam.data_scope.models import ScopeType
from app.modules.iam.data_scope.schemas import (
    DataScopeCreateRequest,
    DataScopeItem,
    DataScopeReplaceRequest,
    DataScopeUpdateRequest,
)
from app.modules.iam.data_scope.service import DataScopeService


def _role(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "code": "AGENT",
        "name": "Agent",
        "description": None,
        "is_system": True,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "deleted_at": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _scope(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "role_id": uuid.uuid4(),
        "scope_type": ScopeType.BRANCH.value,
        "scope_value": "branch-001",
        "created_at": now,
        "updated_at": now,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_replace_role_scopes_full_set() -> None:
    role = _role()
    repo = MagicMock()
    repo.get_role.return_value = role
    repo.list_for_role.return_value = [
        _scope(role_id=role.id, scope_type="BRANCH", scope_value="branch-001"),
        _scope(role_id=role.id, scope_type="GLOBAL", scope_value=None),
    ]

    service = DataScopeService(repo)
    result = service.replace_role_scopes(
        role.id,
        DataScopeReplaceRequest(
            scopes=[
                DataScopeItem(scopeType="BRANCH", scopeValue="branch-001"),
                DataScopeItem(scopeType="GLOBAL"),
            ]
        ),
    )
    repo.delete_all_for_role.assert_called_once_with(role.id)
    assert repo.add.call_count == 2
    repo.commit.assert_called()
    assert len(result) == 2


def test_replace_empty_clears() -> None:
    role = _role()
    repo = MagicMock()
    repo.get_role.return_value = role
    repo.list_for_role.return_value = []

    service = DataScopeService(repo)
    result = service.replace_role_scopes(
        role.id, DataScopeReplaceRequest(scopes=[])
    )
    assert result == []
    repo.delete_all_for_role.assert_called_once_with(role.id)
    repo.add.assert_not_called()


def test_global_rejects_scope_value() -> None:
    with pytest.raises(ValidationError):
        DataScopeItem(scopeType="GLOBAL", scopeValue="x")


def test_self_rejects_scope_value() -> None:
    with pytest.raises(ValidationError):
        DataScopeItem(scopeType="SELF", scopeValue="me")


def test_branch_requires_scope_value() -> None:
    with pytest.raises(ValidationError):
        DataScopeItem(scopeType="BRANCH")


def test_schema_rejects_duplicates() -> None:
    with pytest.raises(ValidationError):
        DataScopeReplaceRequest(
            scopes=[
                DataScopeItem(scopeType="BRANCH", scopeValue="b1"),
                DataScopeItem(scopeType="BRANCH", scopeValue="b1"),
            ]
        )


def test_create_rejects_duplicate_key() -> None:
    role = _role()
    repo = MagicMock()
    repo.get_role.return_value = role
    repo.get_by_key.return_value = _scope(role_id=role.id)

    service = DataScopeService(repo)
    with pytest.raises(ConflictError):
        service.create(
            DataScopeCreateRequest(
                roleId=role.id,
                scopeType="BRANCH",
                scopeValue="branch-001",
            )
        )


def test_get_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    service = DataScopeService(repo)
    with pytest.raises(NotFoundError):
        service.get(uuid.uuid4())


def test_update_normalizes_global() -> None:
    row = _scope(scope_type="BRANCH", scope_value="b1")
    repo = MagicMock()
    repo.get_by_id.return_value = row
    repo.get_by_key.return_value = None

    service = DataScopeService(repo)
    with pytest.raises(ValidationAppError, match="must not have scopeValue"):
        service.update(
            row.id,
            DataScopeUpdateRequest(scopeType="GLOBAL", scopeValue="nope"),
        )


def test_replace_rejects_unknown_role() -> None:
    repo = MagicMock()
    repo.get_role.return_value = None
    service = DataScopeService(repo)
    with pytest.raises(NotFoundError, match="Peran tidak ditemukan"):
        service.replace_role_scopes(
            uuid.uuid4(), DataScopeReplaceRequest(scopes=[])
        )
