"""In-memory Queue application state (TASK-062).

Foundation workspace only — NOT a repository, NOT persistence, NOT SQLAlchemy.
Injected via DI for CQRS handlers during the application-foundation milestone.
"""

from __future__ import annotations

import uuid
from dataclasses import replace

from app.modules.queue.models import Queue, QueueCounter, QueueTicket


class InMemoryQueueState:
    """Process-local Queue BC state. No DB. No shared mutable ticket fields."""

    def __init__(self) -> None:
        self._queues: dict[uuid.UUID, Queue] = {}
        self._tickets: dict[uuid.UUID, QueueTicket] = {}
        self._tickets_by_queue: dict[uuid.UUID, list[uuid.UUID]] = {}
        self._counters_by_queue: dict[uuid.UUID, list[uuid.UUID]] = {}
        self._counters: dict[uuid.UUID, QueueCounter] = {}
        self._ticket_seq: dict[uuid.UUID, int] = {}

    def clear(self) -> None:
        self._queues.clear()
        self._tickets.clear()
        self._tickets_by_queue.clear()
        self._counters_by_queue.clear()
        self._counters.clear()
        self._ticket_seq.clear()

    # --- queues ---

    def put_queue(self, queue: Queue) -> None:
        self._queues[queue.queue_id] = queue
        self._tickets_by_queue.setdefault(queue.queue_id, [])
        self._counters_by_queue.setdefault(queue.queue_id, [])
        self._ticket_seq.setdefault(queue.queue_id, 0)

    def get_queue(self, queue_id: uuid.UUID) -> Queue | None:
        return self._queues.get(queue_id)

    def replace_queue(self, queue: Queue) -> None:
        if queue.queue_id not in self._queues:
            raise KeyError(f"queue not found: {queue.queue_id}")
        self._queues[queue.queue_id] = queue

    # --- tickets ---

    def next_sequence(self, queue_id: uuid.UUID) -> int:
        current = self._ticket_seq.get(queue_id, 0) + 1
        self._ticket_seq[queue_id] = current
        return current

    def put_ticket(self, ticket: QueueTicket) -> None:
        if ticket.ticket_id in self._tickets:
            raise KeyError(f"ticket already exists: {ticket.ticket_id}")
        self._tickets[ticket.ticket_id] = ticket
        self._tickets_by_queue.setdefault(ticket.queue_id, []).append(ticket.ticket_id)

    def get_ticket(self, ticket_id: uuid.UUID) -> QueueTicket | None:
        return self._tickets.get(ticket_id)

    def replace_ticket(self, ticket: QueueTicket) -> None:
        existing = self._tickets.get(ticket.ticket_id)
        if existing is None:
            raise KeyError(f"ticket not found: {ticket.ticket_id}")
        # Replace whole immutable VO — never mutate fields in place.
        self._tickets[ticket.ticket_id] = ticket

    def list_tickets(self, queue_id: uuid.UUID) -> tuple[QueueTicket, ...]:
        ids = self._tickets_by_queue.get(queue_id, [])
        return tuple(self._tickets[tid] for tid in ids if tid in self._tickets)

    def ticket_numbers(self, queue_id: uuid.UUID) -> frozenset[str]:
        return frozenset(t.ticket_number for t in self.list_tickets(queue_id))

    # --- counters (DTO support; no create command in TASK-062) ---

    def put_counter(self, queue_id: uuid.UUID, counter: QueueCounter) -> None:
        self._counters[counter.counter_id] = counter
        self._counters_by_queue.setdefault(queue_id, []).append(counter.counter_id)

    def list_counters(self, queue_id: uuid.UUID) -> tuple[QueueCounter, ...]:
        ids = self._counters_by_queue.get(queue_id, [])
        return tuple(self._counters[cid] for cid in ids if cid in self._counters)

    def with_queue_status(self, queue: Queue, status) -> Queue:
        return replace(queue, status=status)


__all__ = ["InMemoryQueueState"]
