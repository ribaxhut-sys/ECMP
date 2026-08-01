"""Client IP trust boundary (TASK-PLATFORM-SECMIG-P5-005).

Trust model (locked — no proxy-stack redesign):

1. **Primary source** is the ASGI peer ``request.client.host``.
   In Docker/production, Uvicorn ``--proxy-headers`` + ``FORWARDED_ALLOW_IPS``
   rewrites that peer from ``X-Forwarded-*`` only when the immediate hop is
   trusted (see ``backend/docker-entrypoint.sh`` and TLS reverse-proxy docs).

2. **Application-level** ``X-Forwarded-For`` parsing is **opt-in** via
   ``Settings.trust_forwarded_client_ip`` (``TRUST_FORWARDED_CLIENT_IP``).
   Enable only when the process does **not** run Uvicorn proxy-header trust
   and a trusted hop still needs header-based client identity.

3. Auth lockout keys and audit ``ip_address`` must use this helper so the
   trust boundary is applied consistently.
"""

from __future__ import annotations

from fastapi import Request

from app.core.config import Settings, get_settings


def resolve_client_ip(
    request: Request,
    *,
    settings: Settings | None = None,
) -> str | None:
    """Return the client IP honoring the configured trust boundary.

    Truncates to 64 characters to match audit column constraints.
    """
    cfg = settings if settings is not None else get_settings()
    if cfg.trust_forwarded_client_ip:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            first = forwarded.split(",", 1)[0].strip()
            if first:
                return first[:64]
    if request.client and request.client.host:
        return request.client.host[:64]
    return None
