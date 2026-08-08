"""No-op directory — used when no identity source is wired (tests, stub runs)."""

from __future__ import annotations


class NullUserDirectory:
    def display_names(self, user_ids: set[str]) -> dict[str, str]:
        return {}
