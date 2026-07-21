"""Service-layer unit tests (no HTTP client) — the ADR-005 layering payoff.

Includes the rollback-injection test: if the transaction cannot commit, NONE of
case/audit/outbox may persist (FR-001c atomicity, ADR-009).
"""

from __future__ import annotations

import pytest
from conftest import VALID_PAYLOAD
from sqlalchemy.orm import Session

from app import service
from app.models import AuditLogModel, CaseModel, OutboxModel

USER = {"userId": "cs.agent.1", "permissions": {"cases:create", "cases:read"}}


def _counts(session: Session) -> tuple[int, int, int]:
    return (
        session.query(CaseModel).count(),
        session.query(AuditLogModel).count(),
        session.query(OutboxModel).count(),
    )


def test_register_case_returns_contract_shape():
    from app.db import get_engine

    with Session(get_engine()) as session:
        result = service.register_case(session, dict(VALID_PAYLOAD), USER)
    assert result["status"] == "REGISTERED"
    assert result["createdBy"] == "cs.agent.1"
    assert result["createdAt"].tzinfo is not None  # always UTC-aware (FRD §7)
    assert "updated_by" not in result  # not exposed per TS-001 §4


def test_get_case_unknown_returns_none():
    from app.db import get_engine

    with Session(get_engine()) as session:
        assert service.get_case(session, "CASE-0000000000") is None


def test_register_case_rolls_back_atomically(monkeypatch):
    """Inject a commit failure: no partial rows (case/audit/outbox) may survive."""
    from app.db import get_engine

    session = Session(get_engine())

    def failing_commit():
        raise RuntimeError("injected commit failure")

    monkeypatch.setattr(session, "commit", failing_commit)
    with pytest.raises(RuntimeError):
        service.register_case(session, dict(VALID_PAYLOAD), USER)
    session.rollback()
    session.close()

    with Session(get_engine()) as check:
        assert _counts(check) == (0, 0, 0)


def test_outbox_payload_matches_event_catalog():
    """EVT-001 payload keys in code must equal the normative catalog (events.yaml)."""
    import yaml
    from conftest import REPO_ROOT

    from app.db import get_engine

    catalog_path = REPO_ROOT / "08 Event Catalog" / "events" / "events.yaml"
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    evt_001 = next(e for e in catalog["events"] if e["id"] == "EVT-001")
    catalog_keys = set(evt_001["payload"].keys())

    with Session(get_engine()) as session:
        service.register_case(session, dict(VALID_PAYLOAD), USER)
        row = session.query(OutboxModel).one()
        assert set(row.payload.keys()) == catalog_keys
        assert evt_001["name"] == row.event_name


def test_drain_outbox_marks_published_and_is_idempotent():
    from app.db import get_engine

    with Session(get_engine()) as session:
        service.register_case(session, dict(VALID_PAYLOAD), USER)
        published = service.drain_outbox(session)
        assert len(published) == 1
        assert service.drain_outbox(session) == []
        row = session.query(OutboxModel).one()
        assert row.published_at is not None
