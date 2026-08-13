"""KPI API integration tests — Aggregate SoT (DEC-026 / API-318)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import User
from app.modules.cm_batch1.models import CmBatch1ComplaintORM


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
    reason="PostgreSQL not available for KPI API tests",
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
def actor(db_session: Session) -> User:
    user = db_session.scalar(select(User).where(User.deleted_at.is_(None)).limit(1))
    if user is None:
        pytest.skip("No seed user available")
    return user


@pytest.fixture()
def auth_header(actor: User) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={
            "permissions": ["kpi:read", "complaints:create", "complaints:read"],
            "roles": ["ADMIN"],
        },
    )
    return {"Authorization": f"Bearer {token}"}


def _seed_cm(
    db_session: Session,
    *,
    status: str,
    priority: str = "HIGH",
    category: str = "BILLING",
    actor: User,
) -> None:
    now = datetime.now(UTC)
    db_session.add(
        CmBatch1ComplaintORM(
            id=uuid.uuid4(),
            complaint_number=f"UNIT-2608-{uuid.uuid4().hex[:4].upper()}",
            customer_id="CUST-KPI",
            category=category,
            channel="WEB",
            subject=f"KPI {status} {uuid.uuid4().hex[:6]}",
            description="KPI seed",
            priority=priority,
            status=status,
            case_created=False,
            created_by=str(actor.id),
            created_at=now,
            updated_at=now,
        )
    )


def test_kpi_summary_end_to_end(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    actor: User,
) -> None:
    _seed_cm(db_session, status="REGISTERED", actor=actor)
    _seed_cm(db_session, status="CLOSED", actor=actor)
    db_session.commit()

    unfiltered = client.get("/api/v1/kpi/summary", headers=auth_header)
    assert unfiltered.status_code == 200, unfiltered.text
    body = unfiltered.json()["data"]
    assert body["complaints"]["total"] >= 2
    assert body["complaints"]["closed"] >= 1
    assert body["complaints"]["open"] >= 1
    assert body["assignment"]["completed"] == 0
    assert body["overall"]["breached"] == 0

    filtered = client.get(
        "/api/v1/kpi/summary",
        params={"priority": "HIGH", "category": "BILLING"},
        headers=auth_header,
    )
    assert filtered.status_code == 200, filtered.text
    fbody = filtered.json()["data"]
    assert fbody["complaints"]["total"] >= 2
    assert fbody["complaints"]["closed"] >= 1
    assert fbody["complaints"]["open"] >= 1

    now = datetime.now(UTC)
    date_from = (now - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    date_to = (now + timedelta(days=1)).isoformat().replace("+00:00", "Z")
    ranged = client.get(
        "/api/v1/kpi/summary",
        params={"dateFrom": date_from, "dateTo": date_to, "priority": "HIGH"},
        headers=auth_header,
    )
    assert ranged.status_code == 200, ranged.text


def test_kpi_forbidden_without_permission(
    client: TestClient,
    actor: User,
) -> None:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": ["complaints:read"], "roles": ["GUEST"]},
    )
    response = client.get(
        "/api/v1/kpi/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
