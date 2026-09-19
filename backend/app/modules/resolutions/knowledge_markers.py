"""Parses ``@[title](knowledge:<uuid>)`` reference markers embedded in
``ComplaintResolution.resolution_notes`` (Knowledge Reference on
Penyelesaian).

This belongs to the Resolution domain, not Knowledge — it is Resolution's
own interpretation of text it stores; the Knowledge module is untouched.
The marker's ``title`` is a display snapshot only (stability, LOCKED — a
reference never re-resolves by title); the ``knowledge_id`` is the sole
identifier consulted for validation and navigation.
"""

from __future__ import annotations

import re
import uuid

_MARKER_RE = re.compile(r"@\[[^\]\n]*\]\(knowledge:([0-9a-fA-F-]{36})\)")


def extract_knowledge_ids(text: str | None) -> list[uuid.UUID]:
    """Ordered, de-duplicated Knowledge ids referenced in ``text``.

    Malformed or unparsable markers are silently skipped — a broken marker
    degrades to plain text rather than failing the whole resolution.
    """
    seen: set[uuid.UUID] = set()
    ordered: list[uuid.UUID] = []
    for match in _MARKER_RE.finditer(text or ""):
        try:
            parsed = uuid.UUID(match.group(1))
        except ValueError:
            continue
        if parsed not in seen:
            seen.add(parsed)
            ordered.append(parsed)
    return ordered
