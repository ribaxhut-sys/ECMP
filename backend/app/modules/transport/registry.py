"""TransportRegistry — catalog of transport adapters (TASK-058).

Register and look up adapters by channel. Never calls send() / health().
"""

from __future__ import annotations

from app.modules.transport.adapter import TransportAdapter
from app.modules.transport.models import TransportCapability

_KNOWN = frozenset(c.value for c in TransportCapability)


def _normalize_channel(channel: TransportCapability | str) -> str | None:
    if isinstance(channel, TransportCapability):
        return channel.value
    token = str(channel or "").strip().upper()
    if not token:
        return None
    if token not in _KNOWN:
        return None
    return token


class TransportRegistry:
    """In-memory adapter catalog. Lookup only — no execution."""

    def __init__(self) -> None:
        self._adapters: list[TransportAdapter] = []

    def register(self, adapter: TransportAdapter) -> None:
        """Register an adapter. Does not call send() or health()."""
        if not isinstance(adapter, TransportAdapter):
            raise TypeError(
                f"adapter must be TransportAdapter, got {type(adapter).__name__}"
            )
        name = (adapter.name or "").strip()
        if not name:
            raise ValueError("adapter.name must be a non-empty string")
        # Replace same-name adapter to keep catalog deterministic
        self._adapters = [a for a in self._adapters if a.name != name]
        self._adapters.append(adapter)

    def unregister(self, name: str) -> bool:
        """Remove adapter by name. Returns True if removed."""
        before = len(self._adapters)
        self._adapters = [a for a in self._adapters if a.name != name]
        return len(self._adapters) < before

    def lookup(self, channel: TransportCapability | str) -> TransportAdapter | None:
        """Return first registered adapter that supports channel. No send()."""
        normalized = _normalize_channel(channel)
        if normalized is None:
            return None
        capability = TransportCapability(normalized)
        for adapter in self._adapters:
            if adapter.supports(capability):
                return adapter
        return None

    def has(self, channel: TransportCapability | str) -> bool:
        return self.lookup(channel) is not None

    def adapters(self) -> tuple[TransportAdapter, ...]:
        return tuple(self._adapters)

    def clear(self) -> None:
        self._adapters.clear()

    def __len__(self) -> int:
        return len(self._adapters)
