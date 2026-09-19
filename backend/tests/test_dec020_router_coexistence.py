"""DEC-026 — production router posture after Foundation namespace retirement.

Locks:
- Aggregate CM Batch 1 under ``/api/v1/cm``
- Legacy ECMF ``/api/v1/complaints`` lifecycle **unmounted**
- Visit-linked CA BC ticket-nested routes only
- ``complaint_foundation_router`` remains unmounted
"""

from __future__ import annotations

from pathlib import Path

from fastapi.routing import APIRoute, APIRouter

from app.api.router import api_router
from app.modules.complaint.api import complaint_foundation_router
from app.modules.complaint.api.routers.complaints import (
    router as complaint_domain_complaints_router,
)

_ROUTER_PY = Path(__file__).resolve().parents[1] / "app" / "api" / "router.py"


def _iter_api_routes(router: APIRouter):
    """Walk FastAPI include graph (supports ``_IncludedRouter`` wrappers)."""
    for item in router.routes:
        if isinstance(item, APIRoute):
            yield item
            continue
        nested = getattr(item, "original_router", None)
        if isinstance(nested, APIRouter):
            yield from _iter_api_routes(nested)
            continue
        if isinstance(item, APIRouter):
            yield from _iter_api_routes(item)


def _path_methods(router: APIRouter) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for route in _iter_api_routes(router):
        for method in route.methods or ():
            out.add((method, route.path))
    return out


def _paths(router: APIRouter) -> set[str]:
    return {route.path for route in _iter_api_routes(router)}


def test_production_router_source_keeps_dec026_unmount_posture() -> None:
    text = _ROUTER_PY.read_text(encoding="utf-8")
    assert "include_router(cm_batch1_router)" in text
    assert "include_router(complaints_router)" not in text
    assert "include_router(complaint_api_router)" in text
    assert "include_router(complaint_foundation_router)" not in text
    assert "from app.modules.complaint.api import complaint_foundation_router" not in text
    assert "from app.modules.complaints.router import router as complaints_router" not in text


def test_production_router_exposes_aggregate_without_legacy_namespace() -> None:
    paths = _paths(api_router)
    assert any(p.startswith("/api/v1/cm") for p in paths), "missing Aggregate /api/v1/cm"
    legacy = [
        p
        for p in paths
        if p == "/api/v1/complaints" or p.startswith("/api/v1/complaints/")
    ]
    assert legacy == [], f"legacy /api/v1/complaints still mounted: {legacy}"
    assert any(
        "/tickets/" in p and p.endswith("/complaints") for p in paths
    ), "missing ticket-nested CA BC routes"


def test_complaint_foundation_router_not_mounted_on_api_router() -> None:
    """Foundation DELETE (API-394) must not appear on production mounts."""
    production = _path_methods(api_router)
    foundation = _path_methods(complaint_foundation_router)
    domain = _path_methods(complaint_domain_complaints_router)

    assert ("DELETE", "/api/v1/complaints/{complaint_id}") in domain
    assert ("DELETE", "/api/v1/complaints/{complaint_id}") not in production
    assert foundation, "complaint_foundation_router unexpectedly empty"
    assert ("GET", "/api/v1/tickets/{ticket_id}/complaints") in production
    assert ("POST", "/api/v1/tickets/{ticket_id}/complaints") in production
