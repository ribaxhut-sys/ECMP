"""UAT-020 — role assignment privilege escalation guard."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.authorization.role_assignment_policy import (
    assert_can_assign_role,
    can_assign_role,
)
from app.core.errors import ForbiddenError
from app.core.security import hash_password
from app.modules.users.schemas import UserCreateRequest, UserUpdateRequest
from app.modules.users.service import UserService


def _user_row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "username": "jdoe",
        "email": "jdoe@example.com",
        "full_name": "Jane Doe",
        "initials": "JDO",
        "password_hash": hash_password("Secret123!"),
        "role_id": uuid.uuid4(),
        "branch_id": None,
        "is_active": True,
        "last_login_at": None,
        "created_at": now,
        "updated_at": now,
        "created_by": None,
        "updated_by": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


_BRANCH_SCOPED_ROLE_CODES = frozenset(
    {
        "AGENT",
        "CS_AGENT",
        "BRANCH_OFFICER",
        "SUPERVISOR",
        "BRANCH_SUPERVISOR",
    }
)


def _repo_for_create(*, role_code: str) -> tuple[MagicMock, uuid.UUID]:
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = MagicMock()
    repo.username_exists.return_value = False
    repo.email_exists.return_value = False
    repo.list_taken_initials.return_value = set()
    repo.role_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.get_role_code.return_value = role_code
    repo.ensure_user_role.return_value = True
    repo.add.side_effect = lambda user: setattr(user, "id", user_id) or user
    repo.refresh.side_effect = lambda user: user
    return repo, role_id


def _create(
    *,
    actor_roles: tuple[str, ...],
    target_role_code: str,
) -> None:
    repo, role_id = _repo_for_create(role_code=target_role_code)
    branch_id = (
        uuid.uuid4() if target_role_code in _BRANCH_SCOPED_ROLE_CODES else None
    )
    UserService(repo).create(
        UserCreateRequest(
            username=f"u_{uuid.uuid4().hex[:8]}",
            email=f"{uuid.uuid4().hex[:8]}@example.com",
            fullName="Policy User",
            password="Secret123!",
            roleId=role_id,
            branchId=branch_id,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=actor_roles,
    )


@pytest.mark.parametrize(
    ("actor", "target"),
    [
        (("ADMIN",), "ADMIN"),
        (("ADMIN",), "SUPERVISOR"),
        (("ADMIN",), "AGENT"),
        (("SUPERVISOR",), "AGENT"),
        (("SUPERVISOR",), "BRANCH_OFFICER"),
    ],
)
def test_create_allowed_by_policy(actor: tuple[str, ...], target: str) -> None:
    _create(actor_roles=actor, target_role_code=target)


@pytest.mark.parametrize(
    ("actor", "target"),
    [
        (("SUPERVISOR",), "ADMIN"),
        (("SUPERVISOR",), "SUPERVISOR"),
        (("AGENT",), "ADMIN"),
        (("AGENT",), "SUPERVISOR"),
        (("AGENT",), "AGENT"),
        (("BRANCH_OFFICER",), "AGENT"),
        (("VIEWER",), "AGENT"),
    ],
)
def test_create_forbidden_by_policy(actor: tuple[str, ...], target: str) -> None:
    with pytest.raises(ForbiddenError) as exc:
        _create(actor_roles=actor, target_role_code=target)
    assert exc.value.status_code == 403
    assert exc.value.code == "FORBIDDEN"


def test_update_role_escalation_forbidden() -> None:
    old_role = uuid.uuid4()
    new_role = uuid.uuid4()
    user = _user_row(role_id=old_role)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.role_exists.return_value = True
    repo.get_role_code.return_value = "ADMIN"

    with pytest.raises(ForbiddenError) as exc:
        UserService(repo).update(
            user.id,
            UserUpdateRequest(roleId=new_role),
            actor_user_id=uuid.uuid4(),
            actor_roles=("SUPERVISOR",),
        )
    assert exc.value.status_code == 403
    repo.commit.assert_not_called()


def test_update_role_officer_allowed_for_supervisor() -> None:
    old_role = uuid.uuid4()
    new_role = uuid.uuid4()
    branch_id = uuid.uuid4()
    user = _user_row(role_id=old_role, branch_id=branch_id)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.role_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.get_role_code.return_value = "AGENT"
    repo.refresh.side_effect = lambda u: u

    UserService(repo).update(
        user.id,
        UserUpdateRequest(roleId=new_role),
        actor_user_id=uuid.uuid4(),
        actor_roles=("SUPERVISOR",),
    )
    assert user.role_id == new_role
    repo.sync_primary_user_role.assert_called_once_with(
        user.id,
        previous_role_id=old_role,
        new_role_id=new_role,
    )
    repo.commit.assert_called_once()


def test_policy_matrix_helpers() -> None:
    assert can_assign_role(["ADMIN"], "SUPERVISOR")
    assert can_assign_role(["SUPERVISOR"], "AGENT")
    assert not can_assign_role(["SUPERVISOR"], "ADMIN")
    assert not can_assign_role(["SUPERVISOR"], "SUPERVISOR")
    assert not can_assign_role(["AGENT"], "AGENT")

    with pytest.raises(ForbiddenError):
        assert_can_assign_role(["SUPERVISOR"], "ADMIN")
