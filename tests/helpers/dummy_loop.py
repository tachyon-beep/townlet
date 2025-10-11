from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Sequence

from townlet.console.command import ConsoleCommandEnvelope
from townlet.core.sim_loop import (
    SimulationLoop,
    TelemetryComponents,
    WorldComponents,
    PolicyComponents,
)
from townlet.snapshots.state import SnapshotState
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.testing import DummyTelemetrySink
from townlet.world.dto.observation import (
    AgentObservationDTO,
    GlobalObservationDTO,
    ObservationEnvelope,
)
from townlet.world.runtime import RuntimeStepResult


@dataclass(slots=True)
class DummyAgentSnapshot:
    agent_id: str
    needs: dict[str, float] = field(default_factory=lambda: {"hunger": 1.0})
    episode_tick: int = 0
    job_id: str = "dummy_job"


class _DummyWorldState:
    """Minimal world-like object satisfying SimulationLoop expectations."""

    def __init__(self, agent_ids: Sequence[str]) -> None:
        self.config_id = "dummy-config"
        self.tick = 0
        self.agents: dict[str, DummyAgentSnapshot] = {
            agent_id: DummyAgentSnapshot(agent_id) for agent_id in agent_ids
        }
        self.context: _DummyWorldContext | None = None
        self._rng_state: object | None = None
        self._ctx_reset: set[str] = set()

    def request_ctx_reset(self, agent_id: str) -> None:
        self._ctx_reset.add(agent_id)

    def consume_ctx_reset_requests(self) -> set[str]:
        pending = set(self._ctx_reset)
        self._ctx_reset.clear()
        return pending

    def set_rng_state(self, state: object) -> None:  # pragma: no cover - deterministic stub
        self._rng_state = state


class _DummyObservationService:
    """Sentinel observation service satisfying attribute checks."""


class _DummyWorldContext:
    """Stubbed world context providing DTO exports for the loop."""

    def __init__(self, state: _DummyWorldState) -> None:
        self.state = state
        self.state.context = self
        self.observation_service = _DummyObservationService()
        self.rng_manager = None
        self.queue_metrics: dict[str, int] = {"pending": 0}
        self.queue_state: dict[str, Any] = {"queues": {}}
        self.employment_snapshot: dict[str, Any] = {"pending_count": 0}
        self.job_snapshot: dict[str, Any] = {"jobs": {}}
        self.running_affordances: dict[str, Any] = {}
        self.relationship_snapshot: dict[str, Any] = {}
        self.relationship_metrics: dict[str, Any] = {}
        self.economy_snapshot: dict[str, Any] = {}
        self.queue_affinity_metrics: dict[str, Any] = {}
        self.perturbations: dict[str, Any] = {"pending": [], "active": []}
        self.rewards: dict[str, Any] = {}

    def apply_actions(self, actions: Mapping[str, Any]) -> None:  # pragma: no cover - not exercised
        _ = actions

    def export_queue_metrics(self) -> Mapping[str, int]:
        return dict(self.queue_metrics)

    def export_queue_state(self) -> Mapping[str, Any]:
        return copy.deepcopy(self.queue_state)

    def export_employment_snapshot(self) -> Mapping[str, Any]:
        return copy.deepcopy(self.employment_snapshot)

    def export_job_snapshot(self) -> Mapping[str, Mapping[str, Any]]:
        return copy.deepcopy(self.job_snapshot)

    def export_queue_affinity_metrics(self) -> Mapping[str, Any]:
        return dict(self.queue_affinity_metrics)

    def export_running_affordances(self) -> Mapping[str, Any]:
        return copy.deepcopy(self.running_affordances)

    def export_relationship_snapshot(self) -> Mapping[str, Any]:
        return copy.deepcopy(self.relationship_snapshot)

    def export_relationship_metrics(self) -> Mapping[str, Any]:
        return copy.deepcopy(self.relationship_metrics)

    def export_economy_snapshot(self) -> Mapping[str, Any]:
        return copy.deepcopy(self.economy_snapshot)

    def observe(
        self,
        *,
        actions: Mapping[str, Any],
        policy_snapshot: Mapping[str, Any],
        policy_metadata: Mapping[str, Any],
        rivalry_events: Iterable[Mapping[str, Any]],
        stability_metrics: Mapping[str, Any],
        promotion_state: Mapping[str, Any] | None,
        anneal_context: Mapping[str, Any],
        terminated: Mapping[str, bool],
        termination_reasons: Mapping[str, str],
        rewards: Mapping[str, float],
        reward_breakdown: Mapping[str, Mapping[str, float]],
    ) -> ObservationEnvelope:
        agents_dto = [
            AgentObservationDTO(
                agent_id=agent_id,
                needs=dict(snapshot.needs),
                job={"job_id": snapshot.job_id},
                metadata={"episode_tick": snapshot.episode_tick},
                pending_intent=None,
                queue_state={"pending": []},
            )
            for agent_id, snapshot in self.state.agents.items()
        ]
        global_dto = GlobalObservationDTO(
            queue_metrics=dict(self.queue_metrics),
            rewards={
                agent_id: dict(reward_breakdown.get(agent_id, {}))
                for agent_id in reward_breakdown
            },
            perturbations=copy.deepcopy(self.perturbations),
            policy_snapshot=dict(policy_snapshot),
            rivalry_events=[dict(event) for event in rivalry_events],
            stability_metrics=dict(stability_metrics),
            promotion_state=dict(promotion_state or {}),
            policy_metadata=dict(policy_metadata),
            queues=copy.deepcopy(self.queue_state),
            running_affordances=copy.deepcopy(self.running_affordances),
            relationship_snapshot=copy.deepcopy(self.relationship_snapshot),
            relationship_metrics=dict(self.relationship_metrics),
            employment_snapshot=copy.deepcopy(self.employment_snapshot),
            queue_affinity_metrics=dict(self.queue_affinity_metrics),
            economy_snapshot=copy.deepcopy(self.economy_snapshot),
            anneal_context=dict(anneal_context),
        )
        return ObservationEnvelope(
            tick=self.state.tick,
            agents=agents_dto,
            global_context=global_dto,
            actions=dict(actions),
            terminated=dict(terminated),
            termination_reasons=dict(termination_reasons),
        )


