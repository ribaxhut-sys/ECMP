"""CAPABILITY-012 — Search API handler + integration tests."""

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
from app.modules.complaints.schemas import ComplaintResponse
from app.modules.search.domain.enums import ComplaintSortField, SortOrder
from app.modules.search.domain.filters import ComplaintSearchFilters
from app.modules.search.router import search_complaints
from app.modules.search.schemas import (
    ComplaintSearchResponse,
    SearchPagination,
    SearchSort,
)


def test_router_handler_builds_filters() -> None:
    svc = MagicMock()
    now = datetime.now(UTC)
    item = ComplaintResponse(
        id=uuid.uuid4(),
        complaintNumber="CMP-1",
        customerId=None,
        branchId=None,
        sourceType="CUSTOMER",
        sourceId=uuid.uuid4(),
        targetType="BRANCH",
        targetId=None,
        subject="S",
        description="D",
        status="NEW",
        priority="HIGH",
        reportedAt=now,
        createdAt=now,
        updatedAt=now,
    )
    svc.search_complaints.return_value = ComplaintSearchResponse(
        items=[item],
        pagination=SearchPagination.from_total(page=1, page_size=20, total_items=1),
        filtersApplied={"priority": "HIGH"},
        sort=SearchSort(field=ComplaintSortField.CREATED_AT, order=SortOrder.DESC),
    )
    principal = Principal(user_id=uuid.uuid4(), roles=("ADMIN",))
    result = search_complaints(
        service=svc,
        principal=principal,
        keyword="  bill ",
        status_filter=None,
        priority="HIGH",
        category=" Billing ",
        branch_id=None,
        assigned_to=None,
        created_by=None,
        created_from=None,
        created_to=None,
        sla_status=None,
        escalated=True,
        page=1,
        page_size=20,
        sort=ComplaintSortField.CREATED_AT,
        order=SortOrder.DESC,
    )
    assert result.pagination.total_items == 1
    called: ComplaintSearchFilters = svc.search_complaints.call_args.args[0]
    assert called.keyword == "bill"
    assert called.priority == "HIGH"
    assert called.category == "Billing"
    assert called.escalated is True


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


@pytest.mark.skipif(
    not _postgres_available(),
    reason="PostgreSQL not available for Search API tests",
)
class TestSearchApiIntegration:
    @pytest.fixture()
    def db_session(self) -> Generator[Session, None, None]:
        settings = get_settings()
        eng = create_engine(settings.database_url, pool_pre_ping=True, future=True)
        SessionLocal = sessionmaker(
            bind=eng, autoflush=False, autocommit=False, future=True
        )
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
            eng.dispose()

    @pytest.fixture()
    def client(self, db_session: Session) -> Generator[TestClient, None, None]:
        app = create_app()

        def _override() -> Generator[Session, None, None]:
            yield db_session

        app.dependency_overrides[get_db_session] = _override
        with TestClient(app) as test_client:
            yield test_client
        app.dependency_overrides.clear()

    @pytest.fixture()
    def actor(self, db_session: Session) -> User:
        user = db_session.scalar(select(User).where(User.deleted_at.is_(None)).limit(1))
        if user is None:
            pytest.skip("No seed user available")
        return user

    def _auth(self, actor: User) -> dict[str, str]:
        settings = get_settings()
        token = create_access_token(
            subject=str(actor.id),
            settings=settings,
            claims={"permissions": ["complaints:read"], "roles": ["ADMIN"]},
        )
        return {"Authorization": f"Bearer {token}"}

    def test_search_endpoint_returns_envelope(
        self, client: TestClient, actor: User
    ) -> None:
        resp = client.get(
            "/api/v1/complaints/search",
            headers=self._auth(actor),
            params={"page": 1, "pageSize": 5, "sort": "createdAt", "order": "desc"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "items" in body
        assert "pagination" in body
        assert "filtersApplied" in body
        assert "sort" in body
        assert body["sort"]["field"] == "createdAt"
        assert body["sort"]["order"] == "desc"
        pag = body["pagination"]
        for key in (
            "page",
            "pageSize",
            "totalItems",
            "totalPages",
            "hasNext",
            "hasPrevious",
        ):
            assert key in pag

    def test_search_requires_permission(self, client: TestClient, actor: User) -> None:
        settings = get_settings()
        token = create_access_token(
            subject=str(actor.id),
            settings=settings,
            claims={"permissions": ["attachment:read"], "roles": ["ADMIN"]},
        )
        resp = client.get(
            "/api/v1/complaints/search",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
