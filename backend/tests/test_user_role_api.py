"""User-Role Assignment integration tests (TASK-036 / API-351–353)."""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import Permission, Role, User, UserRole
from app.modules.audit.models import SystemAuditLog
from app.modules.iam.user_role.permissions import USER_ROLE_READ, USER_ROLE_UPDATE


def _postgres_available() -> bool:
    settings = get_settings()
    try:
        eng = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            future=True,
            connect_args={"connect_timeout": 2},
        )
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        eng.dispose()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for User-Role API tests",
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    settings = get_settings()
    eng = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    SessionLocal = sessionmaker(bind=eng, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        eng.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def _override() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override
    with TestClient(app, base_url="http://localhost") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def actor(db_session: Session) -> User:
    user = db_session.scalar(select(User).where(User.deleted_at.is_(None)).limit(1))
    if user is None:
        pytest.skip("No seed user available")
    return user


@pytest.fixture(autouse=True)
def ensure_user_roles_schema(db_session: Session) -> None:
    exists = db_session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'user_roles'"
        )
    ).scalar()
    if not exists:
        pytest.skip("user_roles table not migrated (0023_user_roles)")


def _auth(actor: User, *permissions: str) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": list(permissions), "roles": ["ADMIN"]},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_roles(db_session: Session) -> list[Role]:
    codes = ["ADMIN", "SUPERVISOR", "AGENT"]
    rows = list(
        db_session.scalars(
            select(Role).where(
                Role.code.in_(codes),
                Role.deleted_at.is_(None),
            )
        ).all()
    )
    by_code = {row.code: row for row in rows}
    if len(by_code) < 3:
        pytest.skip("Required seed roles missing")
    return [by_code[c] for c in codes]


@pytest.fixture()
def target_user(db_session: Session, sample_roles: list[Role]) -> User:
    """Dedicated user so matrix tests do not disturb seed actor auth."""
    agent = sample_roles[2]
    user = User(
        id=uuid.uuid4(),
        role_id=agent.id,
        branch_id=None,
        email=f"ur_{uuid.uuid4().hex[:8]}@example.com",
        username=f"ur_{uuid.uuid4().hex[:8]}",
        full_name="User Role Test",
        password_hash=None,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_replace_user_roles_flow(
    client: TestClient,
    actor: User,
    db_session: Session,
    sample_roles: list[Role],
    target_user: User,
) -> None:
    headers = _auth(actor, USER_ROLE_READ, USER_ROLE_UPDATE)
    admin, supervisor, agent = sample_roles
    primary_role_id = target_user.role_id

    first = client.put(
        f"/api/v1/users/{target_user.id}/roles",
        headers=headers,
        json={"roleIds": [str(admin.id), str(supervisor.id)]},
    )
    assert first.status_code == 200, first.text
    codes = {item["code"] for item in first.json()["data"]}
    assert codes == {"ADMIN", "SUPERVISOR"}

    replaced = client.put(
        f"/api/v1/users/{target_user.id}/roles",
        headers=headers,
        json={"roleIds": [str(agent.id)]},
    )
    assert replaced.status_code == 200, replaced.text
    codes = {item["code"] for item in replaced.json()["data"]}
    assert codes == {"AGENT"}

    listed = client.get(
        f"/api/v1/users/{target_user.id}/roles",
        headers=headers,
    )
    assert listed.status_code == 200
    assert {item["code"] for item in listed.json()["data"]} == {"AGENT"}

    # users.role_id unchanged (Authorization Engine / primary FK untouched)
    db_session.refresh(target_user)
    assert target_user.role_id == primary_role_id

    users_for_agent = client.get(
        f"/api/v1/roles/{agent.id}/users",
        headers=headers,
    )
    assert users_for_agent.status_code == 200
    assert any(
        item["id"] == str(target_user.id) for item in users_for_agent.json()["data"]
    )

    cleared = client.put(
        f"/api/v1/users/{target_user.id}/roles",
        headers=headers,
        json={"roleIds": []},
    )
    assert cleared.status_code == 200
    assert cleared.json()["data"] == []

    links = list(
        db_session.scalars(
            select(UserRole).where(UserRole.user_id == target_user.id)
        ).all()
    )
    assert links == []

    audits = list(
        db_session.scalars(
            select(SystemAuditLog).where(
                SystemAuditLog.entity_type == "User",
                SystemAuditLog.entity_id == target_user.id,
                SystemAuditLog.event_type == "user.roles.updated",
            )
        ).all()
    )
    assert len(audits) >= 2
    assert all(a.action == "UPDATE" for a in audits)


def test_replace_allows_system_role(
    client: TestClient,
    actor: User,
    target_user: User,
    sample_roles: list[Role],
) -> None:
    headers = _auth(actor, USER_ROLE_READ, USER_ROLE_UPDATE)
    admin = sample_roles[0]
    assert admin.is_system is True

    resp = client.put(
        f"/api/v1/users/{target_user.id}/roles",
        headers=headers,
        json={"roleIds": [str(admin.id)]},
    )
    assert resp.status_code == 200, resp.text
    assert any(item["code"] == "ADMIN" for item in resp.json()["data"])

    client.put(
        f"/api/v1/users/{target_user.id}/roles",
        headers=headers,
        json={"roleIds": []},
    )


def test_replace_rejects_unknown_role(
    client: TestClient,
    actor: User,
    target_user: User,
) -> None:
    headers = _auth(actor, USER_ROLE_UPDATE)
    resp = client.put(
        f"/api/v1/users/{target_user.id}/roles",
        headers=headers,
        json={"roleIds": [str(uuid.uuid4())]},
    )
    assert resp.status_code == 404


def test_replace_rejects_duplicate_ids(
    client: TestClient,
    actor: User,
    target_user: User,
    sample_roles: list[Role],
) -> None:
    headers = _auth(actor, USER_ROLE_UPDATE)
    rid = str(sample_roles[0].id)
    resp = client.put(
        f"/api/v1/users/{target_user.id}/roles",
        headers=headers,
        json={"roleIds": [rid, rid]},
    )
    assert resp.status_code in (400, 422)


def test_user_role_rbac_forbidden_without_permission(
    client: TestClient,
    actor: User,
    target_user: User,
) -> None:
    headers = _auth(actor)
    resp = client.get(
        f"/api/v1/users/{target_user.id}/roles",
        headers=headers,
    )
    assert resp.status_code == 403


def test_seed_user_role_catalog(db_session: Session) -> None:
    codes = {
        row.code
        for row in db_session.scalars(
            select(Permission).where(
                Permission.code.in_(["user_role:read", "user_role:update"]),
                Permission.deleted_at.is_(None),
            )
        ).all()
    }
    assert codes == {"user_role:read", "user_role:update"}
