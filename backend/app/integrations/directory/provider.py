"""User directory port — read-only (ADR-015; identity is Enterprise-owned).

Business services depend only on ``UserDirectory``. Mode A resolves against the
local user table; Mode B swaps the adapter for the platform directory without
touching the Complaint domain.
"""

from __future__ import annotations

from typing import Protocol


class UserDirectory(Protocol):
    def display_names(self, user_ids: set[str]) -> dict[str, str]:
        """Map actor id → operator-facing name. Unknown ids are omitted."""
        ...
