"""Stable 3-letter user initials (stored at registration).

Matches the frontend ``nameInitials`` / ``initialsCandidates`` convention so
lab avatars stay consistent. Allocation is unique across *all* user rows,
including inactive and soft-deleted.
"""

from __future__ import annotations

import string
from collections.abc import Iterable, Iterator


def letters_only(value: str) -> str:
    return "".join(ch for ch in value if ch.isalpha() or ch.isnumeric())


def name_initials(name: str | None) -> str | None:
    value = (name or "").strip()
    if not value:
        return None

    parts = [part for part in value.split() if part]
    code = ""
    if len(parts) >= 3:
        code = f"{parts[0][:1]}{parts[1][:1]}{parts[2][:1]}"
    elif len(parts) == 2:
        first, last = parts[0], parts[1]
        code = (
            f"{first[:1]}{last[:2]}"
            if len(last) >= 2
            else f"{first[:2]}{last[:1]}"
        )
    elif parts:
        code = letters_only(parts[0])

    code = code[:3].upper()
    if len(code) < 3:
        code = letters_only(value)[:3].upper()
    return code or None


def initials_candidates(name: str) -> Iterator[str]:
    natural = name_initials(name)
    if not natural:
        return
    yield natural

    prefix = natural[:2]
    if len(prefix) < 2:
        return

    parts = [part for part in name.strip().split() if part]
    last_word = letters_only(parts[-1] if parts else "").upper()
    for ch in last_word[1:]:
        yield f"{prefix}{ch}"
    for ch in letters_only(name).upper():
        yield f"{prefix}{ch}"
    for ch in string.ascii_uppercase:
        yield f"{prefix}{ch}"


def _alphabet_codes() -> Iterator[str]:
    letters = string.ascii_uppercase
    for a in letters:
        for b in letters:
            for c in letters:
                yield f"{a}{b}{c}"


def allocate_user_initials(
    full_name: str,
    taken: Iterable[str],
    *,
    username: str = "",
) -> str:
    occupied = {code.strip().upper() for code in taken if code and code.strip()}
    for source in (full_name, username):
        for candidate in initials_candidates(source):
            if candidate not in occupied:
                return candidate
    for candidate in _alphabet_codes():
        if candidate not in occupied:
            return candidate
    raise RuntimeError("user initials space exhausted")
