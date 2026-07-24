"""Transport Adapter Foundation package (TASK-058).

Provider abstraction: registry + selector. Never sends. No provider implementations.
"""

from app.modules.transport.adapter import TransportAdapter
from app.modules.transport.models import TransportCapability, TransportResult
from app.modules.transport.registry import TransportRegistry
from app.modules.transport.selector import TransportSelector

__all__ = [
    "TransportAdapter",
    "TransportCapability",
    "TransportRegistry",
    "TransportResult",
    "TransportSelector",
]
