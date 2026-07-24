"""FastAPI dependency injection foundation."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.auth import (
    CurrentPrincipal,
    Principal,
    require_data_scope,
    require_permissions,
    require_roles,
    resolve_effective_scope,
)
from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.dependencies.events import (
    get_dashboard_projection_store,
    get_event_dispatcher,
    get_notification_delivery_store,
    get_notification_intent_store,
    get_notification_store,
)

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSessionDep = Annotated[Session, Depends(get_db_session)]

__all__ = [
    "CurrentPrincipal",
    "DbSessionDep",
    "Principal",
    "SettingsDep",
    "get_dashboard_projection_store",
    "get_db",
    "get_event_dispatcher",
    "get_notification_delivery_store",
    "get_notification_intent_store",
    "get_notification_store",
    "get_settings_dep",
    "require_data_scope",
    "require_permissions",
    "require_roles",
    "resolve_effective_scope",
]


def get_settings_dep() -> Settings:
    """Explicit settings dependency (alias for clarity in routers)."""
    return get_settings()


def get_db() -> Generator[Session, None, None]:
    """Explicit DB session dependency (alias for clarity in routers)."""
    yield from get_db_session()
