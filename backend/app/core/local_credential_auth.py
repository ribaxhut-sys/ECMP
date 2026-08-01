"""ADR-014 / audit K-3 — Mode A local credential AuthN gate.

When ``ECMP_LOCAL_CREDENTIAL_AUTH=false`` (required for staging/production and
``ECMP_ENTERPRISE_MODE=true``), password login / forgot / reset / change /
admin reset / user create / user update-password must fail closed.
Mode B unlock remains gated by Architecture Board (C-7 / C-B6-1).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.core.errors import ForbiddenError
from app.core.user_messages import m


def assert_local_credential_auth_enabled(settings: Settings) -> None:
    """Fail closed when Mode A local credential AuthN surface is disabled."""
    if not settings.ecmp_local_credential_auth:
        raise ForbiddenError(
            m("auth.local_disabled"),
            code="LOCAL_CREDENTIAL_AUTH_DISABLED",
            details={
                "ecmpLocalCredentialAuth": False,
                "ecmpEnterpriseMode": settings.ecmp_enterprise_mode,
            },
        )


def require_local_credential_auth(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Settings:
    """Dependency: allow Mode A credential endpoints only when explicitly enabled."""
    assert_local_credential_auth_enabled(settings)
    return settings
