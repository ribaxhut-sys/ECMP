"""JWT authentication and Authorization Middleware facade (TASK-040).

Public helpers are unchanged for existing routers:

- ``get_current_principal`` / ``CurrentPrincipal``
- ``require_permissions`` / ``require_roles``
- ``require_data_scope`` / ``resolve_effective_scope``
- domain gates (``require_supervisor_assign``, …)

Implementation lives under ``app.core.authorization`` as a single pipeline:

    Authentication → Permission Resolver → Permission Check
      → (optional) Org Unit Guard (SECMIG-P4; G1 opt-in)
      → (optional) Data Scope Resolver → Data Scope Check → Endpoint

Login/JWT issuance, PermissionResolver, and DataScopeResolver are not
modified by this module.
"""

from __future__ import annotations

from app.core.authorization import (
    CurrentPrincipal,
    OrgUnitGuard,
    OrgUnitResolver,
    Principal,
    authenticate_bearer,
    check_data_scope,
    check_permissions,
    check_roles,
    enforce_org_scope,
    get_current_principal,
    require_any_permission,
    require_appointment_complete,
    require_complaint_close,
    require_data_scope,
    require_escalation_close,
    require_escalation_review,
    require_final_resolution,
    require_permissions,
    require_roles,
    require_supervisor_assign,
    require_supervisor_escalate,
    require_user_status_update,
    resolve_effective_scope,
    resolve_principal_permissions,
)

__all__ = [
    "CurrentPrincipal",
    "OrgUnitGuard",
    "OrgUnitResolver",
    "Principal",
    "authenticate_bearer",
    "check_data_scope",
    "check_permissions",
    "check_roles",
    "enforce_org_scope",
    "get_current_principal",
    "require_appointment_complete",
    "require_any_permission",
    "require_complaint_close",
    "require_data_scope",
    "require_escalation_close",
    "require_escalation_review",
    "require_final_resolution",
    "require_permissions",
    "require_roles",
    "require_supervisor_assign",
    "require_supervisor_escalate",
    "require_user_status_update",
    "resolve_effective_scope",
    "resolve_principal_permissions",
]
