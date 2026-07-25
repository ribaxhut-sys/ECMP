"""Wire SearchService dependencies (CAPABILITY-012)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.modules.search.providers.complaint import ComplaintSearchProvider
from app.modules.search.service import SearchService


def build_search_service(session: Session) -> SearchService:
    return SearchService(ComplaintSearchProvider(session))
