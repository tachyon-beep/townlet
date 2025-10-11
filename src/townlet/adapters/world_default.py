"""Default world adapter wiring legacy runtime to the world port."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Callable

from townlet.lifecycle.manager import LifecycleManager
from townlet.observations.builder import ObservationBuilder
from townlet.ports.world import WorldRuntime
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.world.core.context import WorldContext
from townlet.world.core.runtime_adapter import ensure_world_adapter
from townlet.world.grid import WorldState
from townlet.world.runtime import RuntimeStepResult

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.console.command import ConsoleCommandEnvelope
    from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


class DefaultWorldAdapter(WorldRuntime):
    """Adapter that delegates to the existing world runtime implementation."""

    def __init__(
        self,
        *,
        context: WorldContext,
        observation_builder: ObservationBuilder | None = None,
        lifecycle: LifecycleManager | None = None,
        perturbations: PerturbationScheduler | None = None,
        ticks_per_day: int = 0,
    ) -> None:
        self._context = context
        self._lifecycle = lifecycle
        self._perturbations = perturbations
        self._ticks_per_day = max(0, int(ticks_per_day))
        self._pending_actions: dict[str, Any] = {}
        self._queued_console: list["ConsoleCommandEnvelope"] = []
        self._last_result: RuntimeStepResult | None = None
        self._last_events: list[Mapping[str, Any]] = []
        self._last_snapshot: Mapping[str, Any] | None = None

        builder = observation_builder or ObservationBuilder(context.config)
        self._obs_builder = builder
        self._world_adapter = ensure_world_adapter(context.state)
        if getattr(context, "observation_service", None) is None:
            context.observation_service = builder
        if lifecycle is None or perturbations is None:
            raise TypeError(
                "DefaultWorldAdapter requires lifecycle and perturbations when using WorldContext"
            )
        self._tick = getattr(context.state, "tick", 0)

    # ------------------------------------------------------------------
    # Port methods
    # ------------------------------------------------------------------
    def reset(self, seed: int | None = None) -> None:  # pragma: no cover - no-op bridge
        self._context.reset(seed=seed)
        self._pending_actions.clear()
        self._queued_console.clear()
        self._last_result = None
        self._last_events = []
        self._last_snapshot = None
        self._tick = getattr(self._context.state, "tick", 0)

    def queue_console(self, operations: Iterable["ConsoleCommandEnvelope"]) -> None:
        self._queued_console.extend(list(operations))

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable["ConsoleCommandEnvelope"] | None = None,
        action_provider: Callable[[WorldState, int], Mapping[str, Any]] | None = None,
        policy_actions: Mapping[str, Any] | None = None,
    ) -> RuntimeStepResult:
        lifecycle = self._lifecycle
        perturbations = self._perturbations
        if lifecycle is None or perturbations is None:
            raise RuntimeError("Context adapter missing lifecycle/perturbations services")

        queued_ops = list(console_operations) if console_operations is not None else list(self._queued_console)
        self._queued_console.clear()

        combined_actions: dict[str, Any] = {}
        if self._pending_actions:
            combined_actions.update(self._pending_actions)
        if policy_actions:
            combined_actions.update(policy_actions)
        elif action_provider is not None:
            supplied = action_provider(self._context.state, tick)
            combined_actions.update(supplied)

        result = self._context.tick(
            tick=tick,
            console_operations=queued_ops,
            prepared_actions=combined_actions,
            lifecycle=lifecycle,
            perturbations=perturbations,
            ticks_per_day=self._ticks_per_day,
        )
        self._pending_actions.clear()
        self._last_result = result
        self._tick = tick
        self._last_events = [dict(payload) for payload in result.events]
        self._world_adapter = ensure_world_adapter(self._context.state)
        return result

    def agents(self) -> Iterable[str]:
        return self._context.state.agents.keys()

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        terminated = self._last_result.terminated if self._last_result else {}
        builder = self._obs_builder
        if builder is None:
            raise RuntimeError("Observation builder not configured")
        observation_batch = builder.build_batch(self._world_adapter, terminated)
        if agent_ids is None:
            return observation_batch
        return {agent_id: observation_batch[agent_id] for agent_id in agent_ids if agent_id in observation_batch}

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        self._pending_actions = dict(actions)

    def snapshot(self) -> Mapping[str, Any]:
        world_snapshot_getter = getattr(self._context, "snapshot", None)
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

    # ------------------------------------------------------------------
    # Transitional helpers
    # ------------------------------------------------------------------
    def bind_world_adapter(self, adapter: "WorldRuntimeAdapterProtocol") -> None:
        self._world_adapter = adapter


__all__ = ["DefaultWorldAdapter"]
