"""Context façade exposing shared world services and orchestrating ticks."""

from __future__ import annotations

import hashlib
import pickle
import random
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from townlet.console.command import ConsoleCommandEnvelope
from townlet.world.actions import Action, apply_actions
from townlet.world.core.runtime_adapter import ensure_world_adapter
from townlet.world.dto import build_observation_envelope
from townlet.world.dto.observation import ObservationEnvelope
from townlet.world.observations.context import (
    agent_context as observation_agent_context,
)
from townlet.world.rng import RngStreamManager
from townlet.world.systems import default_systems
from townlet.world.systems.affordances import process_actions
from townlet.world.systems.base import SystemContext, SystemStep

if TYPE_CHECKING:  # pragma: no cover
    from townlet.lifecycle.manager import LifecycleManager
    from townlet.scheduler.perturbations import PerturbationScheduler
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
    from townlet.world.observations.interfaces import ObservationServiceProtocol
    from townlet.world.perturbations.service import PerturbationService
    from townlet.world.queue import QueueConflictTracker, QueueManager


@dataclass(slots=True)
class WorldContext:
    """Facade around the modular world capable of executing ticks."""

    state: WorldState
    queue_manager: QueueManager
    queue_conflicts: QueueConflictTracker
    affordance_service: AffordanceRuntimeService
    console: ConsoleService
    employment: EmploymentCoordinator
    employment_runtime: EmploymentRuntime
    employment_service: EmploymentService
    lifecycle_service: LifecycleService
    nightly_reset_service: NightlyResetService
    relationships: RelationshipService
    economy_service: EconomyService
    perturbation_service: PerturbationService
    config: object
    emit_event_callback: Callable[[str, dict[str, Any]], None]
    sync_reservation_callback: Callable[[str], None]
    observation_service: ObservationServiceProtocol | None = None
    systems: tuple[SystemStep, ...] | None = None
    rng_manager: RngStreamManager | None = None
    _pending_actions: dict[str, object] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.systems is None:
            self.systems = default_systems()
        if self.rng_manager is None:
            seed = getattr(self.state, "rng_seed", None)
            if seed is None:
                seed = _derive_seed_from_state(self.state.get_rng_state())
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
        seed_value = getattr(self.state, "rng_seed", None)
        if seed_value is None:
            seed_value = _derive_seed_from_state(self.state.get_rng_state())
        self.rng_manager = RngStreamManager.from_seed(seed_value)

    def apply_actions(self, actions: Mapping[str, object]) -> None:
        for agent_id, payload in actions.items():
            if payload is None:
                # Treat None as an explicit "no action" marker.
                self._pending_actions.pop(agent_id, None)
                continue
            if isinstance(payload, Action):
                self._pending_actions[agent_id] = payload
                continue
            if isinstance(payload, Mapping):
                self._pending_actions[agent_id] = dict(payload)
                continue
            raise TypeError(
                f"Unsupported action payload for agent '{agent_id}': {type(payload)!r}"
            )

    def observe(
        self,
        agent_ids: Iterable[str] | None = None,
        *,
        actions: Mapping[str, object] | None = None,
        terminated: Mapping[str, bool] | None = None,
        termination_reasons: Mapping[str, str] | None = None,
        rewards: Mapping[str, float] | None = None,
        reward_breakdown: Mapping[str, Mapping[str, float]] | None = None,
        policy_snapshot: Mapping[str, object] | None = None,
        policy_metadata: Mapping[str, object] | None = None,
        rivalry_events: Iterable[Mapping[str, object]] | None = None,
        stability_metrics: Mapping[str, object] | None = None,
        promotion_state: Mapping[str, object] | None = None,
        anneal_context: Mapping[str, object] | None = None,
    ) -> ObservationEnvelope:
        if self.observation_service is None:
            raise RuntimeError("WorldContext observation service not configured")

        adapter = ensure_world_adapter(self.state)
        terminated_map = dict(terminated or {})
        raw_batch = self.observation_service.build_batch(adapter, terminated_map)
        contexts = {
            agent_id: observation_agent_context(adapter, agent_id)
            for agent_id in raw_batch.keys()
        }

        target_ids = set(agent_ids) if agent_ids is not None else raw_batch.keys()
        filtered_batch = {
            agent_id: raw_batch[agent_id]
            for agent_id in target_ids
            if agent_id in raw_batch
        }
        filtered_contexts = {
            agent_id: contexts.get(agent_id, {})
            for agent_id in filtered_batch.keys()
        }

        filtered_actions = {}
        if actions:
            for agent in filtered_batch.keys():
                if agent in actions:
                    filtered_actions[str(agent)] = _to_mapping(actions[agent])

        return build_observation_envelope(
            tick=self.state.tick,
            observations=filtered_batch,
            actions=filtered_actions,
            terminated={str(agent): bool(terminated_map.get(agent, False)) for agent in filtered_batch.keys()},
            termination_reasons={str(agent): str((termination_reasons or {}).get(agent, "")) for agent in filtered_batch.keys()},
            queue_metrics=self.export_queue_metrics(),
            rewards={str(agent): float((rewards or {}).get(agent, 0.0)) for agent in filtered_batch.keys()},
            reward_breakdown={
                str(agent): {
                    str(component): float(value)
                    for component, value in ((reward_breakdown or {}).get(agent, {})).items()
                }
                for agent in filtered_batch.keys()
            },
            perturbations=self.export_perturbation_state(),
            policy_snapshot=_to_mapping(policy_snapshot),
            policy_metadata=_to_mapping(policy_metadata),
            rivalry_events=list(rivalry_events or []),
            stability_metrics=_to_mapping(stability_metrics),
            promotion_state=_to_mapping(promotion_state) or None,
            rng_seed=getattr(self.state, "rng_seed", None),
            queues=self.export_queue_state(),
            running_affordances=self.export_running_affordances(),
            relationship_snapshot=self.export_relationship_snapshot(),
            relationship_metrics=self.export_relationship_metrics(),
            agent_snapshots=self.state.agent_snapshots_view(),
            job_snapshot=self.export_job_snapshot(),
            queue_affinity_metrics=self.export_queue_affinity_metrics(),
            employment_snapshot=self.export_employment_snapshot(),
            economy_snapshot=self.export_economy_snapshot(),
            anneal_context=_to_mapping(anneal_context),
            agent_contexts=filtered_contexts,
        )

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
        console_results = list(state.apply_console(console_operations))

        perturbations.tick(state, current_tick=tick)

        combined_actions: dict[str, object] = {}
        if self._pending_actions:
            combined_actions.update(self._pending_actions)
        if prepared_actions:
            combined_actions.update(prepared_actions)

        action_objects = self._coerce_actions(combined_actions)
        if action_objects:
            apply_actions(state, action_objects)
        if combined_actions:
            process_actions(state, combined_actions, tick=tick)
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

        episode_span = None
        if ticks_per_day and ticks_per_day > 0:
            try:
                episode_span = max(1, int(ticks_per_day))
            except Exception:  # pragma: no cover - defensive
                episode_span = None
        if episode_span:
            for snapshot in state.agent_snapshots_view().values():
                current_tick = getattr(snapshot, "episode_tick", 0)
                try:
                    snapshot.episode_tick = (int(current_tick) + 1) % episode_span
                except Exception:  # pragma: no cover - defensive
                    snapshot.episode_tick = 0

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
    # Snapshot helpers used for observation/telemetry assembly
    # ------------------------------------------------------------------
    def export_queue_metrics(self) -> Mapping[str, int]:
        try:
            raw = self.queue_manager.metrics()
            return {str(key): int(value) for key, value in raw.items()}
        except Exception:  # pragma: no cover - defensive
            return {}

    def export_queue_affinity_metrics(self) -> Mapping[str, int]:
        try:
            raw = self.queue_manager.performance_metrics()
            return {str(key): int(value) for key, value in raw.items()}
        except Exception:  # pragma: no cover - defensive
            return {}

    def export_queue_state(self) -> Mapping[str, Any]:
        try:
            snapshot = self.queue_manager.export_state()
            return snapshot if isinstance(snapshot, Mapping) else {}
        except Exception:  # pragma: no cover - defensive
            return {}

    def export_running_affordances(self) -> Mapping[str, Any]:
        try:
            return self.affordance_service.runtime_snapshot()
        except Exception:  # pragma: no cover - defensive
            return {}

    def export_relationship_snapshot(self) -> Mapping[str, Mapping[str, Mapping[str, float]]]:
        try:
            snapshot = self.relationships.relationships_snapshot()
            if isinstance(snapshot, Mapping):
                return snapshot
        except Exception:  # pragma: no cover - defensive
            return {}
        return {}

    def export_relationship_metrics(self) -> Mapping[str, Any]:
        getter = getattr(self.relationships, "relationship_metrics_snapshot", None)
        if callable(getter):
            try:
                metrics = getter()
                if isinstance(metrics, Mapping):
                    return metrics
            except Exception:  # pragma: no cover - defensive
                return {}
        return {}

    def export_employment_snapshot(self) -> Mapping[str, Any]:
        state_getter = getattr(self.state, "employment_queue_snapshot", None)
        if callable(state_getter):
            try:
                snapshot = state_getter()
                if isinstance(snapshot, Mapping):
                    return snapshot
            except Exception:  # pragma: no cover - defensive
                return {}
        getter = getattr(self.employment_service, "snapshot", None)
        if callable(getter):
            try:
                snapshot = getter()
                if isinstance(snapshot, Mapping):
                    return snapshot
            except Exception:  # pragma: no cover - defensive
                return {}
        return {}

    def export_job_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        snapshot: dict[str, dict[str, object]] = {}
        basket_cost_getter = getattr(self.economy_service, "basket_cost_for_agent", None)
        for agent_id, agent in self.state.agent_snapshots_view().items():
            job_payload: dict[str, object] = {
                "job_id": getattr(agent, "job_id", None),
                "on_shift": bool(getattr(agent, "on_shift", False)),
                "shift_state": getattr(agent, "shift_state", None),
                "lateness_counter": int(getattr(agent, "lateness_counter", 0)),
                "wallet": float(getattr(agent, "wallet", 0.0)),
                "attendance_ratio": float(getattr(agent, "attendance_ratio", 0.0)),
                "exit_pending": bool(getattr(agent, "exit_pending", False)),
                "late_ticks_today": int(getattr(agent, "late_ticks_today", 0)),
                "absent_shifts_7d": int(getattr(agent, "absent_shifts_7d", 0)),
                "wages_withheld": float(getattr(agent, "wages_withheld", 0.0)),
            }
            if callable(basket_cost_getter):
                try:
                    job_payload["basket_cost"] = float(basket_cost_getter(agent.agent_id))
                except Exception:  # pragma: no cover - defensive
                    job_payload["basket_cost"] = 0.0
            else:
                job_payload["basket_cost"] = 0.0
            inventory = getattr(agent, "inventory", None)
            if isinstance(inventory, Mapping):
                job_payload["inventory"] = dict(inventory)
            needs = getattr(agent, "needs", None)
            if isinstance(needs, Mapping):
                job_payload["needs"] = {
                    str(need): float(value)
                    for need, value in needs.items()
                }
            snapshot[str(agent_id)] = job_payload
        return snapshot

    def export_economy_snapshot(self) -> Mapping[str, Any]:
        snapshot: dict[str, Any] = {}
        settings_getter = getattr(self.state, "economy_settings", None)
        if callable(settings_getter):
            try:
                snapshot["settings"] = settings_getter()
            except Exception:  # pragma: no cover - defensive
                pass
        price_spikes_getter = getattr(self.state, "active_price_spikes", None)
        if callable(price_spikes_getter):
            try:
                snapshot["active_price_spikes"] = price_spikes_getter()
            except Exception:  # pragma: no cover - defensive
                pass
        utility_getter = getattr(self.state, "utility_snapshot", None)
        if callable(utility_getter):
            try:
                snapshot["utility_snapshot"] = utility_getter()
            except Exception:  # pragma: no cover - defensive
                pass
        if snapshot:
            return snapshot
        getter = getattr(self.economy_service, "snapshot", None)
        if callable(getter):
            try:
                snapshot = getter()
                if isinstance(snapshot, Mapping):
                    return snapshot
            except Exception:  # pragma: no cover - defensive
                return {}
        return {}

    def export_perturbation_state(self) -> Mapping[str, Any]:
        getter = getattr(self.perturbation_service, "latest_state", None)
        if callable(getter):
            try:
                state = getter()
                if isinstance(state, Mapping):
                    return state
            except Exception:  # pragma: no cover - defensive
                return {}
        return {}

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


def _derive_seed_from_state(state: tuple[Any, ...]) -> int:
    payload = pickle.dumps(state)
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


__all__ = ["WorldContext"]
def _to_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {}
