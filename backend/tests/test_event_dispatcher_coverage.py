"""Force EventDispatcher composition so CI coverage includes the wiring module."""

from __future__ import annotations

from app.dependencies.events import (
    get_delivery_engine,
    get_event_dispatcher,
    get_execution_dispatcher,
    get_execution_engine,
    get_execution_runtime,
    get_provider_executor,
    get_transport_selector,
    reset_event_runtime_for_tests,
)


def test_event_dispatcher_wires_consumers_after_reset() -> None:
    reset_event_runtime_for_tests()
    dispatcher = get_event_dispatcher()
    assert dispatcher is get_event_dispatcher()
    assert get_execution_runtime() is not None
    assert get_execution_engine() is not None
    assert get_execution_dispatcher() is not None
    assert get_delivery_engine() is not None
    assert get_transport_selector() is not None
    assert get_provider_executor() is not None
    reset_event_runtime_for_tests()
