"""Queue Domain — operations rules and pluggable policies (CAPABILITY-003).

Persistence-independent. No FastAPI. No ORM. No repository I/O.
"""

from app.modules.queue.domain.ticket_number import (
    PrefixSequenceTicketNumberGenerator,
    TicketNumberGenerator,
)

__all__ = [
    "PrefixSequenceTicketNumberGenerator",
    "TicketNumberGenerator",
]
