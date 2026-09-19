"""Dashboard API integration tests (TASK-027 / API-319)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime

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
    reason="PostgreSQL not available for Dashboard API tests",
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
            "permissions": [
                "dashboard:read",
                "kpi:read",
                "complaints:create",
                "complaints:read",
            ],
            "roles": ["ADMIN"],
        },
    )
    return {"Authorization": f"Bearer {token}"}


def test_dashboard_summary_requires_permission(
    client: TestClient,
    actor: User,
) -> None:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": ["complaints:read"], "roles": ["AGENT"]},
    )
    resp = client.get(
        "/api/v1/dashboard/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_dashboard_summary_end_to_end(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    actor: User,
) -> None:
    before = client.get("/api/v1/dashboard/overview", headers=auth_header)
    assert before.status_code == 200
    before_body = before.json()["data"]
    assert "header" in before_body
    assert "sla" in before_body
    assert "recentActivity" in before_body
    total_before = before_body["header"]["totalComplaints"]

    now = datetime.now(UTC)
    created_numbers: list[str] = []
    for _ in range(2):
        number = f"UNIT-2608-{uuid.uuid4().hex[:4].upper()}"
        created_numbers.append(number)
        db_session.add(
            CmBatch1ComplaintORM(
                id=uuid.uuid4(),
                complaint_number=number,
                customer_id="CUST-DASH",
                category="BILLING",
                channel="WEB",
                subject=f"Dashboard {number}",
                description="Dashboard composition sample",
                priority="HIGH",
                status="REGISTERED",
                case_created=False,
                created_by=str(actor.id),
                created_at=now,
                updated_at=now,
            )
        )
    db_session.commit()

    after = client.get("/api/v1/dashboard/overview", headers=auth_header)
    assert after.status_code == 200
    body = after.json()["data"]

    assert body["header"]["totalComplaints"] >= total_before + 2
    assert body["header"]["openComplaints"] >= 2
    assert "assignment" in body["sla"]
    assert body["sla"]["assignment"]["completed"] == 0
    assert body["sla"]["assignment"]["breached"] == 0
    for key in ("appointment", "resolution", "escalation", "overall"):
        assert body["sla"][key]["completed"] == 0
        assert body["sla"][key]["breached"] == 0

    assert isinstance(body["recentActivity"], list)
    assert len(body["recentActivity"]) <= 10
    if body["recentActivity"]:
        item = body["recentActivity"][0]
        assert "eventType" in item
        assert "complaintNumber" in item
        assert "timestamp" in item
        assert "actor" in item
