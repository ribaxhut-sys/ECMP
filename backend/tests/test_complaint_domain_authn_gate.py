"""Latent AuthN harden for complaint domain foundation router (DEC-020).

Production does not mount ``complaint_foundation_router``. These tests lock
AuthN on the domain complaints router so a future Cutover DEC cannot expose
unauthenticated handlers that trust client identity headers.
"""

from __future__ import annotations

from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from app.core.authorization.authentication import get_current_principal
from app.modules.complaint.api.routers import complaints as complaints_router_mod
from app.modules.complaint.api.routers.complaints import router as complaints_router


def _dependant_calls(dependant: Dependant) -> set[object]:
    found: set[object] = set()
    stack = [dependant]
    seen: set[int] = set()
    while stack:
        current = stack.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if current.call is not None:
            found.add(current.call)
        stack.extend(current.dependencies)
    return found


def test_complaint_domain_router_requires_authenticated_principal() -> None:
    assert any(
        getattr(dep, "dependency", None) is get_current_principal
        for dep in complaints_router.dependencies
    )


def test_complaint_domain_routes_inherit_router_authn_dependency() -> None:
    routes = [r for r in complaints_router.routes if isinstance(r, APIRoute)]
    assert routes, "expected complaint domain routes"
    for route in routes:
        calls = _dependant_calls(route.dependant)
        assert get_current_principal in calls, route.path


def test_module_docstring_states_cutover_only_posture() -> None:
    doc = complaints_router_mod.__doc__ or ""
    assert "Cutover DEC" in doc
