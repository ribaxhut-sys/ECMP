"""UAT-022 — admin-assigned passwords require force_password_change."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.core.security import hash_password, verify_password
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
        "password_hash": hash_password("OldPass12!"),
        "role_id": uuid.uuid4(),
        "branch_id": None,
        "is_active": True,
        "force_password_change": False,
        "last_login_at": None,
        "created_at": now,
        "updated_at": now,
        "created_by": None,
        "updated_by": None,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_admin_create_user_sets_force_password_change() -> None:
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    branch_id = uuid.uuid4()
    repo = MagicMock()
    repo.username_exists.return_value = False
    repo.email_exists.return_value = False
    repo.list_taken_initials.return_value = set()
    repo.role_exists.return_value = True
    repo.branch_exists.return_value = True
    repo.get_role_code.return_value = "AGENT"
    repo.ensure_user_role.return_value = True
    repo.add.side_effect = lambda user: setattr(user, "id", user_id) or user
    repo.refresh.side_effect = lambda user: user

    result = UserService(repo).create(
        UserCreateRequest(
            username="newuser01",
            email="newuser01@example.com",
            fullName="New User",
            password="TempPass1!",
            roleId=role_id,
            branchId=branch_id,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=("ADMIN",),
    )

    added = repo.add.call_args.args[0]
    assert added.force_password_change is True
    assert result.force_password_change is True
    assert verify_password("TempPass1!", added.password_hash)


def test_admin_update_password_sets_force_password_change() -> None:
    user = _user_row(force_password_change=False)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.refresh.side_effect = lambda u: u
    repo.session = MagicMock()

    UserService(repo).update(
        user.id,
        UserUpdateRequest(password="AdminSet99!"),
        actor_user_id=uuid.uuid4(),
        actor_roles=("ADMIN",),
    )

    assert user.force_password_change is True
    assert verify_password("AdminSet99!", user.password_hash)
    repo.commit.assert_called_once()


def test_self_change_password_clears_force_flag() -> None:
    from unittest.mock import patch

    from app.modules.users.schemas import ChangePasswordRequest

    user = _user_row(
        password_hash=hash_password("TempPass1!"),
        force_password_change=True,
    )
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.session = MagicMock()

    with patch("app.modules.users.service.write_password_audit"):
        UserService(repo).change_password(
            user.id,
            ChangePasswordRequest(
                currentPassword="TempPass1!",
                newPassword="MyOwnPass2!",
                confirmPassword="MyOwnPass2!",
            ),
        )

    assert user.force_password_change is False
    assert verify_password("MyOwnPass2!", user.password_hash)
    repo.commit.assert_called_once()


def test_admin_reset_sets_force_password_change() -> None:
    from unittest.mock import patch

    user = _user_row(force_password_change=False)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.session = MagicMock()

    with patch("app.modules.users.service.write_password_audit"):
        result = UserService(repo).admin_reset_password(
            user.id, actor_user_id=uuid.uuid4()
        )

    assert user.force_password_change is True
    assert result.force_password_change is True
    assert verify_password(result.temporary_password, user.password_hash)


def test_forgot_password_reset_clears_force_flag() -> None:
    """User-chosen reset password must not require another change."""
    from app.modules.auth.password_helpers import set_user_password

    user = _user_row(force_password_change=True)
    set_user_password(
        user,  # type: ignore[arg-type]
        password_hash=hash_password("ChosenPass3!"),
        actor_user_id=user.id,
        force_password_change=False,
    )
    assert user.force_password_change is False
