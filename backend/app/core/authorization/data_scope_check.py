"""Data Scope check step of the Authorization Middleware pipeline (TASK-040).

Optional step after Permission Check. Uses existing ``DataScopeResolver``
(TASK-039) and IAM cache. Does **not** auto-filter domain queries —
endpoints opt in via ``require_data_scope`` / ``resolve_effective_scope``.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.authorization.authentication import get_current_principal
from app.core.authorization.principal import Principal
from app.core.errors import DataScopeDeniedError
from app.core.user_messages import m
from app.db.session import get_db_session
from app.modules.iam.data_scope.models import ScopeType
from app.modules.iam.data_scope_resolver import DataScopeResolver, EffectiveScope


def resolve_effective_scope(
    user_id: uuid.UUID,
    session: Session,
) -> EffectiveScope:
    """Resolve effective data scopes for a user (service-layer helper)."""
    return DataScopeResolver(session).resolve_scopes(user_id)


def check_data_scope(
    scope: EffectiveScope,
    *allowed_types: str,
) -> None:
    """Raise :class:`DataScopeDeniedError` when scope does not satisfy types.

    ``GLOBAL`` always satisfies any ``allowed_types`` check.
    With no ``allowed_types``, the check is a no-op.
    """
    if not allowed_types:
        return
    normalized = tuple(ScopeType(t).value for t in allowed_types)
    if scope.has_global():
        return
    if scope.scope_types & set(normalized):
        return
    raise DataScopeDeniedError(
        m("common.data_scope_denied"),
        details={
            "requiredScopeTypes": list(normalized),
            "orGlobal": True,
        },
    )


def require_data_scope(
    *allowed_types: str,
) -> Callable[..., EffectiveScope]:
    """Dependency factory: Authentication → Data Scope Resolver → Check.

    GLOBAL always satisfies any ``allowed_types`` check.
    With no ``allowed_types``, returns the effective scope (may be empty).
    Endpoints opt in — this does not auto-wire domain filtering.
    """
    normalized = tuple(ScopeType(t).value for t in allowed_types)

    def _dependency(
        principal: Annotated[Principal, Depends(get_current_principal)],
        session: Annotated[Session, Depends(get_db_session)],
    ) -> EffectiveScope:
        scope = resolve_effective_scope(principal.user_id, session)
        check_data_scope(scope, *normalized)
        return scope

    return _dependency
