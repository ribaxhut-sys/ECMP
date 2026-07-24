"""Dependency injection wiring for Complaint application (CAPABILITY-004)."""

from __future__ import annotations

from functools import lru_cache

from app.modules.complaint.application.services.domain_service import (
    ComplaintDomainService,
)


@lru_cache(maxsize=1)
def get_complaint_domain_service() -> ComplaintDomainService:
    """DI factory — shared ComplaintDomainService instance."""
    return ComplaintDomainService()


__all__ = ["get_complaint_domain_service"]
