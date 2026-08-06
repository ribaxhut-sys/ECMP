"""Customer search key length rules (FR-002 anti-enumeration hygiene).

Shared contract for FE/BE Mode A lab:
- Name (has letters): min 3 characters
- Phone-like digits (0… / 62…): min 10 digits
- Other numeric ID: min 8 digits
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

KeyKind = Literal["name", "phone", "id"]

MIN_NAME_CHARS = 3
MIN_ID_DIGITS = 8
MIN_PHONE_DIGITS = 10

_DIGIT_RE = re.compile(r"\D+")
_LETTER_RE = re.compile(r"[A-Za-zÀ-ÿ]")


@dataclass(frozen=True)
class SearchKeyValidation:
    ok: bool
    kind: KeyKind | None = None
    digit_count: int = 0
    error_code: str | None = None


def digits_only(value: str) -> str:
    return _DIGIT_RE.sub("", value or "")


def classify_search_key(raw: str) -> KeyKind:
    """Classify operator input for length policy."""
    q = (raw or "").strip()
    digits = digits_only(q)
    has_letter = bool(_LETTER_RE.search(q))
    compact = re.sub(r"\s+", "", q)

    # Mostly numeric → ID or phone (ignore separators)
    if digits and (not has_letter or len(digits) >= max(1, int(len(compact) * 0.7))):
        if digits.startswith("0") or digits.startswith("62"):
            return "phone"
        return "id"
    return "name"


def validate_customer_search_key(raw: str) -> SearchKeyValidation:
    q = (raw or "").strip()
    if not q:
        return SearchKeyValidation(ok=False, error_code="customer.search_key_empty")

    kind = classify_search_key(q)
    digits = digits_only(q)

    if kind == "name":
        if len(q) < MIN_NAME_CHARS:
            return SearchKeyValidation(
                ok=False, kind=kind, digit_count=len(digits), error_code="customer.search_name_too_short"
            )
        return SearchKeyValidation(ok=True, kind=kind, digit_count=len(digits))

    if kind == "phone":
        if len(digits) < MIN_PHONE_DIGITS:
            return SearchKeyValidation(
                ok=False,
                kind=kind,
                digit_count=len(digits),
                error_code="customer.search_phone_too_short",
            )
        return SearchKeyValidation(ok=True, kind=kind, digit_count=len(digits))

    # id
    if len(digits) < MIN_ID_DIGITS:
        return SearchKeyValidation(
            ok=False, kind=kind, digit_count=len(digits), error_code="customer.search_id_too_short"
        )
    return SearchKeyValidation(ok=True, kind=kind, digit_count=len(digits))
