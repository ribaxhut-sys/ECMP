"""In-process Event Dispatcher — public exports (TASK-046).

Not a bus / broker / queue / event store. Same-process delivery only.
"""

from app.modules.event_dispatcher.dispatcher import EventDispatcher
from app.modules.event_dispatcher.handler import EventHandler
from app.modules.event_dispatcher.result import DispatchResult, HandlerResult

__all__ = [
    "DispatchResult",
    "EventDispatcher",
    "EventHandler",
    "HandlerResult",
]
