"""World state container for the modular runtime."""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, TYPE_CHECKING

from townlet.world.agents.registry import AgentRecord, AgentRegistry
from townlet.world.events import Event, EventDispatcher

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.config import SimulationConfig
    from townlet.world.agents.snapshot import AgentSnapshot


@dataclass
class WorldState:
    """Encapsulates mutable world data surfaced through the WP1 ports."""

    config: "SimulationConfig"
    tick: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    rng_seed: int | None = None

    agents: AgentRegistry = field(init=False)
    _rng: random.Random = field(init=False, repr=False)
    _rng_state: tuple[Any, ...] | None = field(default=None, init=False, repr=False)
    _ctx_reset_requests: set[str] = field(default_factory=set, init=False, repr=False)
    _events: EventDispatcher = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random()
        if self.rng_seed is not None:
            self.seed_rng(self.rng_seed)
        else:
            self._rng_state = self._rng.getstate()
        self.agents = AgentRegistry()
        self._events = EventDispatcher()

    # ------------------------------------------------------------------
    # RNG helpers
    # ------------------------------------------------------------------
    def seed_rng(self, seed: int) -> None:
        """Seed the world RNG and persist the state for determinism."""

        self.rng_seed = seed
        self._rng.seed(seed)
        self._rng_state = self._rng.getstate()

    @property
    def rng(self) -> random.Random:
        """Return the RNG used for world-level randomness."""

        return self._rng

    def get_rng_state(self) -> tuple[Any, ...]:
        """Expose the RNG state for snapshotting."""

        if self._rng_state is None:
            self._rng_state = self._rng.getstate()
        return self._rng_state

    def set_rng_state(self, state: tuple[Any, ...]) -> None:
        """Restore the RNG state from a snapshot."""

        self._rng_state = state
        self._rng.setstate(state)

    # ------------------------------------------------------------------
    # Agent management
    # ------------------------------------------------------------------
    def register_agent(
        self,
        snapshot: "AgentSnapshot",
        *,
        tick: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "AgentSnapshot":
        """Insert or replace an agent snapshot in the registry."""

        return self.agents.add(snapshot, tick=tick, metadata=metadata)

    def remove_agent(self, agent_id: str) -> "AgentSnapshot | None":
        """Remove an agent and return the previous snapshot."""

        return self.agents.discard(agent_id)

    def agent_snapshots_view(self) -> Mapping[str, "AgentSnapshot"]:
        """Return an immutable view over agent snapshots."""

        return self.agents.snapshots_view()

    def agent_records_view(self) -> Mapping[str, AgentRecord]:
        """Return read-only access to agent bookkeeping records."""

        return self.agents.records_map()

    # ------------------------------------------------------------------
    # Context-reset signalling (observation hints)
    # ------------------------------------------------------------------
    def request_ctx_reset(self, agent_id: str) -> None:
        """Mark an agent so the next observation toggles ctx_reset_flag."""

        self._ctx_reset_requests.add(agent_id)

    def consume_ctx_reset_requests(self) -> set[str]:
        """Return and clear pending ctx reset requests."""

        pending = set(self._ctx_reset_requests)
        self._ctx_reset_requests.clear()
        return pending

    # ------------------------------------------------------------------
    # Event emission
    # ------------------------------------------------------------------
    def emit_event(
        self,
        event_type: str,
        payload: Mapping[str, Any] | None = None,
        *,
        tick: int | None = None,
        ts: float | None = None,
    ) -> Event:
        """Record a domain event for downstream consumers."""

        return self._events.emit(
            type=event_type,
            payload=dict(payload or {}),
            tick=self.tick if tick is None else tick,
            ts=ts,
        )

    def drain_events(self) -> list[dict[str, Any]]:
        """Return accumulated events as serialisable mappings."""

        return [event.to_dict() for event in self._events.drain()]

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------
    def reset(self, *, seed: int | None = None) -> None:
        """Restore the world to a clean state while keeping configuration."""

        if seed is not None:
            self.seed_rng(seed)
        elif self.rng_seed is not None:
            self.seed_rng(self.rng_seed)
        else:
            self._rng_state = self._rng.getstate()

        self.tick = 0
        self.metadata.clear()
        self.agents.clear()
        self._ctx_reset_requests.clear()
        self._events.clear()

    def snapshot(self) -> dict[str, Any]:
        """Return a serialisable snapshot of core world state."""

        agents_copy = {
            agent_id: copy.deepcopy(snapshot)
            for agent_id, snapshot in self.agents.snapshots_view().items()
        }
        return {
            "tick": self.tick,
            "agents": agents_copy,
            "metadata": copy.deepcopy(self.metadata),
        }

    def metadata_view(self) -> Mapping[str, Any]:
        """Return a read-only view of metadata stored on the world."""

        return MappingProxyType(self.metadata)


__all__ = ["WorldState"]
