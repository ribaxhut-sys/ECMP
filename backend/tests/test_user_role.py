"""User-Role Assignment unit/service tests (TASK-036)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.core.errors import ConflictError, NotFoundError
from app.modules.iam.user_role.schemas import UserRolesReplaceRequest
from app.modules.iam.user_role.service import UserRoleService


def _user(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "username": "tester",
        "email": "tester@example.com",
        "full_name": "Tester",
        "role_id": uuid.uuid4(),
        "branch_id": None,
        "is_active": True,
        "last_login_at": None,
        "created_at": now,
        "updated_at": now,
        "deleted_at": None,
        "role": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


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


def _link(user_id: uuid.UUID, role_id: uuid.UUID) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid.uuid4(),
        user_id=user_id,
        role_id=role_id,
        created_at=datetime.now(UTC),
    )


def test_replace_roles_full_set() -> None:
    user = _user()
    admin = _role(code="ADMIN")
    supervisor = _role(code="SUPERVISOR")
    agent = _role(code="AGENT")

    repo = MagicMock()
    repo.get_user.return_value = user
    repo.list_links_for_user.return_value = [
        _link(user.id, admin.id),
        _link(user.id, supervisor.id),
    ]
    repo.get_roles_by_ids.return_value = [agent]
    repo.list_roles_for_user.return_value = [agent]

    service = UserRoleService(repo)
    result = service.replace_roles(
        user.id, UserRolesReplaceRequest(roleIds=[agent.id])
    )

    removed = repo.delete_links_for_user.call_args.args[1]
    assert removed == {admin.id, supervisor.id}
    assert repo.add_link.call_count == 1
    assert repo.add_link.call_args.args[0].role_id == agent.id
    assert [item.code for item in result] == ["AGENT"]
    repo.commit.assert_called()


def test_replace_roles_empty_clears_all() -> None:
    user = _user()
    admin = _role()
    repo = MagicMock()
    repo.get_user.return_value = user
    repo.list_links_for_user.return_value = [_link(user.id, admin.id)]
    repo.get_roles_by_ids.return_value = []
    repo.list_roles_for_user.return_value = []

    service = UserRoleService(repo)
    result = service.replace_roles(
        user.id, UserRolesReplaceRequest(roleIds=[])
    )
    assert result == []
    repo.delete_links_for_user.assert_called_once_with(user.id, {admin.id})
    repo.add_link.assert_not_called()


def test_replace_rejects_missing_role() -> None:
    user = _user()
    repo = MagicMock()
    repo.get_user.return_value = user
    repo.get_roles_by_ids.return_value = []

    service = UserRoleService(repo)
    with pytest.raises(NotFoundError, match="roles not found"):
        service.replace_roles(
            user.id, UserRolesReplaceRequest(roleIds=[uuid.uuid4()])
        )
    repo.commit.assert_not_called()


def test_replace_rejects_unknown_user() -> None:
    repo = MagicMock()
    repo.get_user.return_value = None
    service = UserRoleService(repo)
    with pytest.raises(NotFoundError, match="User not found"):
        service.replace_roles(
            uuid.uuid4(), UserRolesReplaceRequest(roleIds=[])
        )


def test_assign_rejects_duplicate() -> None:
    user = _user()
    role = _role()
    repo = MagicMock()
    repo.get_user.return_value = user
    repo.get_role.return_value = role
    repo.get_link.return_value = _link(user.id, role.id)

    service = UserRoleService(repo)
    with pytest.raises(ConflictError, match="already assigned"):
        service.assign_role(user.id, role.id)


def test_remove_missing_link() -> None:
    user = _user()
    role = _role()
    repo = MagicMock()
    repo.get_user.return_value = user
    repo.get_role.return_value = role
    repo.get_link.return_value = None

    service = UserRoleService(repo)
    with pytest.raises(NotFoundError, match="link not found"):
        service.remove_role(user.id, role.id)


def test_schema_rejects_duplicate_ids() -> None:
    rid = uuid.uuid4()
    with pytest.raises(ValidationError):
        UserRolesReplaceRequest(roleIds=[rid, rid])
