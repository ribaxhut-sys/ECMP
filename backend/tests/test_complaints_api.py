"""Complaint API integration tests."""

from __future__ import annotations

import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import Customer, SlaPolicy, User


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
    reason="PostgreSQL not available for complaint API tests",
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
def actor_id(db_session: Session) -> uuid.UUID:
    from sqlalchemy import select

    row = db_session.scalar(select(User).where(User.deleted_at.is_(None)).limit(1))
    if row is None:
        pytest.skip("No seed user available")
    return row.id


@pytest.fixture()
def auth_header(actor_id: uuid.UUID) -> dict[str, str]:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor_id),
        settings=settings,
        claims={
            "permissions": [
                "complaints:create",
                "complaints:read",
                "complaints:update",
            ],
            "roles": ["AGENT"],
        },
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def customer_id(db_session: Session) -> uuid.UUID:
    customer = Customer(
        external_customer_id=f"CUST-{uuid.uuid4().hex[:8].upper()}",
        full_name="Test Customer",
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer.id


@pytest.fixture()
def active_sla_policy(db_session: Session) -> SlaPolicy:
    """TASK-023: complaint create requires an active SLA policy."""
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    db_session.execute(
        text(
            "UPDATE sla_policies SET is_active = false, updated_at = :now "
            "WHERE is_active = true"
        ),
        {"now": now},
    )
    policy = SlaPolicy(
        name=f"Test-Policy-{uuid.uuid4().hex[:8]}",
        description="Active policy for complaint API tests",
        assignment_target_minutes=60,
        appointment_target_minutes=1440,
        resolution_target_minutes=2880,
        escalation_target_minutes=480,
        overall_target_minutes=4320,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    return policy


def test_unauthorized_without_token(client: TestClient) -> None:
    response = client.get("/api/v1/complaints")
    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "UNAUTHENTICATED"


def test_forbidden_without_permission(client: TestClient, actor_id: uuid.UUID) -> None:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor_id),
        settings=settings,
        claims={"permissions": [], "roles": ["GUEST"]},
    )
    response = client.get(
        "/api/v1/complaints",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


def test_create_get_list_update_complaint(
    client: TestClient,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
    active_sla_policy: SlaPolicy,
) -> None:
    _ = active_sla_policy
    create_payload = {
        "customerId": str(customer_id),
        "subject": "Billing issue",
        "description": "Charged twice for the same invoice",
        "priority": "HIGH",
        "channel": "EMAIL",
        "category": "BILLING",
    }
    created = client.post(
        "/api/v1/complaints",
        json=create_payload,
        headers=auth_header,
    )
    assert created.status_code == 201, created.text
    data = created.json()["data"]
    assert data["status"] == "NEW"
    assert data["priority"] == "HIGH"
    assert data["complaintNumber"].startswith("CMP-")
    # TASK-042 — legacy create defaults
    assert data["sourceType"] == "CUSTOMER"
    assert data["sourceId"] == str(customer_id)
    assert data["targetType"] == "BRANCH"
    assert data["targetId"] is None
    complaint_id = data["id"]

    fetched = client.get(f"/api/v1/complaints/{complaint_id}", headers=auth_header)
    assert fetched.status_code == 200
    assert fetched.json()["data"]["id"] == complaint_id

    listed = client.get("/api/v1/complaints?page=1&pageSize=20", headers=auth_header)
    assert listed.status_code == 200
    body = listed.json()
    assert "meta" in body
    assert body["meta"]["page"] == 1
    assert any(item["id"] == complaint_id for item in body["data"])

    updated = client.put(
        f"/api/v1/complaints/{complaint_id}",
        json={"priority": "CRITICAL", "subject": "Billing issue escalated"},
        headers=auth_header,
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["data"]["priority"] == "CRITICAL"
    assert updated.json()["data"]["subject"] == "Billing issue escalated"
    assert updated.json()["data"]["status"] == "NEW"


def test_create_rejects_unknown_customer(
    client: TestClient,
    auth_header: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/complaints",
        json={
            "customerId": str(uuid.uuid4()),
            "subject": "x",
            "description": "y",
            "priority": "LOW",
        },
        headers=auth_header,
    )
    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"


@pytest.fixture()
def branch_id(db_session: Session) -> uuid.UUID:
    from app.models import Branch

    branch = Branch(
        code=f"BR-{uuid.uuid4().hex[:8].upper()}",
        name="Test Branch",
        is_active=True,
    )
    db_session.add(branch)
    db_session.commit()
    db_session.refresh(branch)
    return branch.id


def test_create_customer_complaint_generalized(
    client: TestClient,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
    branch_id: uuid.UUID,
    active_sla_policy: SlaPolicy,
) -> None:
    _ = active_sla_policy
    response = client.post(
        "/api/v1/complaints",
        json={
            "sourceType": "CUSTOMER",
            "sourceId": str(customer_id),
            "targetType": "BRANCH",
            "targetId": str(branch_id),
            "subject": "Customer complaint",
            "description": "Generalized customer → branch",
            "priority": "HIGH",
        },
        headers=auth_header,
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    assert data["sourceType"] == "CUSTOMER"
    assert data["sourceId"] == str(customer_id)
    assert data["targetType"] == "BRANCH"
    assert data["targetId"] == str(branch_id)
    assert data["customerId"] == str(customer_id)
    assert data["branchId"] == str(branch_id)
    assert data["status"] == "NEW"


def test_create_branch_complaint(
    client: TestClient,
    auth_header: dict[str, str],
    branch_id: uuid.UUID,
    active_sla_policy: SlaPolicy,
) -> None:
    _ = active_sla_policy
    ho_id = str(uuid.uuid4())
    response = client.post(
        "/api/v1/complaints",
        json={
            "sourceType": "BRANCH",
            "sourceId": str(branch_id),
            "targetType": "HEAD_OFFICE",
            "targetId": ho_id,
            "subject": "Branch complaint",
            "description": "Branch → Head Office",
            "priority": "CRITICAL",
        },
        headers=auth_header,
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    assert data["sourceType"] == "BRANCH"
    assert data["targetType"] == "HEAD_OFFICE"
    assert data["targetId"] == ho_id
    assert data["customerId"] is None
    assert data["branchId"] is None
    assert data["status"] == "NEW"


def test_create_head_office_complaint(
    client: TestClient,
    auth_header: dict[str, str],
    branch_id: uuid.UUID,
    active_sla_policy: SlaPolicy,
) -> None:
    _ = active_sla_policy
    ho_id = str(uuid.uuid4())
    response = client.post(
        "/api/v1/complaints",
        json={
            "sourceType": "HEAD_OFFICE",
            "sourceId": ho_id,
            "targetType": "BRANCH",
            "targetId": str(branch_id),
            "subject": "HO complaint",
            "description": "Head Office → Branch",
            "priority": "MEDIUM",
        },
        headers=auth_header,
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    assert data["sourceType"] == "HEAD_OFFICE"
    assert data["targetType"] == "BRANCH"
    assert data["branchId"] == str(branch_id)
    assert data["customerId"] is None
    assert data["status"] == "NEW"

def test_create_system_complaint_to_head_office(
    client: TestClient,
    auth_header: dict[str, str],
    active_sla_policy: SlaPolicy,
) -> None:
    _ = active_sla_policy
    system_id = str(uuid.uuid4())
    ho_id = str(uuid.uuid4())
    response = client.post(
        "/api/v1/complaints",
        json={
            "sourceType": "SYSTEM",
            "sourceId": system_id,
            "targetType": "HEAD_OFFICE",
            "targetId": ho_id,
            "subject": "System alert",
            "description": "SYSTEM ? Head Office",
            "priority": "HIGH",
        },
        headers=auth_header,
    )
    assert response.status_code == 201, response.text
    data = response.json()["data"]
    assert data["sourceType"] == "SYSTEM"
    assert data["targetType"] == "HEAD_OFFICE"
    assert data["branchId"] is None
    assert data["customerId"] is None


def test_create_rejects_invalid_route(
    client: TestClient,
    auth_header: dict[str, str],
    customer_id: uuid.UUID,
    active_sla_policy: SlaPolicy,
) -> None:
    _ = active_sla_policy
    response = client.post(
        "/api/v1/complaints",
        json={
            "sourceType": "CUSTOMER",
            "sourceId": str(customer_id),
            "targetType": "HEAD_OFFICE",
            "targetId": str(uuid.uuid4()),
            "subject": "Invalid",
            "description": "CUSTOMER ? HEAD_OFFICE not supported",
            "priority": "LOW",
        },
        headers=auth_header,
    )
    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
    assert "Invalid complaint route" in response.json()["message"]
