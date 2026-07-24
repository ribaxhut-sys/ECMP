"""Queue CQRS commands (TASK-062 / CAPABILITY-003)."""

from app.modules.queue.application.commands.call_next_ticket import (
    CallNextTicketCommand,
    CallNextTicketHandler,
)
from app.modules.queue.application.commands.cancel_ticket import (
    CancelTicketCommand,
    CancelTicketHandler,
)
from app.modules.queue.application.commands.close_queue import (
    CloseQueueCommand,
    CloseQueueHandler,
)
from app.modules.queue.application.commands.complete_ticket import (
    CompleteTicketCommand,
    CompleteTicketHandler,
)
from app.modules.queue.application.commands.create_queue import (
    CreateQueueCommand,
    CreateQueueHandler,
)
from app.modules.queue.application.commands.issue_ticket import (
    IssueTicketCommand,
    IssueTicketHandler,
)
from app.modules.queue.application.commands.open_queue import (
    OpenQueueCommand,
    OpenQueueHandler,
)
from app.modules.queue.application.commands.pause_queue import (
    PauseQueueCommand,
    PauseQueueHandler,
)
from app.modules.queue.application.commands.recall_ticket import (
    RecallTicketCommand,
    RecallTicketHandler,
)
from app.modules.queue.application.commands.skip_ticket import (
    SkipTicketCommand,
    SkipTicketHandler,
)

__all__ = [
    "CallNextTicketCommand",
    "CallNextTicketHandler",
    "CancelTicketCommand",
    "CancelTicketHandler",
    "CloseQueueCommand",
    "CloseQueueHandler",
    "CompleteTicketCommand",
    "CompleteTicketHandler",
    "CreateQueueCommand",
    "CreateQueueHandler",
    "IssueTicketCommand",
    "IssueTicketHandler",
    "OpenQueueCommand",
    "OpenQueueHandler",
    "PauseQueueCommand",
    "PauseQueueHandler",
    "RecallTicketCommand",
    "RecallTicketHandler",
    "SkipTicketCommand",
    "SkipTicketHandler",
]
