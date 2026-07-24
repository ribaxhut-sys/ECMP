"""Domain-specific authorization gates (unchanged contracts — TASK-040).

These compose ``require_permissions`` + role checks on the shared pipeline.
Endpoint signatures stay the same; only the underlying helpers moved.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.core.authorization.permission_check import require_permissions
from app.core.authorization.principal import Principal
from app.core.errors import PermissionDeniedError


def require_supervisor_assign(
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:assign"))
    ],
) -> Principal:
    """Assign endpoint gate: permission complaints:assign + SUPERVISOR role."""
    if not principal.has_any_role("SUPERVISOR"):
        raise PermissionDeniedError("Only Supervisor can assign complaints")
    return principal


def require_supervisor_escalate(
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:escalate"))
    ],
) -> Principal:
    """Escalate endpoint gate: permission complaints:escalate + SUPERVISOR role."""
    if not principal.has_any_role("SUPERVISOR", "BRANCH_SUPERVISOR"):
        raise PermissionDeniedError("Only Supervisor can escalate complaints")
    return principal


_ESCALATION_REVIEW_ROLES = (
    "HO_SCHEDULER",
    "HEAD_OFFICE_SCHEDULER",
    "SCHEDULER",
    "ADMIN",
    "ADMINISTRATOR",
)


def require_escalation_review(
    principal: Annotated[
        Principal, Depends(require_permissions("escalations:review"))
    ],
) -> Principal:
    """API-303/304 gate: escalations:review + HO Scheduler or Admin."""
    if not principal.has_any_role(*_ESCALATION_REVIEW_ROLES):
        raise PermissionDeniedError(
            "Only Head Office Scheduler or Admin can review escalations"
        )
    return principal


_APPOINTMENT_COMPLETE_ROLES = (
    "HO_ENGINEER",
    "HEAD_OFFICE_ENGINEER",
    "ADMIN",
    "ADMINISTRATOR",
)


def require_appointment_complete(
    principal: Annotated[
        Principal, Depends(require_permissions("appointments:complete"))
    ],
) -> Principal:
    """API-308 gate: appointments:complete + HO Engineer or Admin."""
    if not principal.has_any_role(*_APPOINTMENT_COMPLETE_ROLES):
        raise PermissionDeniedError(
            "Only Head Office Engineer or Admin can complete appointments"
        )
    return principal


def require_final_resolution(
    principal: Annotated[
        Principal, Depends(require_permissions("appointments:complete"))
    ],
) -> Principal:
    """API-310 gate: appointments:complete + HO Engineer or Admin."""
    if not principal.has_any_role(*_APPOINTMENT_COMPLETE_ROLES):
        raise PermissionDeniedError(
            "Only Head Office Engineer or Admin can submit final resolution"
        )
    return principal


_COMPLAINT_CLOSE_ROLES = (
    "SUPERVISOR",
    "BRANCH_SUPERVISOR",
    "ADMIN",
    "ADMINISTRATOR",
)


def require_complaint_close(
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:close"))
    ],
) -> Principal:
    """API-312 gate: complaints:close + Branch Supervisor or Head Office Admin."""
    if not principal.has_any_role(*_COMPLAINT_CLOSE_ROLES):
        raise PermissionDeniedError(
            "Only Branch Supervisor or Head Office Admin can close complaints"
        )
    return principal


_ESCALATION_CLOSE_ROLES = (
    "ADMIN",
    "ADMINISTRATOR",
)


def require_escalation_close(
    principal: Annotated[
        Principal, Depends(require_permissions("escalations:close"))
    ],
) -> Principal:
    """API-313 gate: escalations:close + Head Office Admin only."""
    if not principal.has_any_role(*_ESCALATION_CLOSE_ROLES):
        raise PermissionDeniedError(
            "Only Head Office Admin can close escalations"
        )
    return principal
