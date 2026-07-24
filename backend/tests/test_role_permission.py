"""Role-Permission Matrix unit/service tests (TASK-035)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import ConflictError, NotFoundError
from app.modules.iam.role_permission.schemas import RolePermissionsReplaceRequest
from app.modules.iam.role_permission.service import RolePermissionService


def _role(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "code": "ADMIN",
        "name": "Admin",
        "description": None,
        "is_system": True,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "deleted_at": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _permission(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "code": "complaint:read",
        "name": "Complaint Read",
        "module": "complaint",
        "description": None,
        "is_system": True,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "deleted_at": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _link(role_id: uuid.UUID, permission_id: uuid.UUID) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        role_id=role_id,
        permission_id=permission_id,
        created_at=datetime.now(UTC),
    )


def test_replace_permissions_full_set() -> None:
    role = _role()
    p_a = _permission(code="a:read")
    p_b = _permission(code="b:read")
    p_c = _permission(code="c:read")
    p_d = _permission(code="d:read")

    repo = MagicMock()
    repo.get_role.return_value = role
    repo.list_links_for_role.return_value = [
        _link(role.id, p_a.id),
        _link(role.id, p_b.id),
        _link(role.id, p_c.id),
    ]
    repo.get_permissions_by_ids.return_value = [p_a, p_d]
    repo.list_permissions_for_role.return_value = [p_a, p_d]

    service = RolePermissionService(repo)
    result = service.replace_permissions(
        role.id,
        RolePermissionsReplaceRequest(permissionIds=[p_a.id, p_d.id]),
    )

    repo.delete_links_for_role.assert_called_once()
    removed = repo.delete_links_for_role.call_args.args[1]
    assert removed == {p_b.id, p_c.id}
    assert repo.add_link.call_count == 1
    added = repo.add_link.call_args.args[0]
    assert added.permission_id == p_d.id
    assert [item.id for item in result] == [p_a.id, p_d.id]
    repo.commit.assert_called()


def test_replace_permissions_empty_clears_all() -> None:
    role = _role()
    p_a = _permission()
    repo = MagicMock()
    repo.get_role.return_value = role
    repo.list_links_for_role.return_value = [_link(role.id, p_a.id)]
    repo.get_permissions_by_ids.return_value = []
    repo.list_permissions_for_role.return_value = []

    service = RolePermissionService(repo)
    result = service.replace_permissions(
        role.id, RolePermissionsReplaceRequest(permissionIds=[])
    )
    assert result == []
    repo.delete_links_for_role.assert_called_once_with(role.id, {p_a.id})
    repo.add_link.assert_not_called()


def test_replace_rejects_missing_permission() -> None:
    role = _role()
    missing_id = uuid.uuid4()
    repo = MagicMock()
    repo.get_role.return_value = role
    repo.get_permissions_by_ids.return_value = []

    service = RolePermissionService(repo)
    with pytest.raises(NotFoundError, match="permissions not found"):
        service.replace_permissions(
            role.id,
            RolePermissionsReplaceRequest(permissionIds=[missing_id]),
        )
    repo.commit.assert_not_called()


def test_replace_rejects_unknown_role() -> None:
    repo = MagicMock()
    repo.get_role.return_value = None
    service = RolePermissionService(repo)
    with pytest.raises(NotFoundError, match="Role not found"):
        service.replace_permissions(
            uuid.uuid4(),
            RolePermissionsReplaceRequest(permissionIds=[]),
        )


def test_assign_rejects_duplicate() -> None:
    role = _role()
    perm = _permission()
    repo = MagicMock()
    repo.get_role.return_value = role
    repo.get_permission.return_value = perm
    repo.get_link.return_value = _link(role.id, perm.id)

    service = RolePermissionService(repo)
    with pytest.raises(ConflictError, match="already assigned"):
        service.assign_permission(role.id, perm.id)


def test_remove_missing_link() -> None:
    role = _role()
    perm = _permission()
    repo = MagicMock()
    repo.get_role.return_value = role
    repo.get_permission.return_value = perm
    repo.get_link.return_value = None

    service = RolePermissionService(repo)
    with pytest.raises(NotFoundError, match="link not found"):
        service.remove_permission(role.id, perm.id)


def test_schema_rejects_duplicate_ids() -> None:
    from pydantic import ValidationError

    pid = uuid.uuid4()
    with pytest.raises(ValidationError):
        RolePermissionsReplaceRequest(permissionIds=[pid, pid])
