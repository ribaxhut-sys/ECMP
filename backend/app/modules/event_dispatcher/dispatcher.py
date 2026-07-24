"""In-process EventDispatcher (TASK-046).

Delivers events to handlers registered in the same application process.
Not an event bus, broker, queue, or event store.
"""

from __future__ import annotations

from typing import Any

from app.core.logging import get_logger
from app.modules.event_dispatcher.handler import EventHandler
from app.modules.event_dispatcher.result import DispatchResult, HandlerResult

logger = get_logger(__name__)


def _handler_name(handler: EventHandler) -> str:
    return type(handler).__name__


class EventDispatcher:
    """Synchronous in-process event delivery.

    Handlers execute in registration order. Failures are isolated:
    one handler exception does not stop subsequent handlers.
    """

    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []

    def register(self, handler: EventHandler) -> None:
        """Append a handler. Duplicate instances are allowed (caller's choice)."""
        if not isinstance(handler, EventHandler):
            raise TypeError(
                f"handler must be EventHandler, got {type(handler).__name__}"
            )
        self._handlers.append(handler)

    def unregister(self, handler: EventHandler) -> bool:
        """Remove the first matching handler instance. Returns True if removed."""
        try:
            self._handlers.remove(handler)
            return True
        except ValueError:
            return False

    def registered_handlers(self) -> list[EventHandler]:
        """Return a shallow copy of handlers in registration order."""
        return list(self._handlers)

    def dispatch(self, event: Any) -> DispatchResult:
        """Deliver ``event`` synchronously to every registered handler.

        Returns a :class:`DispatchResult` summarizing per-handler outcomes.
        Does not persist, enqueue, or publish outside this process.
        """
        results: list[HandlerResult] = []
        success_count = 0
        failed_count = 0

        for handler in self._handlers:
            name = _handler_name(handler)
            try:
                handler.handle(event)
            except Exception as exc:  # noqa: BLE001 — isolate consumer failures
                failed_count += 1
                results.append(
                    HandlerResult(
                        handler_name=name,
                        success=False,
                        error=str(exc) or repr(exc),
                        exception_type=type(exc).__name__,
                    )
                )
                logger.warning(
                    "Event handler failed during dispatch",
                    extra={
                        "extra_fields": {
                            "handler": name,
                            "exceptionType": type(exc).__name__,
                            "error": str(exc),
                        }
                    },
                )
            else:
                success_count += 1
                results.append(
                    HandlerResult(
                        handler_name=name,
                        success=True,
                    )
                )

        return DispatchResult(
            success_count=success_count,
            failed_count=failed_count,
            handler_results=tuple(results),
        )
