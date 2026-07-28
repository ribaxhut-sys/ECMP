"""UAT-021 — primary role change must synchronize user_roles."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.security import hash_password
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserUpdateRequest
from app.modules.users.service import UserService


def _user_row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "username": "role_sync",
        "email": "role_sync@example.com",
        "full_name": "Role Sync",
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


@pytest.mark.parametrize(
    ("from_code", "to_code"),
    [
        ("SUPERVISOR", "AGENT"),  # Supervisor → Officer
        ("ADMIN", "SUPERVISOR"),  # Admin → Supervisor
    ],
)
def test_primary_role_change_removes_old_and_adds_new(
    from_code: str, to_code: str
) -> None:
    old_role = uuid.uuid4()
    new_role = uuid.uuid4()
    user = _user_row(role_id=old_role)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.role_exists.return_value = True
    repo.get_role_code.return_value = to_code
    repo.refresh.side_effect = lambda u: u

    with patch(
        "app.modules.users.service.invalidate_iam_user"
    ) as invalidate:
        UserService(repo).update(
            user.id,
            UserUpdateRequest(roleId=new_role),
            actor_user_id=uuid.uuid4(),
            actor_roles=("ADMIN",),
        )

    assert user.role_id == new_role
    repo.sync_primary_user_role.assert_called_once_with(
        user.id,
        previous_role_id=old_role,
        new_role_id=new_role,
    )
    repo.commit.assert_called_once()
    invalidate.assert_called_once_with(user.id)
    # Prove codes under test are the demotion/replacement cases from UAT-021.
    assert from_code != to_code


def test_sync_primary_user_role_algorithm() -> None:
    """Repository sync: ensure new, remove old; no duplicate insert."""
    user_id = uuid.uuid4()
    old_role = uuid.uuid4()
    new_role = uuid.uuid4()

    session = MagicMock()
    # First get_user_role_link (ensure new): missing → insert
    # Second get_user_role_link (remove old): present → delete
    existing_old = SimpleNamespace(
        id=uuid.uuid4(), user_id=user_id, role_id=old_role
    )
    session.scalar.side_effect = [None, existing_old]

    repo = UserRepository(session)
    repo.sync_primary_user_role(
        user_id, previous_role_id=old_role, new_role_id=new_role
    )

    assert session.add.call_count == 1
    added = session.add.call_args.args[0]
    assert added.user_id == user_id
    assert added.role_id == new_role
    session.delete.assert_called_once_with(existing_old)
    assert session.flush.call_count >= 2


def test_sync_primary_user_role_idempotent_when_new_already_present() -> None:
    user_id = uuid.uuid4()
    old_role = uuid.uuid4()
    new_role = uuid.uuid4()
    existing_new = SimpleNamespace(
        id=uuid.uuid4(), user_id=user_id, role_id=new_role
    )
    existing_old = SimpleNamespace(
        id=uuid.uuid4(), user_id=user_id, role_id=old_role
    )

    session = MagicMock()
    session.scalar.side_effect = [existing_new, existing_old]
    repo = UserRepository(session)

    repo.sync_primary_user_role(
        user_id, previous_role_id=old_role, new_role_id=new_role
    )

    session.add.assert_not_called()
    session.delete.assert_called_once_with(existing_old)


def test_sync_primary_no_op_when_same_role() -> None:
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()
    existing = SimpleNamespace(id=uuid.uuid4(), user_id=user_id, role_id=role_id)

    session = MagicMock()
    session.scalar.return_value = existing
    repo = UserRepository(session)

    repo.sync_primary_user_role(
        user_id, previous_role_id=role_id, new_role_id=role_id
    )

    session.add.assert_not_called()
    session.delete.assert_not_called()


def test_primary_role_change_rolls_back_on_sync_failure() -> None:
    old_role = uuid.uuid4()
    new_role = uuid.uuid4()
    user = _user_row(role_id=old_role)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.role_exists.return_value = True
    repo.get_role_code.return_value = "AGENT"
    repo.sync_primary_user_role.side_effect = RuntimeError("sync failed")

    with pytest.raises(RuntimeError, match="sync failed"):
        UserService(repo).update(
            user.id,
            UserUpdateRequest(roleId=new_role),
            actor_user_id=uuid.uuid4(),
            actor_roles=("ADMIN",),
        )

    repo.commit.assert_not_called()
    repo.rollback.assert_called_once()


def test_role_replacement_via_user_role_service_keeps_only_expected() -> None:
    """PUT /users/{id}/roles replace semantics remain exact (regression)."""
    from app.modules.iam.user_role.schemas import UserRolesReplaceRequest
    from app.modules.iam.user_role.service import UserRoleService

    user = SimpleNamespace(
        id=uuid.uuid4(),
        username="u",
        email="u@example.com",
        full_name="U",
        role_id=uuid.uuid4(),
        branch_id=None,
        is_active=True,
        last_login_at=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        role=None,
    )
    admin = SimpleNamespace(
        id=uuid.uuid4(),
        code="ADMIN",
        name="Admin",
        description=None,
        is_system=True,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        deleted_at=None,
    )
    officer = SimpleNamespace(
        id=uuid.uuid4(),
        code="AGENT",
        name="Officer",
        description=None,
        is_system=True,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        deleted_at=None,
    )

    repo = MagicMock()
    repo.get_user.return_value = user
    repo.list_links_for_user.return_value = [
        SimpleNamespace(user_id=user.id, role_id=admin.id),
        SimpleNamespace(user_id=user.id, role_id=officer.id),
    ]
    repo.get_roles_by_ids.return_value = [officer]
    repo.list_roles_for_user.return_value = [officer]

    UserRoleService(repo).replace_roles(
        user.id,
        UserRolesReplaceRequest(roleIds=[officer.id]),
        actor_roles=("ADMIN",),
    )

    removed = repo.delete_links_for_user.call_args.args[1]
    assert removed == {admin.id}
    assert repo.add_link.call_count == 0  # officer already present
