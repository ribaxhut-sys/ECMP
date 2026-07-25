"""CAPABILITY-012 Search providers package."""

from app.modules.search.providers.base import SearchProvider
from app.modules.search.providers.complaint import ComplaintSearchProvider

__all__ = ["ComplaintSearchProvider", "SearchProvider"]
