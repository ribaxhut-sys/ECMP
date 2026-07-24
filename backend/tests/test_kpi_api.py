"""KPI Foundation integration tests (TASK-026 / API-318)."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.enums import ComplaintStatus, SlaStatus
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import Complaint, Customer, SlaPolicy, SlaRecord, User


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


@pytest.fixture()
def customer_id(db_session: Session) -> uuid.UUID:
    customer = Customer(
        external_customer_id=f"CUST-{uuid.uuid4().hex[:8].upper()}",
        full_name="KPI Customer",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer.id


def _activate_policy(db_session: Session) -> None:
    now = datetime.now(UTC)
    db_session.execute(
        text(
            "UPDATE sla_policies SET is_active = false, updated_at = :now "
            "WHERE is_active = true"
        ),
        {"now": now},
    )
    policy = SlaPolicy(
        name=f"KPI-Policy-{uuid.uuid4().hex[:8]}",
        description="KPI test",
        assignment_target_minutes=60,
        appointment_target_minutes=120,
        resolution_target_minutes=240,
        escalation_target_minutes=90,
        overall_target_minutes=480,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(policy)
    db_session.commit()


def test_kpi_summary_end_to_end(
    client: TestClient,
    db_session: Session,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
    actor: User,
) -> None:
    _activate_policy(db_session)
    marker = f"KPI-{uuid.uuid4().hex[:8]}"

    created = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(customer_id),
            "subject": f"{marker} open",
            "description": "KPI open complaint",
            "priority": "HIGH",
            "channel": "WEB",
            "category": "BILLING",
        },
        headers=auth_header,
    )
    assert created.status_code == 201, created.text
    cid = uuid.UUID(created.json()["data"]["id"])

    # Force assignment COMPLETED + overall BREACHED on this complaint's SLA.
    row = db_session.scalar(select(SlaRecord).where(SlaRecord.complaint_id == cid))
    assert row is not None
    row.assignment_status = SlaStatus.COMPLETED
    row.overall_status = SlaStatus.BREACHED
    db_session.commit()

    # Closed complaint with HIGH priority filter match
    now = datetime.now(UTC)
    closed = Complaint(
        complaint_number=f"CMP-{uuid.uuid4().hex[:10].upper()}",
        customer_id=customer_id,
        source_type="CUSTOMER",
        source_id=customer_id,
        target_type="BRANCH",
        target_id=None,
        subject=f"{marker} closed",
        description="closed",
        status=ComplaintStatus.CLOSED,
        priority="HIGH",
        channel="WEB",
        category="BILLING",
        reported_at=now,
        closed_at=now,
        created_at=now,
        updated_at=now,
        created_by=actor.id,
        updated_by=actor.id,
    )
    db_session.add(closed)
    db_session.flush()
    sla_closed = SlaRecord(
        complaint_id=closed.id,
        assignment_due_at=now + timedelta(hours=1),
        appointment_due_at=now + timedelta(hours=2),
        resolution_due_at=now + timedelta(hours=3),
        escalation_due_at=now + timedelta(hours=1),
        overall_due_at=now + timedelta(hours=4),
        assignment_status=SlaStatus.PENDING,
        appointment_status=SlaStatus.PENDING,
        resolution_status=SlaStatus.PENDING,
        escalation_status=SlaStatus.PENDING,
        overall_status=SlaStatus.PENDING,
        created_at=now,
        updated_at=now,
    )
    db_session.add(sla_closed)
    db_session.commit()

    unfiltered = client.get("/api/v1/kpi/summary", headers=auth_header)
    assert unfiltered.status_code == 200, unfiltered.text
    body = unfiltered.json()["data"]
    assert "complaints" in body
    assert body["complaints"]["total"] >= 2
    assert body["assignment"]["completed"] >= 1
    assert body["overall"]["breached"] >= 1

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

    # Priority filter excludes LOW-only noise if any — ensure API accepts date range.
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
