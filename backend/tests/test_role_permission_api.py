"""Role-Permission Matrix integration tests (TASK-035 / API-348–350)."""

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
from app.models import Permission, Role, RolePermission, User
from app.modules.audit.models import SystemAuditLog
from app.modules.iam.role_permission.permissions import (
    ROLE_PERMISSION_READ,
    ROLE_PERMISSION_UPDATE,
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
    reason="PostgreSQL not available for Role-Permission API tests",
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
def ensure_matrix_schema(db_session: Session) -> None:
    exists = db_session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'role_permissions'"
        )
    ).scalar()
    if not exists:
        pytest.skip("role_permissions table not migrated (0022_role_permissions)")


def _auth(actor: User, *permissions: str) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": list(permissions), "roles": ["ADMIN"]},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def sample_role(db_session: Session) -> Role:
    role = Role(
        id=uuid.uuid4(),
        code=f"RP_TEST_{uuid.uuid4().hex[:8].upper()}",
        name="Role Permission Test",
        description="integration",
        is_system=False,
        is_active=True,
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture()
def sample_permissions(db_session: Session) -> list[Permission]:
    codes = ["complaint:read", "complaint:create", "dashboard:read", "audit:read"]
    rows = list(
        db_session.scalars(
            select(Permission).where(
                Permission.code.in_(codes),
                Permission.deleted_at.is_(None),
            )
        ).all()
    )
    if len(rows) < 4:
        pytest.skip("Required seed permissions missing")
    by_code = {row.code: row for row in rows}
    return [by_code[c] for c in codes]


def test_replace_role_permissions_flow(
    client: TestClient,
    actor: User,
    db_session: Session,
    sample_role: Role,
    sample_permissions: list[Permission],
) -> None:
    headers = _auth(actor, ROLE_PERMISSION_READ, ROLE_PERMISSION_UPDATE)
    a, b, c, d = sample_permissions

    # Initial set A,B,C
    first = client.put(
        f"/api/v1/roles/{sample_role.id}/permissions",
        headers=headers,
        json={"permissionIds": [str(a.id), str(b.id), str(c.id)]},
    )
    assert first.status_code == 200, first.text
    codes = {item["code"] for item in first.json()["data"]}
    assert codes == {"complaint:read", "complaint:create", "dashboard:read"}

    # Replace with A,D
    replaced = client.put(
        f"/api/v1/roles/{sample_role.id}/permissions",
        headers=headers,
        json={"permissionIds": [str(a.id), str(d.id)]},
    )
    assert replaced.status_code == 200, replaced.text
    codes = {item["code"] for item in replaced.json()["data"]}
    assert codes == {"complaint:read", "audit:read"}

    listed = client.get(
        f"/api/v1/roles/{sample_role.id}/permissions",
        headers=headers,
    )
    assert listed.status_code == 200
    assert {item["code"] for item in listed.json()["data"]} == {
        "complaint:read",
        "audit:read",
    }

    # Reverse lookup
    roles_for_a = client.get(
        f"/api/v1/permissions/{a.id}/roles",
        headers=headers,
    )
    assert roles_for_a.status_code == 200
    assert any(item["id"] == str(sample_role.id) for item in roles_for_a.json()["data"])

    # Empty clears
    cleared = client.put(
        f"/api/v1/roles/{sample_role.id}/permissions",
        headers=headers,
        json={"permissionIds": []},
    )
    assert cleared.status_code == 200
    assert cleared.json()["data"] == []

    links = list(
        db_session.scalars(
            select(RolePermission).where(RolePermission.role_id == sample_role.id)
        ).all()
    )
    assert links == []

    audits = list(
        db_session.scalars(
            select(SystemAuditLog).where(
                SystemAuditLog.entity_type == "Role",
                SystemAuditLog.entity_id == sample_role.id,
                SystemAuditLog.event_type == "role.permissions.updated",
            )
        ).all()
    )
    assert len(audits) >= 2
    assert all(a.action == "UPDATE" for a in audits)


def test_replace_allows_system_role(
    client: TestClient,
    actor: User,
    db_session: Session,
    sample_permissions: list[Permission],
) -> None:
    headers = _auth(actor, ROLE_PERMISSION_READ, ROLE_PERMISSION_UPDATE)
    admin = db_session.scalar(
        select(Role).where(
            Role.code == "ADMIN",
            Role.is_system.is_(True),
            Role.deleted_at.is_(None),
        )
    )
    if admin is None:
        pytest.skip("ADMIN system role not seeded")

    perm = sample_permissions[0]
    resp = client.put(
        f"/api/v1/roles/{admin.id}/permissions",
        headers=headers,
        json={"permissionIds": [str(perm.id)]},
    )
    assert resp.status_code == 200, resp.text
    assert any(item["id"] == str(perm.id) for item in resp.json()["data"])

    # cleanup matrix for ADMIN so other tests stay isolated
    client.put(
        f"/api/v1/roles/{admin.id}/permissions",
        headers=headers,
        json={"permissionIds": []},
    )


def test_replace_rejects_unknown_permission(
    client: TestClient,
    actor: User,
    sample_role: Role,
) -> None:
    headers = _auth(actor, ROLE_PERMISSION_UPDATE)
    resp = client.put(
        f"/api/v1/roles/{sample_role.id}/permissions",
        headers=headers,
        json={"permissionIds": [str(uuid.uuid4())]},
    )
    assert resp.status_code == 404


def test_replace_rejects_duplicate_ids(
    client: TestClient,
    actor: User,
    sample_role: Role,
    sample_permissions: list[Permission],
) -> None:
    headers = _auth(actor, ROLE_PERMISSION_UPDATE)
    pid = str(sample_permissions[0].id)
    resp = client.put(
        f"/api/v1/roles/{sample_role.id}/permissions",
        headers=headers,
        json={"permissionIds": [pid, pid]},
    )
    assert resp.status_code in (400, 422)


def test_matrix_rbac_forbidden_without_permission(
    client: TestClient,
    actor: User,
    sample_role: Role,
) -> None:
    headers = _auth(actor)
    resp = client.get(
        f"/api/v1/roles/{sample_role.id}/permissions",
        headers=headers,
    )
    assert resp.status_code == 403


def test_seed_role_permission_catalog(db_session: Session) -> None:
    codes = {
        row.code
        for row in db_session.scalars(
            select(Permission).where(
                Permission.code.in_(
                    ["role_permission:read", "role_permission:update"]
                ),
                Permission.deleted_at.is_(None),
            )
        ).all()
    }
    assert codes == {"role_permission:read", "role_permission:update"}
