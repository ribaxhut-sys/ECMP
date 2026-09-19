"""Keyword match against the local customer cache (ADR-002 — not Customer SoR)."""

from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Customer

_CUSTOMER_NAME_KEY_CAP = 500


def ilike_contains_pattern(keyword: str) -> str:
    escaped = (
        (keyword or "")
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{escaped}%"


def customer_ids_for_keyword(session: Session, keyword: str) -> list[str]:
    """Cache UUID and external id whose name or external id contains ``keyword``.

    Used by Aggregate list (API-514) and Case list (API-536) so WP name search
    does not invent a Customer Master query. Capped so a short token cannot
    expand into an unbounded IN clause.
    """
    kw = (keyword or "").strip()[:200]
    if not kw:
        return []
    pattern = ilike_contains_pattern(kw)
    rows = session.execute(
        select(Customer.id, Customer.external_customer_id)
        .where(
            Customer.deleted_at.is_(None),
            or_(
                Customer.full_name.ilike(pattern, escape="\\"),
                Customer.external_customer_id.ilike(pattern, escape="\\"),
            ),
        )
        .limit(_CUSTOMER_NAME_KEY_CAP)
    ).all()
    keys: list[str] = []
    seen: set[str] = set()
    for cid, external_id in rows:
        for raw in (str(cid) if cid is not None else "", (external_id or "").strip()):
            if raw and raw not in seen:
                seen.add(raw)
                keys.append(raw)
    return keys
