"""IdP role → Core Platform role-code mapping (TASK-PLATFORM-SECMIG-P2-001).

IdP role names are not assumed equal to database ``roles.code`` values.
"""

from __future__ import annotations

from collections.abc import Mapping

# Phase 1 Keycloak realm roles → foundation IAM role codes (0020/0025).
_DEFAULT_IDP_TO_INTERNAL: dict[str, str] = {
    "cs_agent": "AGENT",
    "viewer": "VIEWER",
    "supervisor": "SUPERVISOR",
    "handler": "HANDLER",
}

# Internal codes accepted as already-canonical (pass-through).
_INTERNAL_CODES: frozenset[str] = frozenset(
    {
        "SUPER_ADMIN",
        "ADMIN",
        "ADMINISTRATOR",
        "SUPERVISOR",
        "AGENT",
        "HANDLER",
        "VIEWER",
    }
)


class RoleMapper:
    """Map IdP ``roles[]`` claim values to Core Platform role codes."""

    def __init__(self, mapping: Mapping[str, str] | None = None) -> None:
        base = dict(_DEFAULT_IDP_TO_INTERNAL)
        if mapping:
            for key, value in mapping.items():
                if key is None or value is None:
                    continue
                cleaned_key = str(key).strip()
                cleaned_value = str(value).strip()
                if cleaned_key and cleaned_value:
                    base[cleaned_key.lower()] = cleaned_value.upper()
        self._map = base

    def map_one(self, idp_role: str) -> str | None:
        """Return internal role code or ``None`` when unmapped (ignored)."""
        raw = (idp_role or "").strip()
        if not raw:
            return None
        upper = raw.upper()
        if upper in _INTERNAL_CODES:
            return upper
        return self._map.get(raw.lower())

    def map_many(self, idp_roles: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
        """Map IdP roles; preserve order; drop unknowns; de-duplicate."""
        if not idp_roles:
            return ()
        seen: set[str] = set()
        result: list[str] = []
        for role in idp_roles:
            mapped = self.map_one(str(role) if role is not None else "")
            if mapped is None or mapped in seen:
                continue
            seen.add(mapped)
            result.append(mapped)
        return tuple(result)
