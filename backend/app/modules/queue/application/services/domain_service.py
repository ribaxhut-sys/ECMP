"""QueueDomainService — pure domain rules (TASK-062 / CAPABILITY-003).

No database. No repository. No infrastructure I/O.
Lifecycle validation and ticket-number policy live here — not in controllers.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from app.modules.queue.application.services.errors import QueueApplicationError
from app.modules.queue.domain.ticket_number import (
    PrefixSequenceTicketNumberGenerator,
    TicketNumberGenerator,
)
from app.modules.queue.models import (
    Queue,
    QueuePolicy,
    QueuePriority,
    QueueStatus,
    QueueTicket,
    QueueTicketStatus,
)
from app.core.user_messages import m

_PRIORITY_RANK: dict[QueuePriority, int] = {
    QueuePriority.VIP: 0,
    QueuePriority.PRIORITY: 1,
    QueuePriority.NORMAL: 2,
}

_TERMINAL_TICKET = frozenset(
    {
        QueueTicketStatus.COMPLETED,
        QueueTicketStatus.CANCELLED,
        QueueTicketStatus.SKIPPED,
    }
)

_RECALLABLE = frozenset(
    {
        QueueTicketStatus.CALLED,
        QueueTicketStatus.SERVING,
    }
)


class QueueDomainService:
    """Domain service for queue / ticket business rules."""

    def __init__(
        self,
        ticket_number_generator: TicketNumberGenerator | None = None,
    ) -> None:
        self._ticket_numbers: TicketNumberGenerator = (
            ticket_number_generator
            if ticket_number_generator is not None
            else PrefixSequenceTicketNumberGenerator(prefix="A", width=3)
        )

    def generate_ticket_number(self, sequence: int) -> str:
        """Generate a display ticket number via the injected generator (default A001)."""
        try:
            return self._ticket_numbers.generate(sequence)
        except ValueError as exc:
            raise QueueApplicationError(
                "INVALID_TICKET_SEQUENCE",
                str(exc),
            ) from exc
    def validate_queue_status(
        self,
        queue: Queue,
        *,
        allow: frozenset[QueueStatus] | set[QueueStatus],
        action: str,
    ) -> None:
        """Ensure queue operational status permits the action."""
        if queue.status not in allow:
            raise QueueApplicationError(
                "INVALID_QUEUE_STATUS",
                f"status antrian {queue.status.value} tidak mengizinkan {action}",
            )

    def validate_queue_policy(self, policy: QueuePolicy) -> None:
        """Ensure policy is one of the supported foundation policies."""
        if not isinstance(policy, QueuePolicy):
            raise QueueApplicationError(
                "INVALID_QUEUE_POLICY",
                f"kebijakan antrian tidak didukung: {policy!r}",
            )
        if policy not in (QueuePolicy.FIFO, QueuePolicy.PRIORITY_QUEUE):
            raise QueueApplicationError(
                "INVALID_QUEUE_POLICY",
                f"kebijakan antrian tidak didukung: {policy!r}",
            )

    def validate_can_issue_ticket(self, queue: Queue) -> None:
        """Queue must be OPEN; CLOSED rejects new tickets."""
        if queue.status is QueueStatus.CLOSED:
            raise QueueApplicationError(
                "QUEUE_CLOSED",
                m("queue.closed_new_tickets_rejected"),
            )
        if queue.status is QueueStatus.PAUSED:
            raise QueueApplicationError(
                "QUEUE_PAUSED",
                m("queue.paused_new_tickets_rejected"),
            )
        self.validate_queue_status(
            queue, allow={QueueStatus.OPEN}, action="issue ticket"
        )

    def validate_can_call(self, queue: Queue) -> None:
        """Queue PAUSED / CLOSED rejects calling."""
        if queue.status is QueueStatus.PAUSED:
            raise QueueApplicationError(
                "QUEUE_PAUSED",
                m("queue.paused_calling_rejected"),
            )
        if queue.status is QueueStatus.CLOSED:
            raise QueueApplicationError(
                "QUEUE_CLOSED",
                m("queue.closed_calling_rejected"),
            )
        self.validate_queue_status(
            queue, allow={QueueStatus.OPEN}, action="call next ticket"
        )

    def validate_no_duplicate_ticket_number(
        self,
        ticket_number: str,
        existing_numbers: frozenset[str] | set[str],
    ) -> None:
        if ticket_number in existing_numbers:
            raise QueueApplicationError(
                "DUPLICATE_TICKET_NUMBER",
                f"nomor tiket {ticket_number!r} sudah ada di antrian ini",
            )

    def validate_priority(self, priority: QueuePriority) -> None:
        if not isinstance(priority, QueuePriority):
            raise QueueApplicationError(
                "INVALID_PRIORITY",
                f"prioritas tidak didukung: {priority!r}",
            )

    def validate_priority_rules(
        self,
        policy: QueuePolicy,
        priority: QueuePriority,
    ) -> None:
        """Priority enum always valid; policy governs selection only."""
        self.validate_queue_policy(policy)
        self.validate_priority(priority)

    def select_next_ticket(
        self,
        queue: Queue,
        tickets: tuple[QueueTicket, ...] | list[QueueTicket],
    ) -> QueueTicket | None:
        """Select next WAITING ticket by FIFO or PRIORITY_QUEUE policy."""
        self.validate_queue_policy(queue.policy)
        waiting = [t for t in tickets if t.status is QueueTicketStatus.WAITING]
        if not waiting:
            return None
        if queue.policy is QueuePolicy.FIFO:
            waiting.sort(key=lambda t: t.created_at)
            return waiting[0]
        # PRIORITY_QUEUE: VIP → PRIORITY → NORMAL, then FIFO within rank
        waiting.sort(
            key=lambda t: (_PRIORITY_RANK[t.priority], t.created_at)
        )
        return waiting[0]

    def assert_ticket_callable(self, ticket: QueueTicket) -> None:
        if ticket.status is QueueTicketStatus.CANCELLED:
            raise QueueApplicationError(
                "TICKET_CANCELLED",
                m("queue.cancelled_cannot_be_called"),
            )
        if ticket.status is QueueTicketStatus.COMPLETED:
            raise QueueApplicationError(
                "TICKET_COMPLETED",
                m("queue.completed_cannot_be_called"),
            )
        if ticket.status is QueueTicketStatus.SKIPPED:
            raise QueueApplicationError(
                "TICKET_SKIPPED",
                m("queue.skipped_cannot_be_called"),
            )
        if ticket.status is not QueueTicketStatus.WAITING:
            raise QueueApplicationError(
                "INVALID_TICKET_STATUS",
                f"status tiket {ticket.status.value} tidak dapat dipanggil",
            )

    def assert_not_return_to_waiting(self, ticket: QueueTicket) -> None:
        if ticket.status is QueueTicketStatus.COMPLETED:
            raise QueueApplicationError(
                "TICKET_COMPLETED",
                m("queue.completed_cannot_return_waiting"),
            )
        if ticket.status in _TERMINAL_TICKET:
            raise QueueApplicationError(
                "INVALID_TICKET_TRANSITION",
                f"status tiket {ticket.status.value} tidak dapat kembali ke WAITING",
            )

    def recall_ticket(self, ticket: QueueTicket) -> QueueTicket:
        """Re-announce a CALLED / SERVING ticket. Status unchanged (no Voice/Display)."""
        if ticket.status not in _RECALLABLE:
            raise QueueApplicationError(
                "INVALID_TICKET_TRANSITION",
                f"tidak dapat recall tiket berstatus {ticket.status.value}",
            )
        return ticket

    def transition_ticket(
        self,
        ticket: QueueTicket,
        new_status: QueueTicketStatus,
        *,
        now: datetime | None = None,
    ) -> QueueTicket:
        """Return a new immutable ticket with updated status (replace, not mutate)."""
        if new_status is QueueTicketStatus.WAITING:
            self.assert_not_return_to_waiting(ticket)
            raise QueueApplicationError(
                "INVALID_TICKET_TRANSITION",
                m("queue.tickets_issued_waiting_no_reentry"),
            )
        if new_status is QueueTicketStatus.CALLED:
            self.assert_ticket_callable(ticket)
        elif new_status is QueueTicketStatus.SERVING:
            if ticket.status is not QueueTicketStatus.CALLED:
                raise QueueApplicationError(
                    "INVALID_TICKET_TRANSITION",
                    f"tidak dapat memindahkan tiket ke SERVING dari {ticket.status.value}",
                )
        elif new_status is QueueTicketStatus.COMPLETED:
            if ticket.status not in (
                QueueTicketStatus.CALLED,
                QueueTicketStatus.SERVING,
            ):
                raise QueueApplicationError(
                    "INVALID_TICKET_TRANSITION",
                    f"tidak dapat menyelesaikan tiket berstatus {ticket.status.value}",
                )
        elif new_status is QueueTicketStatus.CANCELLED:
            if ticket.status is QueueTicketStatus.COMPLETED:
                raise QueueApplicationError(
                    "INVALID_TICKET_TRANSITION",
                    m("queue.completed_cannot_be_cancelled"),
                )
            if ticket.status in (
                QueueTicketStatus.CANCELLED,
                QueueTicketStatus.SKIPPED,
            ):
                raise QueueApplicationError(
                    "INVALID_TICKET_TRANSITION",
                    f"tiket sudah berstatus {ticket.status.value}",
                )
            if ticket.status not in (
                QueueTicketStatus.WAITING,
                QueueTicketStatus.CALLED,
                QueueTicketStatus.SERVING,
            ):
                raise QueueApplicationError(
                    "INVALID_TICKET_TRANSITION",
                    f"tidak dapat membatalkan tiket berstatus {ticket.status.value}",
                )
        elif new_status is QueueTicketStatus.SKIPPED:
            if ticket.status not in (
                QueueTicketStatus.WAITING,
                QueueTicketStatus.CALLED,
            ):
                raise QueueApplicationError(
                    "INVALID_TICKET_TRANSITION",
                    f"tidak dapat melewati tiket berstatus {ticket.status.value}",
                )
        else:
            raise QueueApplicationError(
                "INVALID_TICKET_STATUS",
                f"status tiket tidak dikenal: {new_status!r}",
            )
        _ = now or datetime.now(timezone.utc)
        return replace(ticket, status=new_status)

    def with_queue_status(self, queue: Queue, status: QueueStatus) -> Queue:
        if not isinstance(status, QueueStatus):
            raise QueueApplicationError(
                "INVALID_QUEUE_STATUS",
                f"status antrian tidak valid: {status!r}",
            )
        return replace(queue, status=status)


__all__ = ["QueueDomainService"]