class _DummyLifecycleManager:
    def finalize(self, world: _DummyWorldState, tick: int, terminated: Mapping[str, bool]) -> None:
        _ = (world, tick, terminated)


class _DummyPerturbationScheduler:
    def __init__(self) -> None:
        self._state: dict[str, Any] = {"pending": [], "active": []}

    def latest_state(self) -> Mapping[str, Any]:
        return copy.deepcopy(self._state)

    def reset_state(self) -> None:  # pragma: no cover - deterministic
        self._state = {"pending": [], "active": []}

    def import_state(self, payload: Mapping[str, Any]) -> None:
        self._state = copy.deepcopy(dict(payload))

    def set_rng_state(self, _state: object) -> None:  # pragma: no cover - deterministic
        return

    def pending_count(self) -> int:
        pending = self._state.get("pending", [])
        return len(pending) if isinstance(pending, (list, tuple, set)) else 0

    def active_count(self) -> int:
        active = self._state.get("active", [])
        return len(active) if isinstance(active, (list, tuple, set)) else 0


class _DummyRewardEngine:
    def __init__(self) -> None:
        self._latest_breakdown: dict[str, dict[str, float]] = {}

    def compute(
        self,
        world: _DummyWorldState,
        terminated: Mapping[str, bool],
        termination_reasons: Mapping[str, str],
    ) -> dict[str, float]:
        _ = (terminated, termination_reasons)
        rewards = {agent_id: 0.0 for agent_id in world.agents}
        self._latest_breakdown = {agent_id: {"base": 0.0} for agent_id in world.agents}
        return rewards

    def latest_reward_breakdown(self) -> Mapping[str, Mapping[str, float]]:
        return copy.deepcopy(self._latest_breakdown)

    def latest_social_events(self) -> list[dict[str, Any]]:
        return []


class _DummyStabilityMonitor:
    def __init__(self) -> None:
        self._latest: dict[str, Any] = {}

    def track(self, **kwargs: Any) -> None:
        self._latest = {key: copy.deepcopy(value) for key, value in kwargs.items()}

    def latest_metrics(self) -> Mapping[str, Any]:
        return copy.deepcopy(self._latest)

    def import_state(self, payload: Mapping[str, Any]) -> None:  # pragma: no cover - deterministic
        self._latest = copy.deepcopy(dict(payload))

    def reset_state(self) -> None:  # pragma: no cover - deterministic
        self._latest = {}


