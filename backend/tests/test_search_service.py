"""CAPABILITY-012 — SearchService + migration tests."""

from __future__ import annotations

import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.modules.search.domain.enums import ComplaintSortField, SortOrder
from app.modules.search.domain.filters import ComplaintSearchFilters
from app.modules.search.registration import build_search_service
from app.modules.search.service import SearchService


def test_alembic_head_includes_search_indexes() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    cfg = Config(str(backend_root / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_root / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    # Head advances after CAPABILITY-012; search revision must remain on the chain.
    assert script.get_heads() == ["0045_cm_b1_lr_complaint_id"]
    assert "0036_search_indexes" in {r.revision for r in script.walk_revisions()}


def test_migration_file_structure() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "0036_search_indexes.py"
    )
    text = path.read_text(encoding="utf-8")
    for needle in (
        'revision: str = "0036_search_indexes"',
        "0035_attachment_domain",
        "ix_complaints_created_at",
        "ix_complaints_updated_at",
        "ix_complaints_category",
        "ix_complaints_created_by",
    ):
        assert needle in text


def test_service_maps_orm_to_response() -> None:
    provider = MagicMock()
    now = __import__("datetime").datetime.now(__import__("datetime").UTC)
    cid = uuid.uuid4()
    row = SimpleNamespace(
        id=cid,
        complaint_number="CMP-TEST12345",
        customer_id=None,
        branch_id=None,
        source_type="CUSTOMER",
        source_id=uuid.uuid4(),
        target_type="BRANCH",
        target_id=None,
        subject="Subject",
        description="Desc",
        status="NEW",
        priority="HIGH",
        channel=None,
        category="Billing",
        reported_at=now,
        closed_at=None,
        closed_by=None,
        closure_notes=None,
        created_at=now,
        created_by=None,
        updated_at=now,
    )
    provider.search.return_value = ([row], 1)
    svc = SearchService(provider)
    result = svc.search_complaints(
        ComplaintSearchFilters(
            priority="HIGH",
            page=1,
            page_size=20,
            sort=ComplaintSortField.CREATED_AT,
            order=SortOrder.DESC,
        )
    )
    assert len(result.items) == 1
    assert result.items[0].complaint_number == "CMP-TEST12345"
    assert result.pagination.total_items == 1
    assert result.pagination.total_pages == 1
    assert result.filters_applied == {"priority": "HIGH"}
    assert result.sort.field == ComplaintSortField.CREATED_AT


def test_build_search_service() -> None:
    session = MagicMock()
    svc = build_search_service(session)
    assert isinstance(svc, SearchService)
