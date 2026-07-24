"""Authorization Middleware — public API (TASK-040).

Import from ``app.core.auth`` (facade) or ``app.core.authorization``.
"""

from __future__ import annotations

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
)
from app.core.authorization.permission_check import (
    check_permissions,
    check_roles,
    require_permissions,
    require_roles,
)
from app.core.authorization.pipeline import CurrentPrincipal
from app.core.authorization.principal import Principal

__all__ = [
    "CurrentPrincipal",
    "Principal",
    "authenticate_bearer",
    "check_data_scope",
    "check_permissions",
    "check_roles",
    "get_current_principal",
    "require_appointment_complete",
    "require_complaint_close",
    "require_data_scope",
    "require_escalation_close",
    "require_escalation_review",
    "require_final_resolution",
    "require_permissions",
    "require_roles",
    "require_supervisor_assign",
    "require_supervisor_escalate",
    "resolve_effective_scope",
    "resolve_principal_permissions",
]
