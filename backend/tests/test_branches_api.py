"""Branch reference API integration tests (API-223)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import Branch


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
    reason="PostgreSQL not available for branch API tests",
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
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_header() -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(uuid.uuid4()),
        settings=settings,
        claims={
            "permissions": ["complaints:read"],
            "roles": ["AGENT"],
        },
    )
    return {"Authorization": f"Bearer {token}"}


def test_list_branches_returns_active_rows(
    client: TestClient,
    auth_header: dict[str, str],
    db_session: Session,
) -> None:
    code = f"B-{uuid.uuid4().hex[:6].upper()}"
    branch = Branch(code=code, name="Bekasi Test", is_active=True)
    db_session.add(branch)
    db_session.commit()
    db_session.refresh(branch)

    response = client.get("/api/v1/branches", headers=auth_header)
    assert response.status_code == 200, response.text
    body = response.json()
    assert "data" in body and "meta" in body
    match = next((row for row in body["data"] if row["id"] == str(branch.id)), None)
    assert match is not None
    assert match["code"] == code
    assert match["name"] == "Bekasi Test"

    branch.deleted_at = datetime.now(UTC)
    branch.is_active = False
    db_session.commit()
