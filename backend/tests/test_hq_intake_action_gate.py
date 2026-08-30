"""HQ intake action gate (Batch-1 lab Cabang→Pusat) — pure predicate + wiring."""

from __future__ import annotations

import uuid

from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from app.core.authorization.gates import (
    principal_may_auto_approve_intake_escalation,
    principal_may_perform_hq_intake_action,
    require_hq_intake_action,
)
from app.core.authorization.principal import Principal
from app.modules.cm_batch1.router import router as cm_batch1_router


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


def test_ho_scheduler_may_hq_intake() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("HO_SCHEDULER",),
        permissions=frozenset({"escalations:review", "complaints:read"}),
    )
    assert (
        principal_may_perform_hq_intake_action(principal, org_unit_id=None)
        is True
    )


def test_admin_may_hq_intake() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("ADMIN",),
        permissions=frozenset({"escalations:review", "*"}),
    )
    assert (
        principal_may_perform_hq_intake_action(principal, org_unit_id="UPPPD-A")
        is True
    )


def test_agent_pusat_may_hq_intake() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"complaints:read"}),
        org_unit_id="PUSAT",
    )
    assert (
        principal_may_perform_hq_intake_action(principal, org_unit_id="PUSAT")
        is True
    )
    assert (
        principal_may_perform_hq_intake_action(principal, org_unit_id="HO") is True
    )


def test_super_admin_may_hq_intake() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPER_ADMIN",),
        permissions=frozenset({"escalations:review", "*"}),
    )
    assert (
        principal_may_perform_hq_intake_action(principal, org_unit_id=None)
        is True
    )


def test_pusat_supervisor_may_hq_intake() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        permissions=frozenset({"complaints:read", "complaints:escalate"}),
        org_unit_id="PUSAT",
    )
    assert (
        principal_may_perform_hq_intake_action(principal, org_unit_id="PUSAT")
        is True
    )


def test_branch_agent_denied_hq_intake() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"complaints:read"}),
        org_unit_id="UPPPD-A",
    )
    assert (
        principal_may_perform_hq_intake_action(principal, org_unit_id="UPPPD-A")
        is False
    )


def test_review_permission_alone_without_scheduler_role_denied() -> None:
    """escalations:review without HO/Admin role must not unlock HQ intake."""
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        permissions=frozenset({"escalations:review", "complaints:escalate"}),
        org_unit_id="UPPPD-A",
    )
    assert (
        principal_may_perform_hq_intake_action(principal, org_unit_id="UPPPD-A")
        is False
    )


def test_hq_routes_depend_on_require_hq_intake_action() -> None:
    hq_suffixes = (
        "/hq-accept",
        "/hq-accept-and-schedule",
        "/hq-return",
        "/hq-schedule-arrival",
        "/hq-complete",
    )
    routes = [
        r
        for r in cm_batch1_router.routes
        if isinstance(r, APIRoute)
        and any(r.path.endswith(suffix) for suffix in hq_suffixes)
    ]
    assert len(routes) == 5
    for route in routes:
        calls = _dependant_calls(route.dependant)
        assert require_hq_intake_action in calls, route.path


def test_supervisor_may_auto_approve_intake_escalation() -> None:
    supervisor = Principal(
        user_id=uuid.uuid4(),
        roles=("SUPERVISOR",),
        permissions=frozenset({"complaints:escalate", "complaints:create"}),
    )
    assert principal_may_auto_approve_intake_escalation(supervisor) is True

    agent = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"complaints:create"}),
    )
    assert principal_may_auto_approve_intake_escalation(agent) is False

    agent_with_escalate = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"complaints:escalate", "complaints:create"}),
    )
    assert principal_may_auto_approve_intake_escalation(agent_with_escalate) is False
