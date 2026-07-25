"""Process-wide EventDispatcher composition (TASK-047…059).



Wires Notification + Dashboard + KPI + Workflow (+ Execution Plan producer)

without ComplaintService knowing about consumers.



ExecutionRuntime / ExecutionRunStore / ExecutionEngine / ExecutionDispatcher /

DeliveryEngine / TransportRegistry / TransportSelector / ProviderExecutor

are available via DI; runtime, engine, dispatcher, delivery, transport

selection, and provider-execution prepare are not auto-invoked from the

event path (TASK-054…059: prepare + transition + dispatch + delivery

planning + transport selection + provider execution contract only;

no handler execution / no send / no providers).

"""



from __future__ import annotations



from app.modules.dashboard.projection_registration import (

    register_dashboard_projection_handler,

)

from app.modules.dashboard.projection_store import DashboardProjectionStore

from app.modules.delivery.engine import DeliveryEngine

from app.modules.event_dispatcher import EventDispatcher

from app.modules.transport.registry import TransportRegistry

from app.modules.transport.selector import TransportSelector

from app.modules.provider_executor.executor import ProviderExecutor

from app.modules.execution.dispatcher import ExecutionDispatcher
from app.modules.execution.engine import ExecutionEngine

from app.modules.execution.planner import ExecutionPlanner

from app.modules.execution.registry import ExecutionRegistry

from app.modules.execution.run_store import ExecutionRunStore

from app.modules.execution.runtime import ExecutionRuntime

from app.modules.execution.store import ExecutionPlanStore

from app.modules.execution.workflow_producer import WorkflowExecutionProducer

from app.modules.kpi.projection_registration import register_kpi_projection_handler

from app.modules.kpi.projection_store import KpiProjectionStore

from app.modules.notification.delivery_memory import InMemoryNotificationDeliveryStore

from app.modules.notification.intent_memory import InMemoryNotificationIntentStore

from app.modules.notification.memory import InMemoryNotificationStore

from app.modules.notification.registration import register_notification_handler

from app.modules.timeline.registration import register_timeline_handler

from app.modules.workflow.registration import register_workflow_handler

from app.modules.workflow.registry import WorkflowRegistry

from app.modules.workflow.store import WorkflowInstanceStore



_dispatcher: EventDispatcher | None = None

_notification_store: InMemoryNotificationStore | None = None

_intent_store: InMemoryNotificationIntentStore | None = None

_delivery_store: InMemoryNotificationDeliveryStore | None = None

_dashboard_projection_store: DashboardProjectionStore | None = None

_kpi_projection_store: KpiProjectionStore | None = None

_workflow_registry: WorkflowRegistry | None = None

_workflow_instance_store: WorkflowInstanceStore | None = None

_execution_plan_store: ExecutionPlanStore | None = None

_execution_registry: ExecutionRegistry | None = None

_execution_planner: ExecutionPlanner | None = None

_workflow_execution_producer: WorkflowExecutionProducer | None = None

_execution_run_store: ExecutionRunStore | None = None

_execution_runtime: ExecutionRuntime | None = None

_execution_engine: ExecutionEngine | None = None
_execution_dispatcher: ExecutionDispatcher | None = None
_delivery_engine: DeliveryEngine | None = None
_transport_registry: TransportRegistry | None = None
_transport_selector: TransportSelector | None = None
_provider_executor: ProviderExecutor | None = None





def get_notification_store() -> InMemoryNotificationStore:

    """Shared in-memory notification buffer for diagnostics/testing."""

    global _notification_store

    if _notification_store is None:

        _notification_store = InMemoryNotificationStore()

    return _notification_store





def get_notification_intent_store() -> InMemoryNotificationIntentStore:

    """Shared in-memory notification intent buffer for diagnostics/testing."""

    global _intent_store

    if _intent_store is None:

        _intent_store = InMemoryNotificationIntentStore()

    return _intent_store





def get_notification_delivery_store() -> InMemoryNotificationDeliveryStore:

    """Shared in-memory delivery-plan buffer for diagnostics/testing."""

    global _delivery_store

    if _delivery_store is None:

        _delivery_store = InMemoryNotificationDeliveryStore()

    return _delivery_store





def get_dashboard_projection_store() -> DashboardProjectionStore:

    """Shared in-memory dashboard projection for diagnostics/testing."""

    global _dashboard_projection_store

    if _dashboard_projection_store is None:

        _dashboard_projection_store = DashboardProjectionStore()

    return _dashboard_projection_store





def get_kpi_projection_store() -> KpiProjectionStore:

    """Shared in-memory KPI projection for diagnostics/testing."""

    global _kpi_projection_store

    if _kpi_projection_store is None:

        _kpi_projection_store = KpiProjectionStore()

    return _kpi_projection_store





def get_workflow_registry() -> WorkflowRegistry:

    """Shared in-memory workflow definition registry for diagnostics/testing."""

    global _workflow_registry

    if _workflow_registry is None:

        _workflow_registry = WorkflowRegistry()

    return _workflow_registry





def get_workflow_instance_store() -> WorkflowInstanceStore:

    """Shared in-memory workflow instance buffer for diagnostics/testing."""

    global _workflow_instance_store

    if _workflow_instance_store is None:

        _workflow_instance_store = WorkflowInstanceStore()

    return _workflow_instance_store





