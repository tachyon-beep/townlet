"""Default world adapter wiring the modular world context to the port."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Any

from townlet.dto.observations import ObservationEnvelope
from townlet.dto.world import SimulationSnapshot
from townlet.lifecycle.manager import LifecycleManager
from townlet.ports.world import WorldRuntime
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.snapshots import snapshot_from_world
from townlet.world.core.context import WorldContext
from townlet.world.core.runtime_adapter import ensure_world_adapter
from townlet.world.grid import WorldState
from townlet.world.runtime import RuntimeStepResult

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.config import SimulationConfig
    from townlet.console.command import ConsoleCommandEnvelope
    from townlet.core.interfaces import TelemetrySinkProtocol
    from townlet.stability.monitor import StabilityMonitor
    from townlet.stability.promotion import PromotionManager
    from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


class DefaultWorldAdapter(WorldRuntime):
    """Adapter that delegates to the existing world runtime implementation."""

    def __init__(
        self,
        *,
        context: WorldContext,
        observation_builder: object | None = None,
        lifecycle: LifecycleManager | None = None,
        perturbations: PerturbationScheduler | None = None,
        ticks_per_day: int = 0,
    ) -> None:
        self._context = context
        self._lifecycle = lifecycle
        self._perturbations = perturbations
        self._ticks_per_day = max(0, int(ticks_per_day))
        self._last_result: RuntimeStepResult | None = None
        self._last_events: list[Mapping[str, Any]] = []
        self._last_snapshot: SimulationSnapshot | None = None
        self._last_envelope: ObservationEnvelope | None = None

        self._world_adapter = ensure_world_adapter(context.state)
        if observation_builder is not None:
            # Transitional: the adapter no longer owns builders; parameter retained for compatibility.
            _ = observation_builder
        if getattr(context, "observation_service", None) is None:
            raise RuntimeError("WorldContext observation service not configured")
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
        self._last_result = None
        self._last_events = []
        self._last_snapshot = None
        self._last_envelope = None
        self._tick = getattr(self._context.state, "tick", 0)

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable[ConsoleCommandEnvelope] | None = None,
        action_provider: Callable[[WorldState, int], Mapping[str, Any]] | None = None,
        policy_actions: Mapping[str, Any] | None = None,
    ) -> RuntimeStepResult:
        lifecycle = self._lifecycle
        perturbations = self._perturbations
        if lifecycle is None or perturbations is None:
            raise RuntimeError("Context adapter missing lifecycle/perturbations services")

        queued_ops = list(console_operations or [])

        combined_actions: dict[str, Any] = {}
        if policy_actions is not None:
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
        self._last_result = result
        self._last_envelope = None
        self._tick = tick
        self._last_events = [dict(payload) for payload in result.events]
        self._world_adapter = ensure_world_adapter(self._context.state)
        return result

    def agents(self) -> Iterable[str]:
        return tuple(self._context.agents_view().keys())

    def observe(self, agent_ids: Iterable[str] | None = None) -> ObservationEnvelope:
        """Produce a DTO observation envelope for the requested agents.

        Args:
            agent_ids: Optional subset of agent IDs to observe. If None, observes all agents.

        Returns:
            ObservationEnvelope: Typed DTO containing agent observations and global context.
        """
        terminated = self._last_result.terminated if self._last_result else {}
        termination_reasons = self._last_result.termination_reasons if self._last_result else {}
        actions = self._last_result.actions if self._last_result else {}
        envelope = self._context.observe(
            agent_ids=agent_ids,
            actions=actions,
            terminated=terminated,
            termination_reasons=termination_reasons,
        )
        self._last_envelope = envelope
        return envelope

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        self._context.apply_actions(actions)

    def snapshot(
        self,
        *,
        config: SimulationConfig | None = None,
        telemetry: TelemetrySinkProtocol | None = None,
        stability: StabilityMonitor | None = None,
        promotion: PromotionManager | None = None,
        rng_streams: Mapping[str, Any] | None = None,
        identity: Mapping[str, Any] | None = None,
    ) -> SimulationSnapshot:
        world_config = config or getattr(self._context, "config", None)
        if world_config is None:
            raise RuntimeError("WorldContext missing configuration for snapshot export")
        state = snapshot_from_world(
            world_config,
            self._context.state,
            lifecycle=self._lifecycle,
            telemetry=telemetry,
            perturbations=self._perturbations,
            stability=stability,
            promotion=promotion,
            rng_streams=rng_streams,
            identity=identity,
        )
        self._last_snapshot = state
        # Clear cached events now that they have been exposed.
        self._last_events = []
        return state

    def components(self) -> dict[str, Any]:
        """Return adapter components for loop initialization.

        This method provides structured access to the adapter's internal
        components without requiring direct property access. Supports the
        migration away from escape hatch properties.

        Returns:
            Dictionary containing 'context', 'lifecycle', and 'perturbations'.
        """
        return {
            "context": self._context,
            "lifecycle": self._lifecycle,
            "perturbations": self._perturbations,
        }

    # ------------------------------------------------------------------
    # Transitional helpers
    # ------------------------------------------------------------------
    def bind_world_adapter(self, adapter: WorldRuntimeAdapterProtocol) -> None:
        self._world_adapter = adapter


__all__ = ["DefaultWorldAdapter"]
