"""User service unit tests."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import (
    ConflictError,
    NotFoundError,
    ValidationAppError,
)
from app.core.security import hash_password, verify_password
from app.modules.users.schemas import (
    UserCreateRequest,
    UserStatusUpdateRequest,
    UserUpdateRequest,
)
from app.modules.users.service import UserService

_ADMIN_ACTOR = ("ADMIN",)


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


def _create_repo(
    *,
    role_id: uuid.UUID,
    role_code: str = "AGENT",
    created_id: uuid.UUID | None = None,
) -> MagicMock:
    user_id = created_id or uuid.uuid4()
    repo = MagicMock()
    repo.username_exists.return_value = False
    repo.email_exists.return_value = False
    repo.role_exists.return_value = True
    repo.get_role_code.return_value = role_code
    repo.branch_exists.return_value = True
    repo.ensure_user_role.return_value = True
    repo.add.side_effect = lambda user: setattr(user, "id", user_id) or user
    repo.refresh.side_effect = lambda user: user
    return repo


_BRANCH_ID = uuid.UUID("26d8f2bf-7d4c-4e42-b747-d2fa5b18e327")


def test_hash_password_not_plaintext() -> None:
    hashed = hash_password("Secret123")
    assert hashed != "Secret123"
    assert verify_password("Secret123", hashed)


def test_create_user_hashes_password_and_hides_hash() -> None:
    role_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    created = _user_row(role_id=role_id)
    repo = _create_repo(role_id=role_id, created_id=created.id)

    service = UserService(repo)
    result = service.create(
        UserCreateRequest(
            username="jdoe",
            email="jdoe@example.com",
            fullName="Jane Doe",
            password="Secret123",
            roleId=role_id,
            branchId=_BRANCH_ID,
        ),
        actor_user_id=actor_id,
        actor_roles=_ADMIN_ACTOR,
    )

    assert result.username == "jdoe"
    assert not hasattr(result, "password_hash")
    assert "passwordHash" not in result.model_dump(by_alias=True)
    added = repo.add.call_args.args[0]
    assert added.password_hash != "Secret123"
    assert verify_password("Secret123", added.password_hash)
    assert added.is_active is True
    assert added.force_password_change is True
    assert added.branch_id == _BRANCH_ID
    repo.ensure_user_role.assert_called_once_with(created.id, role_id)
    repo.commit.assert_called_once()
    repo.rollback.assert_not_called()


def test_create_branch_scoped_role_without_branch_rejected() -> None:
    role_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code="AGENT")
    service = UserService(repo)

    with pytest.raises(ValidationAppError) as exc:
        service.create(
            UserCreateRequest(
                username="no_branch_agent",
                email="nobranch@example.com",
                fullName="No Branch",
                password="Secret123!",
                roleId=role_id,
            ),
            actor_user_id=uuid.uuid4(),
            actor_roles=_ADMIN_ACTOR,
        )
    assert "Cabang wajib" in exc.value.message
    repo.add.assert_not_called()


def test_create_supervisor_without_branch_rejected() -> None:
    role_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code="SUPERVISOR")
    service = UserService(repo)

    with pytest.raises(ValidationAppError) as exc:
        service.create(
            UserCreateRequest(
                username="no_branch_sup",
                email="nobranchsup@example.com",
                fullName="No Branch Sup",
                password="Secret123!",
                roleId=role_id,
            ),
            actor_user_id=uuid.uuid4(),
            actor_roles=_ADMIN_ACTOR,
        )
    assert "Cabang wajib" in exc.value.message


def test_create_admin_without_branch_allowed() -> None:
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code="ADMIN", created_id=user_id)

    UserService(repo).create(
        UserCreateRequest(
            username="admin_nobranch",
            email="admin_nobranch@example.com",
            fullName="Admin No Branch",
            password="Secret123!",
            roleId=role_id,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    assert repo.add.call_args.args[0].branch_id is None
    repo.commit.assert_called_once()


@pytest.mark.parametrize("role_code", ["AGENT", "SUPERVISOR"])
def test_create_branch_scoped_role_with_branch_accepted(role_code: str) -> None:
    """Commit 2 regression lock: branch-scoped create with a valid branchId
    is unchanged (EBS-001 §2.1 step 3, preserved verbatim)."""
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code=role_code, created_id=user_id)

    UserService(repo).create(
        UserCreateRequest(
            username=f"{role_code.lower()}_with_branch",
            email=f"{role_code.lower()}_branch@example.com",
            fullName=f"{role_code} With Branch",
            password="Secret123!",
            roleId=role_id,
            branchId=_BRANCH_ID,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    assert repo.add.call_args.args[0].branch_id == _BRANCH_ID
    repo.commit.assert_called_once()


_HEAD_OFFICE_SCOPED_ROLE_CODES = [
    "ADMIN",
    "ADMINISTRATOR",
    "HO_SCHEDULER",
    "HEAD_OFFICE_SCHEDULER",
    "SCHEDULER",
    "HO_ENGINEER",
    "HEAD_OFFICE_ENGINEER",
]


@pytest.mark.parametrize("role_code", _HEAD_OFFICE_SCOPED_ROLE_CODES)
def test_create_head_office_scoped_role_with_branch_rejected(role_code: str) -> None:
    """Commit 2: head-office scoped roles must not carry a branchId (EBS-001 §2.1 step 4)."""
    role_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code=role_code)

    with pytest.raises(ValidationAppError) as exc:
        UserService(repo).create(
            UserCreateRequest(
                username=f"{role_code.lower()}_with_branch",
                email=f"{role_code.lower()}_branch@example.com",
                fullName=f"{role_code} With Branch",
                password="Secret123!",
                roleId=role_id,
                branchId=_BRANCH_ID,
            ),
            actor_user_id=uuid.uuid4(),
            actor_roles=_ADMIN_ACTOR,
        )
    assert "Cabang tidak boleh" in exc.value.message
    repo.add.assert_not_called()


@pytest.mark.parametrize("role_code", _HEAD_OFFICE_SCOPED_ROLE_CODES)
def test_create_head_office_scoped_role_without_branch_accepted(role_code: str) -> None:
    """Commit 2: head-office scoped roles remain creatable with branchId omitted."""
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code=role_code, created_id=user_id)

    UserService(repo).create(
        UserCreateRequest(
            username=f"{role_code.lower()}_nobranch",
            email=f"{role_code.lower()}_nobranch@example.com",
            fullName=f"{role_code} No Branch",
            password="Secret123!",
            roleId=role_id,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    assert repo.add.call_args.args[0].branch_id is None
    repo.commit.assert_called_once()


def test_create_super_admin_with_branch_accepted() -> None:
    """Commit 2: SUPER_ADMIN exception is evaluated before both scoped sets —
    branchId remains optional in both directions (EBS-001 §2.1 step 2)."""
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code="SUPER_ADMIN", created_id=user_id)

    UserService(repo).create(
        UserCreateRequest(
            username="super_admin_branch",
            email="super_admin_branch@example.com",
            fullName="Super Admin Branch",
            password="Secret123!",
            roleId=role_id,
            branchId=_BRANCH_ID,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    assert repo.add.call_args.args[0].branch_id == _BRANCH_ID
    repo.commit.assert_called_once()


def test_create_super_admin_without_branch_accepted() -> None:
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code="SUPER_ADMIN", created_id=user_id)

    UserService(repo).create(
        UserCreateRequest(
            username="super_admin_nobranch",
            email="super_admin_nobranch@example.com",
            fullName="Super Admin No Branch",
            password="Secret123!",
            roleId=role_id,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    assert repo.add.call_args.args[0].branch_id is None
    repo.commit.assert_called_once()


def test_create_super_admin_with_inactive_branch_rejected() -> None:
    """SUPER_ADMIN skips the required/forbidden rule only — branch validity
    itself (_ensure_branch) still applies when a branchId is supplied."""
    role_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code="SUPER_ADMIN")
    repo.branch_exists.return_value = False

    with pytest.raises(ValidationAppError) as exc:
        UserService(repo).create(
            UserCreateRequest(
                username="super_admin_bad_branch",
                email="super_admin_bad_branch@example.com",
                fullName="Super Admin Bad Branch",
                password="Secret123!",
                roleId=role_id,
                branchId=_BRANCH_ID,
            ),
            actor_user_id=uuid.uuid4(),
            actor_roles=_ADMIN_ACTOR,
        )
    assert "Cabang tidak ditemukan" in exc.value.message
    repo.add.assert_not_called()


@pytest.mark.parametrize("branch_id", [None, _BRANCH_ID])
def test_create_unclassified_role_branch_optional(
    branch_id: uuid.UUID | None,
) -> None:
    """Unclassified roles (e.g. VIEWER) keep branchId fully optional — Commit 2
    only adds behavior for BRANCH_SCOPED_ROLE_CODES / HEAD_OFFICE_SCOPED_ROLE_CODES,
    the fallback path is untouched."""
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code="VIEWER", created_id=user_id)

    UserService(repo).create(
        UserCreateRequest(
            username="viewer_user",
            email="viewer_user@example.com",
            fullName="Viewer User",
            password="Secret123!",
            roleId=role_id,
            branchId=branch_id,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    assert repo.add.call_args.args[0].branch_id == branch_id
    repo.commit.assert_called_once()


@pytest.mark.parametrize(
    ("persona", "role_code"),
    [
        ("ADMIN", "ADMIN"),
        ("SUPERVISOR", "SUPERVISOR"),
        ("OFFICER", "AGENT"),
    ],
)
def test_create_user_syncs_user_roles_for_persona(
    persona: str, role_code: str
) -> None:
    """UAT-018: Admin / Supervisor / Officer create must insert user_roles."""
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, role_code=role_code, created_id=user_id)
    branch_id = None if role_code == "ADMIN" else _BRANCH_ID

    UserService(repo).create(
        UserCreateRequest(
            username=f"{persona.lower()}_user",
            email=f"{persona.lower()}@example.com",
            fullName=f"{persona} User",
            password="Secret123!",
            roleId=role_id,
            branchId=branch_id,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    repo.add.assert_called_once()
    repo.ensure_user_role.assert_called_once_with(user_id, role_id)
    assert repo.add.call_args.args[0].role_id == role_id
    repo.commit.assert_called_once()


def test_create_user_roles_idempotent_no_duplicate() -> None:
    """If user_roles already exists, ensure_user_role must not insert again."""
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, created_id=user_id)
    repo.ensure_user_role.return_value = False  # already present

    UserService(repo).create(
        UserCreateRequest(
            username="dup_role_user",
            email="dup_role@example.com",
            fullName="Dup Role",
            password="Secret123!",
            roleId=role_id,
            branchId=_BRANCH_ID,
        ),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    repo.ensure_user_role.assert_called_once_with(user_id, role_id)
    assert repo.ensure_user_role.return_value is False
    repo.commit.assert_called_once()


def test_create_user_rolls_back_when_user_roles_fails() -> None:
    """Transaction failure on user_roles must roll back the whole create."""
    role_id = uuid.uuid4()
    user_id = uuid.uuid4()
    repo = _create_repo(role_id=role_id, created_id=user_id)
    repo.ensure_user_role.side_effect = RuntimeError("user_roles insert failed")

    with pytest.raises(RuntimeError, match="user_roles insert failed"):
        UserService(repo).create(
            UserCreateRequest(
                username="rollback_user",
                email="rollback@example.com",
                fullName="Rollback User",
                password="Secret123!",
                roleId=role_id,
                branchId=_BRANCH_ID,
            ),
            actor_user_id=uuid.uuid4(),
            actor_roles=_ADMIN_ACTOR,
        )

    repo.add.assert_called_once()
    repo.ensure_user_role.assert_called_once_with(user_id, role_id)
    repo.commit.assert_not_called()
    repo.rollback.assert_called_once()


def test_ensure_user_role_skips_duplicate_mapping() -> None:
    """Repository helper must not insert a second (user_id, role_id) row."""
    from app.modules.users.repository import UserRepository

    user_id = uuid.uuid4()
    role_id = uuid.uuid4()
    existing = SimpleNamespace(id=uuid.uuid4(), user_id=user_id, role_id=role_id)

    session = MagicMock()
    session.scalar.return_value = existing
    repo = UserRepository(session)

    inserted = repo.ensure_user_role(user_id, role_id)

    assert inserted is False
    session.add.assert_not_called()


def test_ensure_user_role_inserts_when_missing() -> None:
    from app.modules.users.repository import UserRepository

    user_id = uuid.uuid4()
    role_id = uuid.uuid4()

    session = MagicMock()
    session.scalar.return_value = None
    repo = UserRepository(session)

    inserted = repo.ensure_user_role(user_id, role_id)

    assert inserted is True
    session.add.assert_called_once()
    added = session.add.call_args.args[0]
    assert added.user_id == user_id
    assert added.role_id == role_id
    session.flush.assert_called()


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
            actor_roles=_ADMIN_ACTOR,
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
            actor_roles=_ADMIN_ACTOR,
        )
    assert "Peran" in exc.value.message


def test_update_clear_branch_on_agent_rejected() -> None:
    role_id = uuid.uuid4()
    user = _user_row(role_id=role_id, branch_id=_BRANCH_ID)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.get_role_code.return_value = "AGENT"
    repo.branch_exists.return_value = True
    service = UserService(repo)

    with pytest.raises(ValidationAppError) as exc:
        service.update(
            user.id,
            UserUpdateRequest(branchId=None),
            actor_user_id=uuid.uuid4(),
            actor_roles=_ADMIN_ACTOR,
        )
    assert "Cabang wajib" in exc.value.message
    repo.commit.assert_not_called()


def test_update_set_branch_on_head_office_role_rejected() -> None:
    """Commit 2: assigning a branch to an existing head-office-role user is
    rejected on update, mirroring the create-path rule."""
    role_id = uuid.uuid4()
    user = _user_row(role_id=role_id, branch_id=None)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.get_role_code.return_value = "ADMIN"
    repo.branch_exists.return_value = True
    service = UserService(repo)

    with pytest.raises(ValidationAppError) as exc:
        service.update(
            user.id,
            UserUpdateRequest(branchId=_BRANCH_ID),
            actor_user_id=uuid.uuid4(),
            actor_roles=_ADMIN_ACTOR,
        )
    assert "Cabang tidak boleh" in exc.value.message
    repo.commit.assert_not_called()


def test_update_role_change_to_head_office_with_existing_branch_rejected() -> None:
    """Commit 2: changing role AGENT -> ADMIN without clearing branchId in the
    same request is rejected — effective role/branch are re-validated together."""
    old_role = uuid.uuid4()
    new_role = uuid.uuid4()
    user = _user_row(role_id=old_role, branch_id=_BRANCH_ID)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.role_exists.return_value = True
    repo.get_role_code.return_value = "ADMIN"
    service = UserService(repo)

    with pytest.raises(ValidationAppError) as exc:
        service.update(
            user.id,
            UserUpdateRequest(roleId=new_role),
            actor_user_id=uuid.uuid4(),
            actor_roles=_ADMIN_ACTOR,
        )
    assert "Cabang tidak boleh" in exc.value.message
    repo.commit.assert_not_called()


def test_update_unrelated_field_on_head_office_user_accepted() -> None:
    """Unrelated field updates (no role_id/branch_id change) must not re-trigger
    organization-location validation, even for a head-office-role user."""
    role_id = uuid.uuid4()
    user = _user_row(role_id=role_id, branch_id=None, email="old@example.com")
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.get_role_code.return_value = "ADMIN"
    repo.email_exists.return_value = False
    repo.refresh.side_effect = lambda u: u

    UserService(repo).update(
        user.id,
        UserUpdateRequest(email="new@example.com"),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    assert user.email == "new@example.com"
    repo.commit.assert_called_once()


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
            actor_roles=_ADMIN_ACTOR,
        )


def test_update_role_syncs_user_roles() -> None:
    old_role = uuid.uuid4()
    new_role = uuid.uuid4()
    user = _user_row(role_id=old_role, branch_id=_BRANCH_ID)
    repo = MagicMock()
    repo.get_by_id.return_value = user
    repo.role_exists.return_value = True
    repo.get_role_code.return_value = "AGENT"
    repo.branch_exists.return_value = True
    repo.refresh.side_effect = lambda u: u

    UserService(repo).update(
        user.id,
        UserUpdateRequest(roleId=new_role),
        actor_user_id=uuid.uuid4(),
        actor_roles=_ADMIN_ACTOR,
    )

    assert user.role_id == new_role
    repo.sync_primary_user_role.assert_called_once_with(
        user.id,
        previous_role_id=old_role,
        new_role_id=new_role,
    )
    repo.commit.assert_called_once()
