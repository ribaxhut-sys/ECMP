"""Unique user initials assigned at registration."""

from __future__ import annotations

from app.modules.users.initials import allocate_user_initials, name_initials


def test_name_initials_matches_frontend_rules() -> None:
    assert name_initials("Budi Santoso Pratama") == "BSP"
    assert name_initials("Budi Santoso") == "BSA"
    assert name_initials("Andi Wijaya") == "AWI"
    assert name_initials("Ali B") == "ALB"
    assert name_initials("Elena") == "ELE"
    assert name_initials("  Budi   Santoso  ") == "BSA"
    assert name_initials("") is None


def test_allocate_keeps_natural_code_when_free() -> None:
    assert allocate_user_initials("Budi Santoso", []) == "BSA"


def test_allocate_skips_taken_including_inactive_codes() -> None:
    # Inactive user A still occupies BSA — user B must not reuse it.
    code = allocate_user_initials("Budi Santoso", {"BSA"})
    assert code == "BSN"
    assert code != "BSA"


def test_two_identical_names_get_distinct_codes() -> None:
    first = allocate_user_initials("Budi Santoso", [])
    second = allocate_user_initials("Budi Santoso", {first})
    assert first == "BSA"
    assert second == "BSN"