class _DummyPromotionManager:
    def __init__(self) -> None:
        self._snapshot: dict[str, Any] = {"level": 0}

    def update_from_metrics(self, metrics: Mapping[str, Any], tick: int) -> None:
        _ = tick
        self._snapshot = {"metrics": dict(metrics)}

    def snapshot(self) -> Mapping[str, Any]:
        return copy.deepcopy(self._snapshot)

    def import_state(self, payload: Mapping[str, Any]) -> None:  # pragma: no cover
        self._snapshot = copy.deepcopy(dict(payload))

    def reset(self) -> None:  # pragma: no cover - deterministic
        self._snapshot = {"level": 0}


class _DummyEmbeddingAllocator:
    def metrics(self) -> Mapping[str, float]:
        return {}


class _DummyWorldAdapter:
    def __init__(self) -> None:
        self.embedding_allocator = _DummyEmbeddingAllocator()

    def consume_rivalry_events(self) -> list[Mapping[str, Any]]:
        return []

    def running_affordances_snapshot(self) -> Mapping[str, Any]:
        return {}

    def relationships_snapshot(self) -> Mapping[str, Any]:
        return {}


class _DummyPolicyHarness:
    def __init__(self, agent_ids: Sequence[str]) -> None:
        self._agents = tuple(agent_ids)
        self._anneal_ratio: float | None = None
        self._ctx_reset_callback: Callable[[str], None] | None = None
        self._world_supplier: Callable[[], Any] | None = None

    def bind_world_supplier(self, supplier: Callable[[], Any]) -> None:
        self._world_supplier = supplier

    def register_ctx_reset_callback(self, callback: Callable[[str], None]) -> None:
        self._ctx_reset_callback = callback

    def enable_anneal_blend(self, _enabled: bool) -> None:  # pragma: no cover - deterministic
        return

    def on_episode_start(self, _agents: Sequence[str]) -> None:  # pragma: no cover
        return

    def supports_observation_envelope(self) -> bool:
        return True

    def decide(self, world: Any, tick: int, *, envelope: ObservationEnvelope) -> dict[str, dict[str, Any]]:
        _ = (world, tick, envelope)
        return {agent_id: {} for agent_id in self._agents}

    def post_step(self, rewards: Mapping[str, float], terminated: Mapping[str, bool]) -> None:
        _ = (rewards, terminated)

    def latest_policy_snapshot(self) -> Mapping[str, Any]:
        return {"hash": "dummy", "agents": list(self._agents)}

    def possessed_agents(self) -> Sequence[str]:
        return self._agents

    def consume_option_switch_counts(self) -> Mapping[str, int]:
        return {}

    def flush_transitions(self, *, envelope: ObservationEnvelope) -> Sequence[dict[str, Any]]:
        _ = envelope
        return []

    def active_policy_hash(self) -> str:
        return "dummy"

    def current_anneal_ratio(self) -> float | None:
        return self._anneal_ratio

    def set_anneal_ratio(self, ratio: float | None) -> None:
        self._anneal_ratio = ratio

    def enable_autorestart(self, _enabled: bool) -> None:  # pragma: no cover - deterministic
        return

    def reset_state(self) -> None:  # pragma: no cover - deterministic
        return

    def anneal_context(self) -> Mapping[str, Any]:
        return {}

    def on_episode_end(self) -> None:  # pragma: no cover - deterministic
        return


