"""FastAPI dependency injection foundation."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.auth import CurrentPrincipal, Principal, require_permissions, require_roles
from app.core.config import Settings, get_settings
from app.db.session import get_db_session

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSessionDep = Annotated[Session, Depends(get_db_session)]

__all__ = [
    "CurrentPrincipal",
    "DbSessionDep",
    "Principal",
    "SettingsDep",
    "get_db",
    "get_settings_dep",
    "require_permissions",
    "require_roles",
]


def get_settings_dep() -> Settings:
    """Explicit settings dependency (alias for clarity in routers)."""
    return get_settings()


def get_db() -> Generator[Session, None, None]:
    """Explicit DB session dependency (alias for clarity in routers)."""
    yield from get_db_session()
