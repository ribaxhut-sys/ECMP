"""Domain-specific authorization gates (unchanged contracts — TASK-040).

These compose ``require_permissions`` + role checks on the shared pipeline.
Endpoint signatures stay the same; only the underlying helpers moved.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.permission_check import require_permissions
from app.core.authorization.principal import Principal
from app.core.authorization.visibility import is_pusat_unit
from app.core.errors import PermissionDeniedError
from app.core.user_messages import m
from app.db.session import get_db_session


def require_supervisor_assign(
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:assign"))
    ],
) -> Principal:
    """Assign gate: complaints:assign + Supervisor/Manager (F4 capability parity)."""
    if not principal.has_any_role(
        "SUPERVISOR", "BRANCH_SUPERVISOR", "MANAGER"
    ):
        raise PermissionDeniedError(m("complaint.only_supervisor_assign"))
    return principal


def require_supervisor_escalate(
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:escalate"))
    ],
) -> Principal:
    """Escalate gate: complaints:escalate + Supervisor/Manager (F4 parity)."""
    if not principal.has_any_role(
        "SUPERVISOR", "BRANCH_SUPERVISOR", "MANAGER"
    ):
        raise PermissionDeniedError(m("complaint.only_supervisor_escalate"))
    return principal


_ESCALATION_REVIEW_ROLES = (
    "HO_SCHEDULER",
    "HEAD_OFFICE_SCHEDULER",
    "SCHEDULER",
    "ADMIN",
    "ADMINISTRATOR",
)

# Lab persona "Agent Pusat" = AGENT-family on unit PUSAT (not HO_SCHEDULER).
_PUSAT_AGENT_ROLES = (
    "AGENT",
    "CS_AGENT",
    "HANDLER",
    "BRANCH_OFFICER",
)


def principal_may_perform_hq_intake_action(
    principal: Principal,
    *,
    org_unit_id: str | None,
) -> bool:
    """Pure HQ intake gate (Batch-1 lab) — org already resolved/normalized.

    Mirrors ``require_hq_intake_action`` without I/O so FE/UI and tests can
    stay aligned without inventing a second AuthZ rule.
    """
    if principal.has_permission("escalations:review") and principal.has_any_role(
        *_ESCALATION_REVIEW_ROLES
    ):
        return True
    if principal.has_permission("complaints:read") and principal.has_any_role(
        *_PUSAT_AGENT_ROLES
    ):
        return is_pusat_unit(org_unit_id)
    return False


def require_escalation_review(
    principal: Annotated[
        Principal, Depends(require_permissions("escalations:review"))
    ],
) -> Principal:
    """API-303/304 gate: escalations:review + HO Scheduler or Admin."""
    if not principal.has_any_role(*_ESCALATION_REVIEW_ROLES):
        raise PermissionDeniedError(
            m("escalation.only_scheduler_admin_review")
        )
    return principal


def require_hq_intake_action(
    principal: Annotated[Principal, Depends(get_current_principal)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Principal:
    """CM Batch-1 HQ accept / return / schedule (lab).

    Allows classic ``escalations:review`` + HO Scheduler/Admin, **or** Agent
    (family) whose membership unit is Pusat — Mode A lab "Agent Pusat".
    """
    resolver = OrgUnitResolver(session)
    org = resolver.normalize(principal.org_unit_id) or (
        resolver.resolve_principal_membership(principal.user_id)
        if principal.has_any_role(*_PUSAT_AGENT_ROLES)
        else None
    )
    if principal_may_perform_hq_intake_action(principal, org_unit_id=org):
        return principal
    raise PermissionDeniedError(m("escalation.only_scheduler_admin_review"))


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
            m("appointment.only_engineer_admin_complete")
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
            m("resolution.only_engineer_admin_submit")
        )
    return principal


_COMPLAINT_CLOSE_ROLES = (
    "SUPERVISOR",
    "BRANCH_SUPERVISOR",
    "MANAGER",
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
            m("complaint.only_supervisor_admin_close")
        )
    return principal


_ESCALATION_CLOSE_ROLES = (
    "ADMIN",
    "ADMINISTRATOR",
)

_USER_STATUS_UPDATE_ROLES = (
    "ADMIN",
    "ADMINISTRATOR",
    "SUPER_ADMIN",
    # Branch manager persona (BC-8.4, UM-BUG-007) — own-branch only, enforced
    # separately in users/router.py update_user_status (not head-office-wide
    # like Admin above).
    "MANAGER",
)


def require_user_status_update(
    principal: Annotated[
        Principal, Depends(require_permissions("users:update"))
    ],
) -> Principal:
    """API-217 gate: users:update + Head Office Admin or branch Manager."""
    if not principal.has_any_role(*_USER_STATUS_UPDATE_ROLES):
        raise PermissionDeniedError(m("user.only_head_office_admin_status"))
    return principal


def require_escalation_close(
    principal: Annotated[
        Principal, Depends(require_permissions("escalations:close"))
    ],
) -> Principal:
    """API-313 gate: escalations:close + Head Office Admin only."""
    if not principal.has_any_role(*_ESCALATION_CLOSE_ROLES):
        raise PermissionDeniedError(
            m("escalation.only_admin_close")
        )
    return principal


# Announcement management (Pengumuman) — business decision, LOCKED: only
# Admin Pusat / Supervisor Pusat / Manager Pusat. ADMIN is a HEAD_OFFICE_
# SCOPED_ROLE_CODES role (users/service.py) — it can never carry a branch, so
# an absent org unit already means head office. SUPERVISOR/MANAGER are
# BRANCH_SCOPED_ROLE_CODES roles shared with Cabang staff (same role code,
# no separate "Pusat" role — see DEC-024), so role alone cannot tell them
# apart; only a branch actually coded Pusat (is_pusat_unit) does.
_ANNOUNCEMENT_ADMIN_ROLES = ("ADMIN", "ADMINISTRATOR", "SUPER_ADMIN")
_ANNOUNCEMENT_UNIT_ROLES = ("SUPERVISOR", "BRANCH_SUPERVISOR", "MANAGER")


def _is_pusat_or_unscoped(org_unit_id: str | None) -> bool:
    """No branch at all reads as head office — true for every real Admin."""
    if OrgUnitResolver.normalize(org_unit_id) is None:
        return True
    return is_pusat_unit(org_unit_id)


def principal_may_manage_announcements(
    principal: Principal,
    *,
    org_unit_id: str | None,
) -> bool:
    """Pure predicate — mirrors ``require_announcement_manage`` without I/O
    so FE/UI and tests can stay aligned without inventing a second AuthZ rule.
    """
    if not principal.has_permission("announcement:manage"):
        return False
    if principal.has_any_role(*_ANNOUNCEMENT_ADMIN_ROLES):
        return _is_pusat_or_unscoped(org_unit_id)
    if principal.has_any_role(*_ANNOUNCEMENT_UNIT_ROLES):
        return is_pusat_unit(org_unit_id)
    return False


def require_announcement_manage(
    principal: Annotated[Principal, Depends(get_current_principal)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Principal:
    """Announcement create/update/publish/unpublish/delete/manage-list gate.

    Dev mode issues no ``orgUnitId`` claim, so fall back to the ECMP-owned
    membership record (same pattern as ``require_hq_intake_action``).
    """
    resolver = OrgUnitResolver(session)
    org = resolver.normalize(principal.org_unit_id) or resolver.resolve_principal_membership(
        principal.user_id
    )
    if principal_may_manage_announcements(principal, org_unit_id=org):
        return principal
    raise PermissionDeniedError(
        m("announcement.only_admin_supervisor_manager_pusat")
    )


# Knowledge management (Pengetahuan) — business decision, LOCKED (ECMP —
# Business & Domain Design: Modul Pengetahuan, §3): only Admin Pusat /
# Supervisor Pusat / Manager Pusat may create/edit/upload/publish/archive.
# Same Pusat-proof requirement as announcements — SUPERVISOR/MANAGER role
# codes are shared with Cabang staff, so only an actual Pusat-coded org unit
# (or an unscoped Admin) proves "Pusat". Read access (knowledge:read) is
# global — every role holding complaints:read.
_KNOWLEDGE_ADMIN_ROLES = ("ADMIN", "ADMINISTRATOR", "SUPER_ADMIN")
_KNOWLEDGE_UNIT_ROLES = ("SUPERVISOR", "BRANCH_SUPERVISOR", "MANAGER")


def principal_may_manage_knowledge(
    principal: Principal,
    *,
    org_unit_id: str | None,
) -> bool:
    """Pure predicate — mirrors ``require_knowledge_manage`` without I/O so
    FE/UI and tests can stay aligned without inventing a second AuthZ rule."""
    if not principal.has_permission("knowledge:manage"):
        return False
    if principal.has_any_role(*_KNOWLEDGE_ADMIN_ROLES):
        return _is_pusat_or_unscoped(org_unit_id)
    if principal.has_any_role(*_KNOWLEDGE_UNIT_ROLES):
        return is_pusat_unit(org_unit_id)
    return False


def require_knowledge_manage(
    principal: Annotated[Principal, Depends(get_current_principal)],
    session: Annotated[Session, Depends(get_db_session)],
) -> Principal:
    """Knowledge create/update/publish/archive/delete/file-upload gate.

    Dev mode issues no ``orgUnitId`` claim, so fall back to the ECMP-owned
    membership record (same pattern as ``require_announcement_manage``).
    """
    resolver = OrgUnitResolver(session)
    org = resolver.normalize(principal.org_unit_id) or resolver.resolve_principal_membership(
        principal.user_id
    )
    if principal_may_manage_knowledge(principal, org_unit_id=org):
        return principal
    raise PermissionDeniedError(
        m("knowledge.only_admin_supervisor_manager_pusat")
    )
