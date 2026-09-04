"""Mode A adapter — resolves actor ids against the local user table."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


class LocalUserDirectory:
    def __init__(self, session: Session) -> None:
        self._session = session

    def display_names(self, user_ids: set[str]) -> dict[str, str]:
        wanted: dict[uuid.UUID, str] = {}
        for raw in user_ids:
            try:
                wanted[uuid.UUID(str(raw))] = str(raw)
            except (TypeError, ValueError):
                continue  # non-UUID actor keys (system, jobs) have no directory entry
        if not wanted:
            return {}
        rows = self._session.scalars(
            select(User).where(
                User.id.in_(wanted.keys()), User.deleted_at.is_(None)
            )
        ).all()
        out: dict[str, str] = {}
        for row in rows:
            name = (row.full_name or "").strip() or (row.username or "").strip()
            if name:
                out[wanted[row.id]] = name
        return out
