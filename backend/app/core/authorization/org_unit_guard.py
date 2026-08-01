"""OrgUnitGuard — organization-scope enforcement after Permission Check (SECMIG-P4).

Runs only as Authorization. Never inside JWT validation / JWKS / role mapping /
permission resolution. Dev mode is a no-op so lab regression stays unchanged.
"""

from __future__ import annotations

import uuid
from typing import Any

from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.config import Settings, get_settings
from app.core.errors import OrgScopeDeniedError
from app.core.logging import get_logger, log_extra
from app.core.user_messages import m

logger = get_logger("app.authz.org_scope")


def _service_allowlist(settings: Settings) -> frozenset[str]:
    raw = (settings.ecmp_org_scope_service_allowlist or "").strip()
    if not raw:
        return frozenset()
    return frozenset(
        part.strip().upper() for part in raw.split(",") if part.strip()
    )


def _service_subjects(settings: Settings) -> frozenset[uuid.UUID]:
    """Configured service-account subject UUIDs (machine identity allowlist)."""
    raw = (settings.ecmp_org_scope_service_subjects or "").strip()
    if not raw:
        return frozenset()
    subjects: set[uuid.UUID] = set()
    for part in raw.split(","):
        cleaned = part.strip()
        if not cleaned:
            continue
        try:
            subjects.add(uuid.UUID(cleaned))
        except ValueError:
            logger.warning(
                "ORG_SCOPE_SERVICE_SUBJECT_INVALID",
                extra=log_extra(subject=cleaned),
            )
    return frozenset(subjects)


def org_scope_enforcement_enabled(settings: Settings) -> bool:
    """Org gate is inactive in ``dev`` AuthN mode (lab / CI default)."""
    return (settings.ecmp_auth_mode or "dev").strip().lower() == "jwt"


def is_machine_service_identity(
    principal: Principal,
    settings: Settings,
) -> bool:
    """True when the principal subject is an explicitly configured service UUID.

    Role allowlist alone is not identity proof (SECMIG-P4-001R / M-2).
    """
    return principal.user_id in _service_subjects(settings)


def is_service_account_allowlisted(
    principal: Principal,
    settings: Settings,
) -> bool:
    """Service org-scope bypass: machine identity AND allow-listed role.

    Default deny when either allowlist is empty or either check fails.
    """
    if not is_machine_service_identity(principal, settings):
        return False
    allow = _service_allowlist(settings)
    if not allow:
        return False
    return any(role.upper() in allow for role in principal.roles)


def _public_denial_details(reason: str) -> dict[str, Any]:
    """Client-facing details — never leak protected resource ownership."""
    return {"reason": reason}


def _audit_org_scope_denied(
    *,
    principal: Principal,
    reason: str,
    principal_org: str | None,
    resource_org: str | None,
) -> None:
    """Append-only style application audit for ORG_SCOPE_DENIED (no DB redesign)."""
    logger.warning(
        "ORG_SCOPE_DENIED",
        extra=log_extra(
            event="ORG_SCOPE_DENIED",
            reason=reason,
            principalUserId=str(principal.user_id),
            principalOrgUnitId=principal_org,
            resourceOrgUnitId=resource_org,
            roles=list(principal.roles),
        ),
    )


class OrgUnitGuard:
    """Compare ``principal.org_unit_id`` to a resolved resource org unit."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings

    def enforce(
        self,
        principal: Principal,
        resource_org_unit_id: str | None,
        *,
        settings: Settings | None = None,
    ) -> None:
        cfg = settings or self._settings
        if cfg is None:
            cfg = get_settings()

        if not org_scope_enforcement_enabled(cfg):
            return

        principal_org = OrgUnitResolver.normalize(principal.org_unit_id)
        resource_org = OrgUnitResolver.normalize(resource_org_unit_id)

        # Service-account / missing-claim path: default deny unless identity + role.
        if principal_org is None:
            if is_service_account_allowlisted(principal, cfg):
                return
            _audit_org_scope_denied(
                principal=principal,
                reason="missing_org_unit_claim",
                principal_org=None,
                resource_org=resource_org,
            )
            raise OrgScopeDeniedError(
                m("org.scope_missing_org_unit_claim"),
                details=_public_denial_details("missing_org_unit_claim"),
            )

        if resource_org is None:
            _audit_org_scope_denied(
                principal=principal,
                reason="missing_resource_org_unit",
                principal_org=principal_org,
                resource_org=None,
            )
            raise OrgScopeDeniedError(
                m("org.scope_resource_no_org_unit"),
                details=_public_denial_details("missing_resource_org_unit"),
            )

        if principal_org != resource_org:
            _audit_org_scope_denied(
                principal=principal,
                reason="org_unit_mismatch",
                principal_org=principal_org,
                resource_org=resource_org,
            )
            raise OrgScopeDeniedError(
                m("common.org_scope_denied"),
                details=_public_denial_details("org_unit_mismatch"),
            )


def enforce_org_scope(
    principal: Principal,
    resource_org_unit_id: str | None,
    settings: Settings,
) -> None:
    """Module-level helper used by routers after permission checks."""
    OrgUnitGuard(settings).enforce(principal, resource_org_unit_id, settings=settings)
