"""Mutable mapping wrapper for agent snapshots."""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Callable, Dict, Iterable, Iterator, Optional

from .snapshot import AgentSnapshot

AgentCallback = Callable[[AgentSnapshot], None]


class AgentRegistry(MutableMapping[str, AgentSnapshot]):
    """Provide a central access point for agent snapshots.

    The registry preserves compatibility with the legacy ``dict`` interface so
    existing code can continue to use ``world.agents[...]``. Optional
    ``on_add``/``on_remove`` callbacks allow the world façade to hook into
    lifecycle updates (spatial index, employment runtime, etc.).
    """

    def __init__(
        self,
        initial: Optional[Iterable[tuple[str, AgentSnapshot]]] = None,
        *,
        on_add: AgentCallback | None = None,
        on_remove: AgentCallback | None = None,
    ) -> None:
        self._agents: Dict[str, AgentSnapshot] = {}
        self._on_add = on_add
        self._on_remove = on_remove
        if initial is not None:
            for key, snapshot in initial:
                self._agents[str(key)] = snapshot

    def __getitem__(self, key: str) -> AgentSnapshot:
        return self._agents[key]

    def __setitem__(self, key: str, value: AgentSnapshot) -> None:
        self._agents[key] = value
        if self._on_add is not None:
            self._on_add(value)

    def __delitem__(self, key: str) -> None:
        snapshot = self._agents.pop(key)
        if self._on_remove is not None:
            self._on_remove(snapshot)

    def __iter__(self) -> Iterator[str]:
        return iter(self._agents)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._agents)

    def add(self, snapshot: AgentSnapshot) -> AgentSnapshot:
        """Insert ``snapshot`` into the registry and invoke callbacks."""

        self[snapshot.agent_id] = snapshot
        return snapshot

    def discard(self, agent_id: str) -> AgentSnapshot | None:
        """Remove an agent if present and return the snapshot."""

        try:
            snapshot = self._agents.pop(agent_id)
        except KeyError:
            return None
        if self._on_remove is not None:
            self._on_remove(snapshot)
        return snapshot

    def configure_callbacks(
        self,
        *,
        on_add: AgentCallback | None = None,
        on_remove: AgentCallback | None = None,
    ) -> None:
        """Update lifecycle callbacks used during mutation."""

        if on_add is not None:
            self._on_add = on_add
        if on_remove is not None:
            self._on_remove = on_remove

    def values_map(self) -> Dict[str, AgentSnapshot]:
        """Return a shallow copy of the underlying agent map."""

        return dict(self._agents)


__all__ = ["AgentRegistry", "AgentSnapshot", "AgentCallback"]
