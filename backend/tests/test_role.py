"""Role Management unit/service tests (TASK-033)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.iam.role.schemas import RoleCreateRequest, RoleUpdateRequest
from app.modules.iam.role.service import RoleService


def _role(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "code": "CUSTOM_ROLE",
        "name": "Custom Role",
        "description": "desc",
        "is_system": False,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "deleted_at": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_create_normalizes_code_and_rejects_duplicate() -> None:
    repo = MagicMock()
    repo.get_by_code.return_value = None

    def add(row: object) -> object:
        return row

    repo.add.side_effect = add
    service = RoleService(repo)

    result = service.create(
        RoleCreateRequest(code="custom_role", name="Custom", isActive=True)
    )
    assert result.code == "CUSTOM_ROLE"
    assert result.is_system is False
    repo.commit.assert_called()

    repo.get_by_code.return_value = _role(code="CUSTOM_ROLE")
    with pytest.raises(ConflictError):
        service.create(
            RoleCreateRequest(code="CUSTOM_ROLE", name="Dup", isActive=True)
        )


def test_create_rejects_invalid_code() -> None:
    service = RoleService(MagicMock())
    with pytest.raises(ValidationAppError):
        service.create(
            RoleCreateRequest(code="1bad", name="Bad", isActive=True)
        )


def test_delete_rejects_system_role() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = _role(is_system=True, code="ADMIN")
    service = RoleService(repo)

    with pytest.raises(ConflictError, match="Peran sistem"):
        service.delete(uuid.uuid4())
    repo.soft_delete.assert_not_called()


def test_delete_soft_deletes_custom_role() -> None:
    row = _role(is_system=False)
    repo = MagicMock()
    repo.get_by_id.return_value = row
    service = RoleService(repo)

    service.delete(row.id)
    repo.soft_delete.assert_called_once_with(row)
    repo.commit.assert_called()


def test_get_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    service = RoleService(repo)
    with pytest.raises(NotFoundError):
        service.get(uuid.uuid4())


def test_update_name_and_description() -> None:
    row = _role()
    repo = MagicMock()
    repo.get_by_id.return_value = row
    service = RoleService(repo)

    result = service.update(
        row.id,
        RoleUpdateRequest(name="Renamed", description="new desc"),
    )
    assert result.name == "Renamed"
    assert row.description == "new desc"
    repo.commit.assert_called()
