"""Permission Management unit/service tests (TASK-034)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.iam.permission.schemas import (
    PermissionCreateRequest,
    PermissionUpdateRequest,
)
from app.modules.iam.permission.service import PermissionService


def _permission(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "code": "custom:read",
        "name": "Custom Read",
        "module": "custom",
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
    service = PermissionService(repo)

    result = service.create(
        PermissionCreateRequest(
            code="Custom:Read",
            name="Custom Read",
            module="Custom",
            isActive=True,
        )
    )
    assert result.code == "custom:read"
    assert result.module == "custom"
    assert result.is_system is False
    repo.commit.assert_called()

    repo.get_by_code.return_value = _permission(code="custom:read")
    with pytest.raises(ConflictError):
        service.create(
            PermissionCreateRequest(
                code="custom:read",
                name="Dup",
                module="custom",
                isActive=True,
            )
        )


def test_create_rejects_invalid_code_format() -> None:
    service = PermissionService(MagicMock())
    with pytest.raises(ValidationAppError):
        service.create(
            PermissionCreateRequest(
                code="InvalidCode",
                name="Bad",
                module="invalid",
                isActive=True,
            )
        )


def test_create_rejects_module_mismatch() -> None:
    service = PermissionService(MagicMock())
    with pytest.raises(ValidationAppError, match="[Aa]walan modul|prefiks"):
        service.create(
            PermissionCreateRequest(
                code="complaint:read",
                name="Mismatch",
                module="settings",
                isActive=True,
            )
        )


def test_delete_rejects_system_permission() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = _permission(
        is_system=True, code="complaint:read", module="complaint"
    )
    service = PermissionService(repo)

    with pytest.raises(ConflictError, match="Izin sistem"):
        service.delete(uuid.uuid4())
    repo.soft_delete.assert_not_called()


def test_delete_soft_deletes_custom_permission() -> None:
    row = _permission(is_system=False)
    repo = MagicMock()
    repo.get_by_id.return_value = row
    service = PermissionService(repo)

    service.delete(row.id)
    repo.soft_delete.assert_called_once_with(row)
    repo.commit.assert_called()


def test_get_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    service = PermissionService(repo)
    with pytest.raises(NotFoundError):
        service.get(uuid.uuid4())


def test_update_name_and_description() -> None:
    row = _permission()
    repo = MagicMock()
    repo.get_by_id.return_value = row
    service = PermissionService(repo)

    result = service.update(
        row.id,
        PermissionUpdateRequest(name="Renamed", description="new desc"),
    )
    assert result.name == "Renamed"
    assert row.description == "new desc"
    repo.commit.assert_called()
