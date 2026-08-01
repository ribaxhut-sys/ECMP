"""Permission Management integration tests (TASK-034 / API-343–347)."""

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
from app.models import Permission, User
from app.modules.audit.models import SystemAuditLog
from app.modules.iam.permission.permissions import (
    PERMISSION_CREATE,
    PERMISSION_DELETE,
    PERMISSION_READ,
    PERMISSION_UPDATE,
)

_SEED_CODES = (
    "complaint:read",
    "complaint:create",
    "complaint:update",
    "complaint:delete",
    "assignment:read",
    "assignment:update",
    "appointment:read",
    "appointment:create",
    "appointment:update",
    "appointment:delete",
    "resolution:read",
    "resolution:create",
    "resolution:update",
    "resolution:delete",
    "escalation:read",
    "escalation:create",
    "escalation:update",
    "escalation:delete",
    "dashboard:read",
    "settings:read",
    "settings:update",
    "attachment:read",
    "attachment:create",
    "attachment:delete",
    "notification:read",
    "notification:create",
    "notification:update",
    "notification:delete",
    "audit:read",
    "role:read",
    "role:create",
    "role:update",
    "role:delete",
    "permission:read",
    "permission:create",
    "permission:update",
    "permission:delete",
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
    reason="PostgreSQL not available for Permission API tests",
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
def ensure_permissions_schema(db_session: Session) -> None:
    exists = db_session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'permissions'"
        )
    ).scalar()
    if not exists:
        pytest.skip("permissions table not migrated (0021_permissions)")


def _auth(actor: User, *permissions: str) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": list(permissions), "roles": ["ADMIN"]},
    )
    return {"Authorization": f"Bearer {token}"}


def _unique_code() -> tuple[str, str]:
    suffix = uuid.uuid4().hex[:8]
    module = f"tmp{suffix}"
    return f"{module}:read", module


def test_permission_crud_flow(
    client: TestClient,
    actor: User,
    db_session: Session,
) -> None:
    headers = _auth(
        actor, PERMISSION_READ, PERMISSION_CREATE, PERMISSION_UPDATE, PERMISSION_DELETE
    )
    code, module = _unique_code()

    created = client.post(
        "/api/v1/permissions",
        headers=headers,
        json={
            "code": code.upper(),
            "name": "Temp Read",
            "module": module.upper(),
            "description": "integration",
            "isActive": True,
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()["data"]
    permission_id = body["id"]
    assert body["code"] == code
    assert body["module"] == module
    assert body["isSystem"] is False
    assert body["isActive"] is True

    listed = client.get("/api/v1/permissions", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == permission_id for item in listed.json()["data"])

    filtered = client.get(
        "/api/v1/permissions",
        headers=headers,
        params={"module": module},
    )
    assert filtered.status_code == 200
    assert all(item["module"] == module for item in filtered.json()["data"])

    got = client.get(f"/api/v1/permissions/{permission_id}", headers=headers)
    assert got.status_code == 200
    assert got.json()["data"]["name"] == "Temp Read"

    updated = client.put(
        f"/api/v1/permissions/{permission_id}",
        headers=headers,
        json={"name": "Updated Permission", "isActive": False},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["name"] == "Updated Permission"
    assert updated.json()["data"]["isActive"] is False

    deleted = client.delete(f"/api/v1/permissions/{permission_id}", headers=headers)
    assert deleted.status_code == 204

    row = db_session.get(Permission, uuid.UUID(permission_id))
    assert row is not None
    assert row.deleted_at is not None
    assert row.is_active is False

    audits = list(
        db_session.scalars(
            select(SystemAuditLog)
            .where(
                SystemAuditLog.entity_type == "Permission",
                SystemAuditLog.entity_id == uuid.UUID(permission_id),
            )
            .order_by(SystemAuditLog.created_at.asc())
        ).all()
    )
    actions = [a.action for a in audits]
    assert "CREATE" in actions
    assert "UPDATE" in actions
    assert "DELETE" in actions
    event_types = {a.event_type for a in audits}
    assert "permission.created" in event_types
    assert "permission.updated" in event_types
    assert "permission.deleted" in event_types


def test_cannot_delete_system_permission(
    client: TestClient,
    actor: User,
    db_session: Session,
) -> None:
    headers = _auth(actor, PERMISSION_READ, PERMISSION_DELETE)
    system = db_session.scalar(
        select(Permission).where(
            Permission.code == "complaint:read",
            Permission.is_system.is_(True),
            Permission.deleted_at.is_(None),
        )
    )
    if system is None:
        pytest.skip("complaint:read system permission not seeded")

    resp = client.delete(f"/api/v1/permissions/{system.id}", headers=headers)
    assert resp.status_code == 409, resp.text
    assert "Izin sistem" in resp.json()["message"]


def test_permission_rbac_forbidden_without_permission(
    client: TestClient,
    actor: User,
) -> None:
    headers = _auth(actor)  # no permission:* claims
    resp = client.get("/api/v1/permissions", headers=headers)
    assert resp.status_code == 403


def test_seed_permissions_present(db_session: Session) -> None:
    rows = list(
        db_session.scalars(
            select(Permission).where(
                Permission.code.in_(_SEED_CODES),
                Permission.deleted_at.is_(None),
            )
        ).all()
    )
    codes = {row.code for row in rows}
    assert codes == set(_SEED_CODES)
    for row in rows:
        assert row.is_system is True
        assert row.is_active is True
        assert ":" in row.code
        assert row.code.startswith(f"{row.module}:")
