"""Additional coverage for UserRepository (TASK-PLATFORM-CI-COV-001)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.modules.users.repository import UserRepository


def test_username_email_role_branch_exists_paths() -> None:
    session = MagicMock()
    repo = UserRepository(session)
    uid = uuid.uuid4()

    session.scalar.side_effect = [uid, None, uid, "AGENT", uid, None]
    assert repo.username_exists("a") is True
    assert repo.username_exists("b", exclude_user_id=uid) is False
    assert repo.email_exists("e@x") is True
    assert repo.get_role_code(uid) == "AGENT"
    assert repo.role_exists(uid) is True
    assert repo.branch_exists(uid) is False


def test_ensure_and_remove_user_role() -> None:
    session = MagicMock()
    repo = UserRepository(session)
    user_id = uuid.uuid4()
    role_id = uuid.uuid4()

    existing = MagicMock()
    session.scalar.return_value = existing
    assert repo.ensure_user_role(user_id, role_id) is False

    session.scalar.return_value = None
    assert repo.ensure_user_role(user_id, role_id) is True
    session.add.assert_called()
    session.flush.assert_called()

    link = MagicMock()
    session.scalar.return_value = link
    assert repo.remove_user_role(user_id, role_id) is True
    session.delete.assert_called_with(link)

    session.scalar.return_value = None
    assert repo.remove_user_role(user_id, role_id) is False


def test_sync_primary_user_role_removes_previous() -> None:
    session = MagicMock()
    repo = UserRepository(session)
    user_id = uuid.uuid4()
    prev = uuid.uuid4()
    new = uuid.uuid4()
    repo.ensure_user_role = MagicMock(return_value=True)  # type: ignore[method-assign]
    repo.remove_user_role = MagicMock(return_value=True)  # type: ignore[method-assign]
    repo.sync_primary_user_role(user_id, previous_role_id=prev, new_role_id=new)
    repo.ensure_user_role.assert_called_with(user_id, new)
    repo.remove_user_role.assert_called_with(user_id, prev)


def test_list_page_and_refresh_commit_rollback() -> None:
    session = MagicMock()
    repo = UserRepository(session)
    role_id = uuid.uuid4()
    user = SimpleNamespace(role_id=role_id, role=None)
    user.__dict__["role"] = None
    session.scalar.return_value = 1
    session.scalars.return_value.unique.return_value.all.return_value = [user]
    rows, total = repo.list_page(
        page=1, page_size=10, is_active=True, role_id=role_id, branch_id=uuid.uuid4()
    )
    assert total == 1
    assert rows == [user]

    role = MagicMock()
    session.get.return_value = role
    assert repo.refresh(user) is user
    assert user.role is role

    repo.commit()
    session.commit.assert_called()
    repo.rollback()
    session.rollback.assert_called()


def test_get_by_id_and_add() -> None:
    session = MagicMock()
    repo = UserRepository(session)
    user = MagicMock()
    session.scalar.return_value = user
    assert repo.get_by_id(uuid.uuid4()) is user
    assert repo.add(user) is user
    session.add.assert_called_with(user)
