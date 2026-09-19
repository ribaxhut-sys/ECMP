"""Queue/customer writes no longer ride ``complaints:create`` (0073).

``complaints:create`` had become a de-facto "front-office staff may act"
catch-all: it also opened queue creation, counter creation (API-370), ticket
issuing (API-365/376), and customer phone edits — none of which create a
Complaint. These tests pin the separation in both directions: the new
permission opens the endpoint, and ``complaints:create`` alone no longer does.
"""

from __future__ import annotations

import inspect
import uuid
from typing import get_type_hints

import pytest

from app.core.authorization.permission_check import check_permissions
from app.core.authorization.principal import Principal
from app.core.errors import PermissionDeniedError
from app.modules.customers import router as customers_router_mod
from app.modules.queue.api.routers import counters as counters_mod
from app.modules.queue.api.routers import queues as queues_mod
from app.modules.queue.api.routers import tickets as tickets_mod


def _gate_permissions(handler) -> set[str]:
    """Read the permission codes a FastAPI handler's ``require_permissions``
    dependency was built with, without standing up the whole app.

    The router modules use ``from __future__ import annotations``, so the raw
    signature carries strings — resolve them with ``get_type_hints`` to reach
    the ``Annotated[..., Depends(...)]`` metadata.
    """
    codes: set[str] = set()
    hints = get_type_hints(handler, include_extras=True)
    for annotation in hints.values():
        for meta in getattr(annotation, "__metadata__", ()):
            dependency = getattr(meta, "dependency", None)
            if dependency is None:
                continue
            required = inspect.getclosurevars(dependency).nonlocals.get("required")
            if required:
                codes.update(required)
    return codes


_WRITE_HANDLERS = (
    (queues_mod.create_queue, "queue:manage"),
    (counters_mod.create_counter, "queue:manage"),
    (tickets_mod.create_ticket, "queue:manage"),
    (tickets_mod.issue_ticket_operation, "queue:manage"),
    (customers_router_mod.update_customer_phone, "customers:update"),
)


@pytest.mark.parametrize(
    ("handler", "expected"),
    _WRITE_HANDLERS,
    ids=[h.__name__ for h, _ in _WRITE_HANDLERS],
)
def test_write_endpoint_requires_its_own_permission(handler, expected: str) -> None:
    codes = _gate_permissions(handler)
    assert expected in codes
    # The whole point of 0073: holding complaints:create is no longer enough.
    assert "complaints:create" not in codes


def test_complaints_create_holder_is_refused_the_new_permissions() -> None:
    """End of the leak, asserted on the check itself rather than a signature."""
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"complaints:create", "complaints:read"}),
    )
    for perm in ("queue:manage", "customers:update"):
        with pytest.raises(PermissionDeniedError) as excinfo:
            check_permissions(principal, perm)
        assert excinfo.value.details["missingPermissions"] == [perm]


def test_granted_principal_passes_the_new_gates() -> None:
    principal = Principal(
        user_id=uuid.uuid4(),
        roles=("AGENT",),
        permissions=frozenset({"queue:manage", "customers:update"}),
    )
    check_permissions(principal, "queue:manage")
    check_permissions(principal, "customers:update")
