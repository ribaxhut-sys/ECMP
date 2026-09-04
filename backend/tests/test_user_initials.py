"""Unique user initials assigned at registration."""

from __future__ import annotations

import string

import pytest

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


def test_name_initials_ignores_punctuation_only() -> None:
    assert name_initials("...") is None
    assert name_initials("Li X") == "LIX"


def test_allocate_uses_username_then_alphabet_when_name_has_no_letters() -> None:
    assert allocate_user_initials("...", [], username="andi") == "AND"
    assert allocate_user_initials("...", []) == "AAA"


def test_allocate_raises_when_letter_space_is_exhausted() -> None:
    taken = {
        f"{a}{b}{c}"
        for a in string.ascii_uppercase
        for b in string.ascii_uppercase
        for c in string.ascii_uppercase
    }
    with pytest.raises(RuntimeError, match="exhausted"):
        allocate_user_initials("Budi Santoso", taken)