class _LoopDummyWorldRuntime:
    def __init__(self, world: _DummyWorldState, context: _DummyWorldContext) -> None:
        self._world = world
        self.context = context
        self._queued_console: list[ConsoleCommandEnvelope] = []
        self._last_actions: dict[str, Any] = {}
        self._adapter = _DummyWorldAdapter()
        self.config_id = world.config_id

    def bind_world(self, world: _DummyWorldState) -> None:
        self._world = world

    def bind_world_adapter(self, adapter: _DummyWorldAdapter) -> None:
        self._adapter = adapter

    def queue_console(self, operations: Iterable[ConsoleCommandEnvelope]) -> None:
        self._queued_console.extend(operations)

    def reset(self, seed: int | None = None) -> None:  # pragma: no cover - deterministic
        _ = seed
        self._queued_console.clear()
        self._world.tick = 0

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable[ConsoleCommandEnvelope] | None = None,
        action_provider: Callable[[Any, int], Mapping[str, Any]] | None = None,
        policy_actions: Mapping[str, Any] | None = None,
    ):
        self._world.tick = tick
        queued = list(console_operations or self._queued_console)
        self._queued_console.clear()
        if action_provider is not None:
            actions = dict(action_provider(self._world, tick))
        else:
            actions = {}
        if policy_actions:
            actions.update(policy_actions)
        self._last_actions = actions
        terminated = {agent_id: False for agent_id in self._world.agents}
        return RuntimeStepResult(
            console_results=[],
            events=[{"tick": tick, "queued_console": len(queued)}],
            actions=actions,
            terminated=terminated,
            termination_reasons={},
        )

    def agents(self) -> Iterable[str]:
        return tuple(self._world.agents.keys())

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        selected = agent_ids if agent_ids is not None else self._world.agents.keys()
        return {agent_id: {"tick": self._world.tick} for agent_id in selected}

    def apply_actions(self, actions: Mapping[str, Any]) -> None:  # pragma: no cover - deterministic
        self._last_actions = dict(actions)

    def snapshot(self) -> SnapshotState:
        return SnapshotState(config_id=self._world.config_id, tick=self._world.tick)

    def transport_status(self) -> Mapping[str, Any]:  # pragma: no cover - deterministic
        return {"provider": "dummy", "queue_length": 0, "dropped_messages": 0}


@dataclass(slots=True)
class DummyLoopHarness:
    loop: SimulationLoop
    telemetry_sink: DummyTelemetrySink
    runtime: _LoopDummyWorldRuntime
    context: _DummyWorldContext
    world: _DummyWorldState
    policy: _DummyPolicyHarness


def build_dummy_loop(
    config: Any,
    *,
    agent_ids: Sequence[str] = ("agent_a", "agent_b"),
) -> DummyLoopHarness:
    """Construct a simulation loop wired with dummy providers for fast smokes."""

    loop = SimulationLoop(config)

    world_state = _DummyWorldState(agent_ids)
    context = _DummyWorldContext(world_state)
    runtime = _LoopDummyWorldRuntime(world_state, context)
    lifecycle = _DummyLifecycleManager()
    perturbations = _DummyPerturbationScheduler()
    reward_engine = _DummyRewardEngine()
    stability_monitor = _DummyStabilityMonitor()
    promotion_manager = _DummyPromotionManager()
    policy_harness = _DummyPolicyHarness(agent_ids)
    telemetry_sink = DummyTelemetrySink()
    telemetry_publisher = TelemetryPublisher(config=config)

    def _world_builder(_loop: SimulationLoop) -> WorldComponents:
        _loop._world_context = context  # ensure cached context
        return WorldComponents(
            world=world_state,
            lifecycle=lifecycle,
            perturbations=perturbations,
            observation_service=context.observation_service,
            world_port=runtime,
            ticks_per_day=1440,
            provider="dummy",
        )

    def _policy_builder(_loop: SimulationLoop) -> PolicyComponents:
        return PolicyComponents(
            port=policy_harness,
            controller=policy_harness,
            decision_backend=policy_harness,
            provider="dummy",
        )

    def _telemetry_builder(_loop: SimulationLoop) -> TelemetryComponents:
        return TelemetryComponents(
            port=telemetry_sink,
            publisher=telemetry_publisher,
            provider="dummy",
        )

    loop.override_world_components(_world_builder)
    loop.override_policy_components(_policy_builder)
    loop.override_telemetry_components(_telemetry_builder)
    loop._build_components()

    loop.rewards = reward_engine
    loop.stability = stability_monitor
    loop.promotion = promotion_manager
    loop._world_adapter = _DummyWorldAdapter()
    runtime.bind_world_adapter(loop._world_adapter)
    return DummyLoopHarness(
        loop=loop,
        telemetry_sink=telemetry_sink,
        runtime=runtime,
        context=context,
        world=world_state,
        policy=policy_harness,
    )


__all__ = ["build_dummy_loop", "DummyLoopHarness"]
