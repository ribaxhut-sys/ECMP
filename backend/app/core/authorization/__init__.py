"""Authorization Middleware — public API (TASK-040).

Import from ``app.core.auth`` (facade) or ``app.core.authorization``.
"""

from __future__ import annotations

from app.core.authorization.auth_strategy import (
    AuthenticationStrategy,
    DevAuthenticationStrategy,
    JwtAuthenticationStrategy,
    build_authentication_strategy,
    configure_authentication,
    get_authentication_strategy,
    reset_authentication_strategy,
)
from app.core.authorization.authentication import (
    authenticate_bearer,
    get_current_principal,
    resolve_principal_permissions,
)
from app.core.authorization.data_scope_check import (
    check_data_scope,
    require_data_scope,
    resolve_effective_scope,
)
from app.core.authorization.gates import (
    require_appointment_complete,
    require_complaint_close,
    require_escalation_close,
    require_escalation_review,
    require_final_resolution,
    require_supervisor_assign,
    require_supervisor_escalate,
    require_user_status_update,
)
from app.core.authorization.org_unit_guard import (
    OrgUnitGuard,
    enforce_org_scope,
    is_machine_service_identity,
    is_service_account_allowlisted,
    org_scope_enforcement_enabled,
)
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.permission_check import (
    check_any_permission,
    check_permissions,
    check_roles,
    require_any_permission,
    require_permissions,
    require_roles,
)
from app.core.authorization.pipeline import CurrentPrincipal
from app.core.authorization.principal import Principal
from app.core.authorization.role_assignment_policy import (
    assert_can_assign_role,
    can_assign_role,
)
from app.core.authorization.role_mapper import RoleMapper

__all__ = [
    "AuthenticationStrategy",
    "CurrentPrincipal",
    "DevAuthenticationStrategy",
    "JwtAuthenticationStrategy",
    "OrgUnitGuard",
    "OrgUnitResolver",
    "Principal",
    "RoleMapper",
    "assert_can_assign_role",
    "authenticate_bearer",
    "build_authentication_strategy",
    "can_assign_role",
    "check_data_scope",
    "check_any_permission",
    "check_permissions",
    "check_roles",
    "configure_authentication",
    "enforce_org_scope",
    "get_authentication_strategy",
    "get_current_principal",
    "is_machine_service_identity",
    "is_service_account_allowlisted",
    "org_scope_enforcement_enabled",
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
    "reset_authentication_strategy",
    "resolve_effective_scope",
    "resolve_principal_permissions",
]