def get_execution_plan_store() -> ExecutionPlanStore:

    """Shared in-memory execution plan buffer for diagnostics/testing."""

    global _execution_plan_store

    if _execution_plan_store is None:

        _execution_plan_store = ExecutionPlanStore()

    return _execution_plan_store





def get_execution_registry() -> ExecutionRegistry:

    """Shared in-memory execution task-handler catalog (never invoked)."""

    global _execution_registry

    if _execution_registry is None:

        _execution_registry = ExecutionRegistry()

    return _execution_registry





def get_execution_planner() -> ExecutionPlanner:

    """Shared ExecutionPlanner instance."""

    global _execution_planner

    if _execution_planner is None:

        _execution_planner = ExecutionPlanner()

    return _execution_planner





def get_workflow_execution_producer() -> WorkflowExecutionProducer:

    """Workflow → ExecutionPlan producer (TASK-053)."""

    global _workflow_execution_producer

    if _workflow_execution_producer is None:

        _workflow_execution_producer = WorkflowExecutionProducer(

            planner=get_execution_planner(),

            store=get_execution_plan_store(),

        )

    return _workflow_execution_producer





def get_execution_run_store() -> ExecutionRunStore:

    """Shared in-memory execution run buffer for diagnostics/testing."""

    global _execution_run_store

    if _execution_run_store is None:

        _execution_run_store = ExecutionRunStore()

    return _execution_run_store





def get_execution_runtime() -> ExecutionRuntime:

    """Shared ExecutionRuntime (prepare-only; never invokes handlers)."""

    global _execution_runtime

    if _execution_runtime is None:

        _execution_runtime = ExecutionRuntime(store=get_execution_run_store())

    return _execution_runtime





def get_execution_engine() -> ExecutionEngine:

    """Shared ExecutionEngine (transition validation only; never invokes handlers)."""

    global _execution_engine

    if _execution_engine is None:

        _execution_engine = ExecutionEngine(store=get_execution_run_store())

    return _execution_engine





def get_execution_dispatcher() -> ExecutionDispatcher:
    """Shared ExecutionDispatcher (plan-only; never invokes handlers)."""
    global _execution_dispatcher
    if _execution_dispatcher is None:
        _execution_dispatcher = ExecutionDispatcher(registry=get_execution_registry())
    return _execution_dispatcher


def get_delivery_engine() -> DeliveryEngine:
    """Shared DeliveryEngine (prepare-only; never sends or calls providers)."""
    global _delivery_engine
    if _delivery_engine is None:
        _delivery_engine = DeliveryEngine()
    return _delivery_engine


def get_transport_registry() -> TransportRegistry:
    """Shared TransportRegistry (catalog only; never calls send())."""
    global _transport_registry
    if _transport_registry is None:
        _transport_registry = TransportRegistry()
    return _transport_registry


def get_transport_selector() -> TransportSelector:
    """Shared TransportSelector (selection only; never calls send())."""
    global _transport_selector
    if _transport_selector is None:
        _transport_selector = TransportSelector(registry=get_transport_registry())
    return _transport_selector


def get_provider_executor() -> ProviderExecutor:
    """Shared ProviderExecutor (prepare-only; never calls send())."""
    global _provider_executor
    if _provider_executor is None:
        _provider_executor = ProviderExecutor()
    return _provider_executor


def get_event_dispatcher() -> EventDispatcher:

    """Shared in-process dispatcher with registered consumers."""

    global _dispatcher

    if _dispatcher is None:

        _dispatcher = EventDispatcher()

        register_notification_handler(

            _dispatcher,

            store=get_notification_store(),

            intent_store=get_notification_intent_store(),

            delivery_store=get_notification_delivery_store(),

            persist=True,

        )

        register_timeline_handler(_dispatcher)

        register_dashboard_projection_handler(

            _dispatcher,

            store=get_dashboard_projection_store(),

        )

        register_kpi_projection_handler(

            _dispatcher,

            store=get_kpi_projection_store(),

        )

        register_workflow_handler(

            _dispatcher,

            registry=get_workflow_registry(),

            store=get_workflow_instance_store(),

            on_instances=get_workflow_execution_producer(),

        )

    return _dispatcher





def reset_event_runtime_for_tests() -> None:
    """Clear process singletons (tests only)."""
    global \
        _dispatcher, \
        _notification_store, \
        _intent_store, \
        _delivery_store, \
        _dashboard_projection_store, \
        _kpi_projection_store, \
        _workflow_registry, \
        _workflow_instance_store, \
        _execution_plan_store, \
        _execution_registry, \
        _execution_planner, \
        _workflow_execution_producer, \
        _execution_run_store, \
        _execution_runtime, \
        _execution_engine, \
        _execution_dispatcher, \
        _delivery_engine, \
        _transport_registry, \
        _transport_selector, \
        _provider_executor
    _dispatcher = None
    _notification_store = None
    _intent_store = None
    _delivery_store = None
    _dashboard_projection_store = None
    _kpi_projection_store = None
    _workflow_registry = None
    _workflow_instance_store = None
    _execution_plan_store = None
    _execution_registry = None
    _execution_planner = None
    _workflow_execution_producer = None
    _execution_run_store = None
    _execution_runtime = None
    _execution_engine = None
    _execution_dispatcher = None
    _delivery_engine = None
    _transport_registry = None
    _transport_selector = None
    _provider_executor = None


