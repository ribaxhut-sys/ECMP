"""System Settings persistence (TASK-028)."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import SettingVisibility
from app.modules.settings.models import Setting


class SettingsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def get_by_key(self, key: str) -> Setting | None:
        stmt = select(Setting).where(Setting.key == key)
        return self._session.scalar(stmt)

    def list_all(self) -> list[Setting]:
        stmt = select(Setting).order_by(Setting.category, Setting.key)
        return list(self._session.scalars(stmt).all())

    def list_public(self) -> list[Setting]:
        stmt = (
            select(Setting)
            .where(Setting.visibility == SettingVisibility.PUBLIC)
            .order_by(Setting.category, Setting.key)
        )
        return list(self._session.scalars(stmt).all())

    def update_value(self, row: Setting, *, value: str) -> Setting:
        row.value = value
        row.updated_at = datetime.now(UTC)
        self._session.add(row)
        self._session.flush()
        return row

    def commit(self) -> None:
        self._session.commit()
