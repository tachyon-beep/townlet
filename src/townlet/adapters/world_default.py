"""Default world adapter wiring legacy runtime to the world port."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from townlet.observations.builder import ObservationBuilder
from townlet.ports.world import WorldRuntime
from townlet.world.core.runtime_adapter import WorldRuntimeAdapter, ensure_world_adapter
from townlet.world.grid import WorldState
from townlet.world.runtime import RuntimeStepResult, WorldRuntime as LegacyWorldRuntime


class DefaultWorldAdapter(WorldRuntime):
    """Adapter that delegates to the existing world runtime implementation."""

    def __init__(
        self,
        runtime: LegacyWorldRuntime,
        observation_builder: ObservationBuilder,
    ) -> None:
        self._runtime = runtime
        self._obs_builder = observation_builder
        self._world_adapter = ensure_world_adapter(runtime.world)
        self._pending_actions: dict[str, Any] = {}
        self._last_result: RuntimeStepResult | None = None
        self._tick: int = getattr(runtime.world, "tick", 0)
        self._last_events: list[Mapping[str, Any]] = []
        self._last_snapshot: Mapping[str, Any] | None = None

    # ------------------------------------------------------------------
    # Port methods
    # ------------------------------------------------------------------
    def reset(self, seed: int | None = None) -> None:  # pragma: no cover - no-op bridge
        _ = seed
        # Legacy runtime recreates world externally; leave as no-op for now.

    def tick(self) -> None:
        next_tick = self._tick + 1
        result = self._runtime.tick(tick=next_tick, policy_actions=self._pending_actions)
        self._pending_actions = {}
        self._last_result = result
        self._tick = next_tick
        # Capture emitted events for snapshot consumers.
        self._last_events = [dict(payload) for payload in result.events]
        # Update adapter reference in case world was rebound.
        self._world_adapter = ensure_world_adapter(self._runtime.world)

    def agents(self) -> Iterable[str]:
        return self._runtime.world.agents.keys()

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        terminated = self._last_result.terminated if self._last_result else {}
        observation_batch = self._obs_builder.build_batch(self._world_adapter, terminated)
        if agent_ids is None:
            return observation_batch
        return {agent_id: observation_batch[agent_id] for agent_id in agent_ids if agent_id in observation_batch}

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        self._pending_actions = dict(actions)

    def snapshot(self) -> Mapping[str, Any]:
        world_snapshot_getter = getattr(self._runtime, "snapshot", None)
        if callable(world_snapshot_getter):
            snapshot = world_snapshot_getter()
        else:  # pragma: no cover - defensive
            snapshot = {}
        payload = dict(snapshot)
        payload.setdefault("tick", self._tick)
        payload.setdefault("events", list(self._last_events))
        self._last_snapshot = payload
        # Clear cached events now that they have been exposed.
        self._last_events = []
        return payload

    @property
    def legacy_runtime(self) -> LegacyWorldRuntime:
        """Expose the wrapped legacy runtime for transitional call sites."""

        return self._runtime

    @property
    def world_state(self) -> WorldState:
        """Expose the legacy world instance for compatibility."""

        return self._runtime.world


__all__ = ["DefaultWorldAdapter"]
