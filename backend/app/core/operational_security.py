"""Operational security policy (TASK-PLATFORM-SECMIG-P5-005).

Documents runtime defaults and audit-flood handling without changing
authentication architecture, API contracts, or audit semantics.
"""

from __future__ import annotations

from typing import Any, Final

# ---------------------------------------------------------------------------
# Audit flood handling (LOCKED policy — documentation only)
# ---------------------------------------------------------------------------
# Security audit writes remain synchronous, append-only, and fail-open for the
# request path (see write_security_event). Under authentication abuse storms
# (e.g. repeated TOKEN_REJECTED / LOCKOUT), every eligible event may still
# attempt a durable write. That amplification is an accepted residual risk.
#
# Explicit non-goals for this task:
# - no sampling / dropping of audit events
# - no async workers / queues for audit persistence
# - no change to SecurityEventType taxonomy or AuditService semantics
#
# Operator mitigation belongs at the edge (reverse-proxy / WAF rate limits),
# not inside the audit writer.

AUDIT_FLOOD_POLICY: Final[dict[str, Any]] = {
    "id": "SECMIG-P5-005-AUDIT-FLOOD",
    "sampling": False,
    "asyncWorkers": False,
    "semanticsUnchanged": True,
    "writeMode": "synchronous_best_effort",
    "failOpenOnWriteError": True,
    "mitigation": "edge_controls",
    "summary": (
        "Every security audit event is written synchronously (best-effort, "
        "fail-open). Flood amplification is mitigated at the edge; the "
        "application does not sample or defer audit writes."
    ),
}

# ---------------------------------------------------------------------------
# Runtime security operational defaults (documented; Settings remains source)
# ---------------------------------------------------------------------------

RUNTIME_SECURITY_DEFAULTS: Final[dict[str, Any]] = {
    "login_rate_limit_enabled": True,
    "login_max_failed_attempts": 5,
    "login_lockout_seconds": 300,
    # Prefer ASGI peer (Uvicorn ProxyHeaders when FORWARDED_ALLOW_IPS allows).
    # Application-level X-Forwarded-For parsing is opt-in only.
    "trust_forwarded_client_ip": False,
    "forwarded_allow_ips": "127.0.0.1",
}


def retry_after_header_value(details: dict[str, Any] | None) -> str | None:
    """Map ``details.retryAfterSeconds`` → ``Retry-After`` header value.

    Returns ``None`` when the body does not expose a non-negative numeric
    retry hint. Does not mutate ``details``.
    """
    if not details:
        return None
    raw = details.get("retryAfterSeconds")
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return None
    if raw < 0:
        return None
    return str(int(raw))
