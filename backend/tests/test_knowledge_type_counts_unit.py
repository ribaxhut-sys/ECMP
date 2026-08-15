"""Unit coverage for Knowledge ``@`` type-count mapping (no HTTP / Postgres)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from app.modules.knowledge.repository import KnowledgeRepository, within_effective_window
from app.modules.knowledge.router import knowledge_type_counts
from app.modules.knowledge.schemas import KnowledgeTypeCounts
from app.modules.knowledge.service import KnowledgeService


def test_within_effective_window_rejects_future_and_expired() -> None:
    now = datetime(2026, 8, 15, tzinfo=UTC)
    future = SimpleNamespace(
        effective_from=now + timedelta(days=1),
        effective_to=None,
    )
    expired = SimpleNamespace(
        effective_from=None,
        effective_to=now - timedelta(days=1),
    )
    open_ended = SimpleNamespace(effective_from=None, effective_to=None)
    assert within_effective_window(future, now=now) is False
    assert within_effective_window(expired, now=now) is False
    assert within_effective_window(open_ended, now=now) is True


def test_count_citable_by_type_groups_session_rows() -> None:
    class _Result:
        def all(self) -> list[tuple[str, int]]:
            return [("SOP", 2), ("PERATURAN", 1)]

    class _Session:
        def execute(self, _stmt: object) -> _Result:
            return _Result()

    repo = KnowledgeRepository(_Session())  # type: ignore[arg-type]
    assert repo.count_citable_by_type(now=datetime(2026, 8, 15, tzinfo=UTC)) == {
        "SOP": 2,
        "PERATURAN": 1,
    }


def test_service_count_citable_by_type_fills_zeroes() -> None:
    class _Repo:
        def count_citable_by_type(self, *, now=None) -> dict[str, int]:
            _ = now
            return {"SOP": 3}

    svc = KnowledgeService(_Repo(), None, None, None, None)  # type: ignore[arg-type]
    counts = svc.count_citable_by_type()
    assert counts.SOP == 3
    assert counts.PANDUAN == 0
    assert counts.PERATURAN == 0


def test_router_type_counts_returns_data_envelope() -> None:
    class _Svc:
        def count_citable_by_type(self) -> KnowledgeTypeCounts:
            return KnowledgeTypeCounts(SOP=1)

    wrapped = knowledge_type_counts(service=_Svc(), principal=object())  # type: ignore[arg-type]
    assert wrapped.data.SOP == 1
    assert wrapped.data.KEPUTUSAN == 0
