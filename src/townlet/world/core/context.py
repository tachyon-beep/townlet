"""Context façade exposing shared world services and orchestrating ticks."""

from __future__ import annotations

import random
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, TYPE_CHECKING

from townlet.console.command import ConsoleCommandEnvelope, ConsoleCommandResult
from townlet.world.actions import Action, apply_actions
from townlet.world.rng import RngStreamManager
from townlet.world.systems import default_systems
from townlet.world.systems.base import SystemContext, SystemStep

if TYPE_CHECKING:  # pragma: no cover
    from townlet.world.affordance_runtime_service import AffordanceRuntimeService
    from townlet.world.agents.employment import EmploymentService
    from townlet.world.agents.lifecycle import LifecycleService
    from townlet.world.agents.nightly_reset import NightlyResetService
    from townlet.world.agents.relationships_service import RelationshipService
    from townlet.world.console.service import ConsoleService
    from townlet.world.economy import EconomyService
    from townlet.world.employment_runtime import EmploymentRuntime
    from townlet.world.employment_service import EmploymentCoordinator
    from townlet.world.grid import WorldState
    from townlet.world.perturbations.service import PerturbationService
    from townlet.world.queue import QueueConflictTracker, QueueManager
    from townlet.lifecycle.manager import LifecycleManager
    from townlet.scheduler.perturbations import PerturbationScheduler


@dataclass(slots=True)
class WorldContext:
    """Facade around the modular world capable of executing ticks."""

    state: "WorldState"
    queue_manager: "QueueManager"
    queue_conflicts: "QueueConflictTracker"
    affordance_service: "AffordanceRuntimeService"
    console: "ConsoleService"
    employment: "EmploymentCoordinator"
    employment_runtime: "EmploymentRuntime"
    employment_service: "EmploymentService"
    lifecycle_service: "LifecycleService"
    nightly_reset_service: "NightlyResetService"
    relationships: "RelationshipService"
    economy_service: "EconomyService"
    perturbation_service: "PerturbationService"
    config: object
    emit_event_callback: Callable[[str, dict[str, Any]], None]
    sync_reservation_callback: Callable[[str], None]
    systems: tuple[SystemStep, ...] | None = None
    rng_manager: RngStreamManager | None = None
    _pending_actions: dict[str, object] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.systems is None:
            self.systems = default_systems()
        if self.rng_manager is None:
            seed = getattr(self.state, "rng_seed", None)
            self.rng_manager = RngStreamManager.from_seed(seed)

    # ------------------------------------------------------------------
    # Views into underlying state
    # ------------------------------------------------------------------
    def agents_view(self) -> Mapping[str, object]:
        return self.state.agent_snapshots_view()

    def objects_view(self) -> Mapping[str, object]:
        return MappingProxyType(self.state.objects)

    def affordances_view(self) -> Mapping[str, object]:
        return MappingProxyType(self.state.affordances)

    def running_affordances_view(self) -> Mapping[str, object]:
        return MappingProxyType(self.state.running_affordances_snapshot())

    # ------------------------------------------------------------------
    # Event and reservation helpers
    # ------------------------------------------------------------------
    def emit_event(self, event: str, payload: dict[str, Any]) -> None:
        self.emit_event_callback(event, payload)

    def sync_reservation(self, object_id: str) -> None:
        self.sync_reservation_callback(object_id)

    @property
    def console_bridge(self) -> Any:
        """Expose the console bridge for integrations/tests."""

        return getattr(self.console, "bridge", None)

    # ------------------------------------------------------------------
    # Orchestration API
    # ------------------------------------------------------------------
    def reset(self, *, seed: int | None = None) -> None:
        reset_fn = getattr(self.state, "reset", None)
        if callable(reset_fn):
            reset_fn(seed=seed)
        else:
            self.state.tick = 0
            if seed is not None:
                rng = getattr(self.state, "rng", None)
                if isinstance(rng, random.Random):
                    rng.seed(seed)
            drain = getattr(self.state, "drain_events", None)
            if callable(drain):
                drain()
        self._pending_actions.clear()
        self.rng_manager = RngStreamManager.from_seed(getattr(self.state, "rng_seed", None))

    def apply_actions(self, actions: Mapping[str, object]) -> None:
        for agent_id, payload in actions.items():
            if isinstance(payload, Action):
                self._pending_actions[agent_id] = payload
            elif isinstance(payload, Mapping):
                self._pending_actions[agent_id] = dict(payload)
            else:
                self._pending_actions[agent_id] = payload

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable[ConsoleCommandEnvelope],
        prepared_actions: Mapping[str, object],
        lifecycle: LifecycleManager,
        perturbations: PerturbationScheduler,
        ticks_per_day: int,
    ) -> dict[str, Any]:
        state = self.state
        state.tick = tick

        lifecycle.process_respawns(state, tick=tick)
        state.apply_console(console_operations)
        console_results = list(state.consume_console_results())

        perturbations.tick(state, current_tick=tick)

        combined_actions: dict[str, object] = {}
        if self._pending_actions:
            combined_actions.update(self._pending_actions)
        if prepared_actions:
            combined_actions.update(prepared_actions)

        action_objects = self._coerce_actions(combined_actions)
        if action_objects:
            apply_actions(state, action_objects)
        self._pending_actions.clear()

        rng_manager = self.rng_manager or RngStreamManager.from_seed(getattr(state, "rng_seed", None))
        dispatcher = state.event_dispatcher()
        system_ctx = SystemContext(
            state=state,
            rng=rng_manager,
            events=dispatcher,
        )
        self.rng_manager = rng_manager
        for step in self.systems or ():
            step(system_ctx)

        if ticks_per_day and tick % ticks_per_day == 0:
            self.nightly_reset_service.apply(tick)

        terminated = dict(lifecycle.evaluate(state, tick=tick))
        termination_reasons = dict(lifecycle.termination_reasons())
        events = state.drain_events()

        result_payload = {
            "console_results": console_results,
            "events": events,
            "actions": {key: combined_actions[key] for key in combined_actions},
            "terminated": terminated,
            "termination_reasons": termination_reasons,
        }
        from townlet.world.runtime import RuntimeStepResult

        return RuntimeStepResult(**result_payload)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------
    def snapshot(self) -> Mapping[str, object]:
        return self.state.snapshot()

    def apply_nightly_reset(self, tick: int) -> list[str]:
        """Delegate nightly reset to the configured service."""

        return self.nightly_reset_service.apply(tick)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _coerce_actions(self, actions: Mapping[str, object]) -> list[Action]:
        coerced: list[Action] = []
        for agent_id, payload in actions.items():
            if isinstance(payload, Action):
                coerced.append(payload)
                continue
            if isinstance(payload, Mapping):
                data = dict(payload)
                kind = str(data.get("kind", "noop"))
                coerced.append(Action(agent_id=agent_id, kind=kind, payload=data))
                continue
            self.state.emit_event(
                "action.invalid",
                {
                    "agent_id": agent_id,
                    "error": "payload must be a mapping",
                },
            )
        return coerced


__all__ = ["WorldContext"]
