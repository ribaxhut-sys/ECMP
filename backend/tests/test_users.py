"""User service unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.core.security import hash_password, verify_password
from app.modules.users.schemas import (
    UserCreateRequest,
    UserStatusUpdateRequest,
    UserUpdateRequest,
)
from app.modules.users.service import UserService


def _user_row(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "username": "jdoe",
        "email": "jdoe@example.com",
        "full_name": "Jane Doe",
        "password_hash": hash_password("Secret123"),
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


def test_hash_password_not_plaintext() -> None:
    hashed = hash_password("Secret123")
    assert hashed != "Secret123"
    assert verify_password("Secret123", hashed)


def test_create_user_hashes_password_and_hides_hash() -> None:
    role_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    created = _user_row(role_id=role_id)

    repo = MagicMock()
    repo.username_exists.return_value = False
    repo.email_exists.return_value = False
    repo.role_exists.return_value = True
    repo.add.side_effect = lambda user: setattr(user, "id", created.id) or user
    repo.refresh.side_effect = lambda user: user

    service = UserService(repo)
    result = service.create(
        UserCreateRequest(
            username="jdoe",
            email="jdoe@example.com",
            fullName="Jane Doe",
            password="Secret123",
            roleId=role_id,
        ),
        actor_user_id=actor_id,
    )

    assert result.username == "jdoe"
    assert not hasattr(result, "password_hash")
    assert "passwordHash" not in result.model_dump(by_alias=True)
    added = repo.add.call_args.args[0]
    assert added.password_hash != "Secret123"
    assert verify_password("Secret123", added.password_hash)
    assert added.is_active is True
    repo.sync_primary_user_role.assert_called_once_with(created.id, role_id)


def test_create_duplicate_username_conflict() -> None:
    repo = MagicMock()
    repo.username_exists.return_value = True
    service = UserService(repo)

    with pytest.raises(ConflictError):
        service.create(
            UserCreateRequest(
                username="jdoe",
                email="jdoe@example.com",
                fullName="Jane Doe",
                password="Secret123",
                roleId=uuid.uuid4(),
            ),
            actor_user_id=uuid.uuid4(),
        )


def test_create_missing_role_rejected() -> None:
    repo = MagicMock()
    repo.username_exists.return_value = False
    repo.email_exists.return_value = False
    repo.role_exists.return_value = False
    service = UserService(repo)

    with pytest.raises(ValidationAppError) as exc:
        service.create(
            UserCreateRequest(
                username="jdoe",
                email="jdoe@example.com",
                fullName="Jane Doe",
                password="Secret123",
                roleId=uuid.uuid4(),
            ),
            actor_user_id=uuid.uuid4(),
        )
    assert "Role" in exc.value.message


def test_get_user_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        UserService(repo).get(uuid.uuid4())


def test_soft_deactivate_sets_inactive() -> None:
    user = _user_row(is_active=True)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.refresh.side_effect = lambda u: u

    result = UserService(repo).update_status(
        user.id,
        UserStatusUpdateRequest(isActive=False),
        actor_user_id=uuid.uuid4(),
    )

    assert user.is_active is False
    assert result.is_active is False
    assert getattr(user, "deleted_at", None) is None
    repo.commit.assert_called_once()


def test_update_requires_unique_email() -> None:
    user = _user_row()
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.email_exists.return_value = True
    service = UserService(repo)

    with pytest.raises(ConflictError):
        service.update(
            user.id,
            UserUpdateRequest(email="taken@example.com"),
            actor_user_id=uuid.uuid4(),
        )
