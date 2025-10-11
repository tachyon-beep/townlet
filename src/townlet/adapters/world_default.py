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
from townlet.world.runtime import RuntimeStepResult, WorldRuntime as LegacyWorldRuntime

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.console.command import ConsoleCommandEnvelope
    from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


class DefaultWorldAdapter(WorldRuntime):
    """Adapter that delegates to the existing world runtime implementation."""

    def __init__(
        self,
        *,
        runtime: LegacyWorldRuntime | None = None,
        context: WorldContext | None = None,
        observation_builder: ObservationBuilder | None = None,
        lifecycle: LifecycleManager | None = None,
        perturbations: PerturbationScheduler | None = None,
        ticks_per_day: int = 0,
    ) -> None:
        if runtime is None and context is None:
            raise TypeError("DefaultWorldAdapter requires either 'runtime' or 'context'")
        if runtime is not None and context is not None:
            raise TypeError("DefaultWorldAdapter cannot receive both 'runtime' and 'context'")

        self._obs_builder = observation_builder
        self._legacy_runtime: LegacyWorldRuntime | None = runtime
        self._context: WorldContext | None = context
        self._lifecycle = lifecycle
        self._perturbations = perturbations
        self._ticks_per_day = max(0, int(ticks_per_day))
        self._pending_actions: dict[str, Any] = {}
        self._queued_console: list["ConsoleCommandEnvelope"] = []
        self._last_result: RuntimeStepResult | None = None
        self._last_events: list[Mapping[str, Any]] = []
        self._last_snapshot: Mapping[str, Any] | None = None

        if runtime is not None:
            builder = observation_builder or ObservationBuilder(runtime.world.config)
            self._obs_builder = builder
            self._world_adapter = ensure_world_adapter(runtime.world)
            self._tick: int = getattr(runtime.world, "tick", 0)
        else:
            assert context is not None
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
        if self._legacy_runtime is not None:
            _ = seed
            return
        if self._context is not None:
            self._context.reset(seed=seed)
            self._pending_actions.clear()
            self._queued_console.clear()
            self._last_result = None

    def queue_console(self, operations: Iterable["ConsoleCommandEnvelope"]) -> None:
        if self._legacy_runtime is not None:
            self._legacy_runtime.queue_console(operations)
            return
        self._queued_console.extend(list(operations))

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable["ConsoleCommandEnvelope"] | None = None,
        action_provider: Callable[[WorldState, int], Mapping[str, Any]] | None = None,
        policy_actions: Mapping[str, Any] | None = None,
    ) -> RuntimeStepResult:
        if self._legacy_runtime is not None:
            if policy_actions is not None:
                pending_actions: Mapping[str, Any] | None = dict(policy_actions)
            elif self._pending_actions:
                pending_actions = dict(self._pending_actions)
            else:
                pending_actions = None
            result = self._legacy_runtime.tick(
                tick=tick,
                console_operations=console_operations,
                action_provider=action_provider,
                policy_actions=pending_actions,
            )
            self._pending_actions = {}
            self._last_result = result
            self._tick = tick
            self._last_events = [dict(payload) for payload in result.events]
            self._world_adapter = ensure_world_adapter(self._legacy_runtime.world)
            return result

        assert self._context is not None
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
        return result

    def agents(self) -> Iterable[str]:
        if self._legacy_runtime is not None:
            return self._legacy_runtime.world.agents.keys()
        assert self._context is not None
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
        if self._legacy_runtime is not None:
            world_snapshot_getter = getattr(self._legacy_runtime, "snapshot", None)
        else:
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
        if self._legacy_runtime is not None:
            binder = getattr(self._legacy_runtime, "bind_world_adapter", None)
            if callable(binder):
                binder(adapter)
        self._world_adapter = adapter

    @property
    def world_state(self) -> WorldState:
        """Expose the legacy world instance for compatibility."""

        if self._legacy_runtime is not None:
            return self._legacy_runtime.world
        assert self._context is not None
        return self._context.state


__all__ = ["DefaultWorldAdapter"]
