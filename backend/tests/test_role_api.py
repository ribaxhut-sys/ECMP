"""Role Management integration tests (TASK-033 / API-338–342)."""

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
from app.models import Role, User
from app.modules.audit.models import SystemAuditLog
from app.modules.iam.role.permissions import (
    ROLE_CREATE,
    ROLE_DELETE,
    ROLE_READ,
    ROLE_UPDATE,
)


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
    reason="PostgreSQL not available for Role API tests",
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
def ensure_roles_schema(db_session: Session) -> None:
    col = db_session.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = 'roles' AND column_name = 'is_system'"
        )
    ).scalar()
    if not col:
        pytest.skip("roles.is_system not migrated (0020_roles)")


def _auth(actor: User, *permissions: str) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": list(permissions), "roles": ["ADMIN"]},
    )
    return {"Authorization": f"Bearer {token}"}


def _unique_code() -> str:
    return f"ROLE_{uuid.uuid4().hex[:10].upper()}"


def test_role_crud_flow(
    client: TestClient,
    actor: User,
    db_session: Session,
) -> None:
    headers = _auth(actor, ROLE_READ, ROLE_CREATE, ROLE_UPDATE, ROLE_DELETE)
    code = _unique_code()

    created = client.post(
        "/api/v1/roles",
        headers=headers,
        json={
            "code": code.lower(),
            "name": "Test Role",
            "description": "integration",
            "isActive": True,
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()["data"]
    role_id = body["id"]
    assert body["code"] == code
    assert body["isSystem"] is False
    assert body["isActive"] is True

    listed = client.get("/api/v1/roles", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == role_id for item in listed.json()["data"])

    got = client.get(f"/api/v1/roles/{role_id}", headers=headers)
    assert got.status_code == 200
    assert got.json()["data"]["name"] == "Test Role"

    updated = client.put(
        f"/api/v1/roles/{role_id}",
        headers=headers,
        json={"name": "Updated Role", "isActive": False},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["name"] == "Updated Role"
    assert updated.json()["data"]["isActive"] is False

    deleted = client.delete(f"/api/v1/roles/{role_id}", headers=headers)
    assert deleted.status_code == 204

    row = db_session.get(Role, uuid.UUID(role_id))
    assert row is not None
    assert row.deleted_at is not None
    assert row.is_active is False

    # Audit CREATE / UPDATE / DELETE
    audits = list(
        db_session.scalars(
            select(SystemAuditLog)
            .where(
                SystemAuditLog.entity_type == "Role",
                SystemAuditLog.entity_id == uuid.UUID(role_id),
            )
            .order_by(SystemAuditLog.created_at.asc())
        ).all()
    )
    actions = [a.action for a in audits]
    assert "CREATE" in actions
    assert "UPDATE" in actions
    assert "DELETE" in actions


def test_cannot_delete_system_role(
    client: TestClient,
    actor: User,
    db_session: Session,
) -> None:
    headers = _auth(actor, ROLE_READ, ROLE_DELETE)
    system = db_session.scalar(
        select(Role).where(
            Role.code == "ADMIN",
            Role.is_system.is_(True),
            Role.deleted_at.is_(None),
        )
    )
    if system is None:
        pytest.skip("ADMIN system role not seeded")

    resp = client.delete(f"/api/v1/roles/{system.id}", headers=headers)
    assert resp.status_code == 409, resp.text
    assert "System role" in resp.json()["message"]


def test_role_rbac_forbidden_without_permission(
    client: TestClient,
    actor: User,
) -> None:
    headers = _auth(actor)  # no role:* permissions
    resp = client.get("/api/v1/roles", headers=headers)
    assert resp.status_code == 403


def test_seed_roles_present(db_session: Session) -> None:
    codes = {
        row.code
        for row in db_session.scalars(
            select(Role).where(
                Role.code.in_(
                    ["SUPER_ADMIN", "ADMIN", "SUPERVISOR", "AGENT", "VIEWER"]
                ),
                Role.deleted_at.is_(None),
            )
        ).all()
    }
    assert codes == {
        "SUPER_ADMIN",
        "ADMIN",
        "SUPERVISOR",
        "AGENT",
        "VIEWER",
    }
    for code in codes:
        row = db_session.scalar(select(Role).where(Role.code == code))
        assert row is not None
        assert row.is_system is True
