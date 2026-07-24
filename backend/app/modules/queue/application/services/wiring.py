"""Dependency injection wiring for Queue application (TASK-062)."""

from __future__ import annotations

from functools import lru_cache

from app.modules.queue.application.services.domain_service import QueueDomainService
from app.modules.queue.application.services.state import InMemoryQueueState


@lru_cache(maxsize=1)
def get_queue_domain_service() -> QueueDomainService:
    """DI factory — shared QueueDomainService instance."""
    return QueueDomainService()


@lru_cache(maxsize=1)
def get_queue_state() -> InMemoryQueueState:
    """DI factory — process-local foundation state (not a repository)."""
    return InMemoryQueueState()


__all__ = [
    "get_queue_domain_service",
    "get_queue_state",
]
