"""Data Scope Foundation integration tests (TASK-037 / API-354–355)."""

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
from app.models import DataScope, Permission, Role, User
from app.modules.audit.models import SystemAuditLog
from app.modules.iam.data_scope.permissions import DATA_SCOPE_READ, DATA_SCOPE_UPDATE


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
    reason="PostgreSQL not available for Data Scope API tests",
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
def ensure_data_scopes_schema(db_session: Session) -> None:
    exists = db_session.execute(
        text(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_name = 'data_scopes'"
        )
    ).scalar()
    if not exists:
        pytest.skip("data_scopes table not migrated (0024_data_scopes)")


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
        code=f"DS_TEST_{uuid.uuid4().hex[:8].upper()}",
        name="Data Scope Test",
        description="integration",
        is_system=False,
        is_active=True,
    )
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


def test_replace_data_scopes_flow(
    client: TestClient,
    actor: User,
    db_session: Session,
    sample_role: Role,
) -> None:
    headers = _auth(actor, DATA_SCOPE_READ, DATA_SCOPE_UPDATE)

    first = client.put(
        f"/api/v1/roles/{sample_role.id}/data-scopes",
        headers=headers,
        json={
            "scopes": [
                {"scopeType": "BRANCH", "scopeValue": "branch-001"},
                {"scopeType": "BRANCH", "scopeValue": "branch-002"},
                {"scopeType": "SELF"},
            ]
        },
    )
    assert first.status_code == 200, first.text
    data = first.json()["data"]
    assert len(data) == 3
    types = {(item["scopeType"], item["scopeValue"]) for item in data}
    assert types == {
        ("BRANCH", "branch-001"),
        ("BRANCH", "branch-002"),
        ("SELF", None),
    }

    replaced = client.put(
        f"/api/v1/roles/{sample_role.id}/data-scopes",
        headers=headers,
        json={
            "scopes": [
                {"scopeType": "GLOBAL"},
                {"scopeType": "CUSTOM", "scopeValue": "region-west"},
            ]
        },
    )
    assert replaced.status_code == 200, replaced.text
    data = replaced.json()["data"]
    assert {(item["scopeType"], item["scopeValue"]) for item in data} == {
        ("GLOBAL", None),
        ("CUSTOM", "region-west"),
    }

    listed = client.get(
        f"/api/v1/roles/{sample_role.id}/data-scopes",
        headers=headers,
    )
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 2

    cleared = client.put(
        f"/api/v1/roles/{sample_role.id}/data-scopes",
        headers=headers,
        json={"scopes": []},
    )
    assert cleared.status_code == 200
    assert cleared.json()["data"] == []
    assert (
        db_session.scalar(
            select(DataScope).where(DataScope.role_id == sample_role.id)
        )
        is None
    )

    audits = list(
        db_session.scalars(
            select(SystemAuditLog).where(
                SystemAuditLog.entity_type == "Role",
                SystemAuditLog.entity_id == sample_role.id,
                SystemAuditLog.event_type == "role.data_scopes.updated",
            )
        ).all()
    )
    assert len(audits) >= 2
    assert all(a.action == "UPDATE" for a in audits)


def test_validation_global_with_value(
    client: TestClient,
    actor: User,
    sample_role: Role,
) -> None:
    headers = _auth(actor, DATA_SCOPE_UPDATE)
    resp = client.put(
        f"/api/v1/roles/{sample_role.id}/data-scopes",
        headers=headers,
        json={"scopes": [{"scopeType": "GLOBAL", "scopeValue": "nope"}]},
    )
    assert resp.status_code in (400, 422)


def test_validation_branch_without_value(
    client: TestClient,
    actor: User,
    sample_role: Role,
) -> None:
    headers = _auth(actor, DATA_SCOPE_UPDATE)
    resp = client.put(
        f"/api/v1/roles/{sample_role.id}/data-scopes",
        headers=headers,
        json={"scopes": [{"scopeType": "BRANCH"}]},
    )
    assert resp.status_code in (400, 422)


def test_validation_duplicates(
    client: TestClient,
    actor: User,
    sample_role: Role,
) -> None:
    headers = _auth(actor, DATA_SCOPE_UPDATE)
    resp = client.put(
        f"/api/v1/roles/{sample_role.id}/data-scopes",
        headers=headers,
        json={
            "scopes": [
                {"scopeType": "BRANCH", "scopeValue": "b1"},
                {"scopeType": "BRANCH", "scopeValue": "b1"},
            ]
        },
    )
    assert resp.status_code in (400, 422)


def test_data_scope_rbac_forbidden(
    client: TestClient,
    actor: User,
    sample_role: Role,
) -> None:
    headers = _auth(actor)
    resp = client.get(
        f"/api/v1/roles/{sample_role.id}/data-scopes",
        headers=headers,
    )
    assert resp.status_code == 403


def test_unknown_role_not_found(
    client: TestClient,
    actor: User,
) -> None:
    headers = _auth(actor, DATA_SCOPE_READ)
    resp = client.get(
        f"/api/v1/roles/{uuid.uuid4()}/data-scopes",
        headers=headers,
    )
    assert resp.status_code == 404


def test_seed_data_scope_catalog(db_session: Session) -> None:
    codes = {
        row.code
        for row in db_session.scalars(
            select(Permission).where(
                Permission.code.in_(["data_scope:read", "data_scope:update"]),
                Permission.deleted_at.is_(None),
            )
        ).all()
    }
    assert codes == {"data_scope:read", "data_scope:update"}
