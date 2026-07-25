"""CAPABILITY-013 — Dashboard API handler + integration tests."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.auth import Principal
from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import create_app
from app.models import User
from app.modules.dashboard.domain.dto import TrendPeriod
from app.modules.dashboard.router import (
    get_dashboard_kpi,
    get_dashboard_notifications,
    get_dashboard_overview,
    get_dashboard_queue,
    get_dashboard_service,
    get_dashboard_sla,
    get_dashboard_summary,
    get_dashboard_trends,
)
from app.modules.dashboard.schemas import (
    DashboardComplaintSummaryResponse,
    DashboardKpiResponse,
    DashboardNotificationsResponse,
    DashboardOverviewResponse,
    DashboardQueueResponse,
    DashboardSlaResponse,
    DashboardTrendItem,
    DashboardTrendsResponse,
)


def test_router_handlers_forward_filters() -> None:
    svc = MagicMock()
    svc.summary.return_value = DashboardComplaintSummaryResponse(
        totalComplaints=1,
        openComplaints=1,
        closedComplaints=0,
        pendingComplaints=0,
        overdueComplaints=0,
        escalatedComplaints=0,
        todayComplaints=1,
        thisMonthComplaints=1,
    )
    svc.queue.return_value = DashboardQueueResponse(
        waiting=0,
        serving=0,
        completed=0,
        cancelled=0,
        averageWaitingTime=0.0,
    )
    svc.sla.return_value = DashboardSlaResponse(
        active=0,
        breached=0,
        resolvedWithinSLA=0,
        resolvedOutsideSLA=0,
        compliancePercentage=0.0,
    )
    svc.notifications.return_value = DashboardNotificationsResponse(
        pending=0, sent=0, failed=0, cancelled=0
    )
    svc.trends.return_value = DashboardTrendsResponse(
        period="7d",
        items=[DashboardTrendItem(date=datetime.now(UTC).date(), count=0)],
    )
    svc.kpi.return_value = DashboardKpiResponse(
        complaintResolutionRate=0.0,
        slaCompliance=0.0,
        escalationRate=0.0,
        averageResolutionTime=0.0,
        averageQueueWaitingTime=0.0,
    )
    principal = Principal(user_id=uuid.uuid4(), roles=("ADMIN",))
    branch = uuid.uuid4()
    df = datetime(2026, 7, 1, tzinfo=UTC)
    dt = datetime(2026, 7, 25, tzinfo=UTC)

    get_dashboard_summary(
        service=svc,
        principal=principal,
        branch_id=branch,
        date_from=df,
        date_to=dt,
    )
    get_dashboard_queue(
        service=svc, principal=principal, branch_id=branch, date_from=df, date_to=dt
    )
    get_dashboard_sla(
        service=svc, principal=principal, branch_id=branch, date_from=df, date_to=dt
    )
    get_dashboard_notifications(
        service=svc, principal=principal, date_from=df, date_to=dt
    )
    get_dashboard_trends(
        service=svc,
        principal=principal,
        period=TrendPeriod.SEVEN_D,
        branch_id=branch,
        date_from=df,
        date_to=dt,
    )
    get_dashboard_kpi(
        service=svc, principal=principal, branch_id=branch, date_from=df, date_to=dt
    )
    assert svc.summary.called
    assert svc.queue.called
    assert svc.sla.called
    assert svc.notifications.called
    assert svc.trends.called
    assert svc.kpi.called


def test_overview_router_handler() -> None:
    from app.modules.dashboard.schemas import (
        DashboardHeader,
        DashboardSlaStage,
        DashboardSlaSummary,
    )

    svc = MagicMock()
    svc.overview.return_value = DashboardOverviewResponse(
        header=DashboardHeader(
            totalComplaints=0, openComplaints=0, closedComplaints=0
        ),
        sla=DashboardSlaSummary(
            assignment=DashboardSlaStage(),
            appointment=DashboardSlaStage(),
            resolution=DashboardSlaStage(),
            escalation=DashboardSlaStage(),
            overall=DashboardSlaStage(),
        ),
        recentActivity=[],
    )
    principal = Principal(user_id=uuid.uuid4(), roles=("ADMIN",))
    result = get_dashboard_overview(service=svc, principal=principal)
    assert result.data.header.total_complaints == 0


def test_get_dashboard_service_factory() -> None:
    session = MagicMock()
    svc = get_dashboard_service(session=session)
    assert svc is not None


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


pytestmark_pg = pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for Dashboard CAPABILITY-013 API tests",
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
            "permissions": ["dashboard:read"],
            "roles": ["ADMIN"],
        },
    )
    return {"Authorization": f"Bearer {token}"}


@pytestmark_pg
def test_capability013_endpoints_shape(
    client: TestClient, auth_header: dict[str, str]
) -> None:
    for path in (
        "/api/v1/dashboard/summary",
        "/api/v1/dashboard/queue",
        "/api/v1/dashboard/sla",
        "/api/v1/dashboard/notifications",
        "/api/v1/dashboard/trends?period=7d",
        "/api/v1/dashboard/kpi",
        "/api/v1/dashboard/overview",
    ):
        resp = client.get(path, headers=auth_header)
        assert resp.status_code == 200, path
        assert "data" in resp.json()

    summary = client.get(
        "/api/v1/dashboard/summary", headers=auth_header
    ).json()["data"]
    for key in (
        "totalComplaints",
        "openComplaints",
        "closedComplaints",
        "pendingComplaints",
        "overdueComplaints",
        "escalatedComplaints",
        "todayComplaints",
        "thisMonthComplaints",
    ):
        assert key in summary
        assert isinstance(summary[key], int)

    kpi = client.get("/api/v1/dashboard/kpi", headers=auth_header).json()["data"]
    for key in (
        "complaintResolutionRate",
        "slaCompliance",
        "escalationRate",
        "averageResolutionTime",
        "averageQueueWaitingTime",
    ):
        assert key in kpi
        assert isinstance(kpi[key], (int, float))


@pytestmark_pg
def test_capability013_requires_permission(
    client: TestClient, actor: User
) -> None:
    settings = get_settings()
    token = create_access_token(
        subject=str(actor.id),
        settings=settings,
        claims={"permissions": ["complaints:read"], "roles": ["AGENT"]},
    )
    resp = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
