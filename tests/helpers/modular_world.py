"""Test harness for exercising the modular world context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from townlet.config import SimulationConfig
from townlet.core.sim_loop import WorldComponents
from townlet.factories.world_factory import create_world
from townlet.lifecycle.manager import LifecycleManager
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.world.core.context import WorldContext
from townlet.world.grid import WorldState


def _ticks_per_day(config: SimulationConfig) -> int:
    observations = getattr(config, "observations_config", None)
    hybrid = getattr(observations, "hybrid", None) if observations is not None else None
    if hybrid is not None:
        value = getattr(hybrid, "time_ticks_per_day", None)
        if value is not None:
            try:
                return max(1, int(value))
            except Exception:  # pragma: no cover - defensive
                return 1440
    return 1440


@dataclass(slots=True)
class ModularTestWorld:
    """Convenience wrapper around ``WorldContext`` for unit tests.

    The wrapper forwards attribute access to the underlying ``WorldState`` so
    existing tests that expect to work with the legacy state object can keep
    their assertions. Mutating helpers (``apply_actions`` / ``resolve_affordances``)
    delegate into the modular context, ensuring we exercise the same pipeline
    used by the production runtime.
    """

    config: SimulationConfig
    state: WorldState
    context: WorldContext
    lifecycle: LifecycleManager
    perturbations: PerturbationScheduler
    ticks_per_day: int

    @classmethod
    def from_config(cls, config: SimulationConfig) -> "ModularTestWorld":
        state = WorldState.from_config(config)
        context = getattr(state, "context", None)
        if context is None:
            raise RuntimeError("WorldState did not initialise WorldContext")
        adapter = create_world(world=state, config=config)
        lifecycle = adapter.lifecycle_manager
        perturbations = adapter.perturbation_scheduler
        return cls(
            config=config,
            state=state,
            context=adapter.context,
            lifecycle=lifecycle,
            perturbations=perturbations,
            ticks_per_day=_ticks_per_day(config),
        )

    # ------------------------------------------------------------------
    # World-like helpers used throughout the legacy tests
    # ------------------------------------------------------------------
    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        self.context.apply_actions(actions)

    def resolve_affordances(
        self,
        *,
        current_tick: int,
        prepared_actions: Mapping[str, Any] | None = None,
        console_operations: Iterable[Mapping[str, Any]] | None = None,
    ) -> Any:
        return self.context.tick(
            tick=current_tick,
            console_operations=tuple(console_operations or ()),
            prepared_actions=dict(prepared_actions or {}),
            lifecycle=self.lifecycle,
            perturbations=self.perturbations,
            ticks_per_day=self.ticks_per_day,
        )

    def drain_events(self) -> list[dict[str, Any]]:
        return self.state.drain_events()

    # ------------------------------------------------------------------
    # Simulation loop integration
    # ------------------------------------------------------------------
    def world_components(self) -> WorldComponents:
        observation_service = getattr(self.context, "observation_service", None)
        if observation_service is None:
            raise RuntimeError("WorldContext missing observation service")
        adapter = create_world(world=self.state, config=self.config)
        return WorldComponents(
            world=self.state,
            lifecycle=adapter.lifecycle_manager,
            perturbations=adapter.perturbation_scheduler,
            observation_service=observation_service,
            world_port=adapter,
            ticks_per_day=self.ticks_per_day,
            provider="default",
        )

    # ------------------------------------------------------------------
    # Attribute forwarding to the underlying state
    # ------------------------------------------------------------------
    def __getattr__(self, name: str) -> Any:  # pragma: no cover - delegation
        return getattr(self.state, name)

    def __setattr__(self, name: str, value: Any) -> None:  # pragma: no cover - delegation
        if name in {
            "config",
            "state",
            "context",
            "lifecycle",
            "perturbations",
            "ticks_per_day",
        }:
            object.__setattr__(self, name, value)
        else:
            setattr(self.state, name, value)
