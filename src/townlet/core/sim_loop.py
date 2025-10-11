"""Top-level simulation loop wiring.

The loop follows the order defined in docs/HIGH_LEVEL_DESIGN.md and delegates to
feature-specific subsystems. Each dependency is a thin façade around the actual
implementation, allowing tests to substitute stubs while the real code evolves.
"""

from __future__ import annotations

import copy
import hashlib
import logging
import random
import time
import traceback
from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path
from typing import Any

from townlet.config import AffordanceRuntimeConfig, SimulationConfig
from townlet.core.interfaces import (
    PolicyBackendProtocol,
    TelemetrySinkProtocol,
    WorldRuntimeProtocol,
)
from townlet.factories import create_policy, create_telemetry, create_world
from townlet.lifecycle.manager import LifecycleManager
from townlet.observations.builder import ObservationBuilder
from townlet.rewards.engine import RewardEngine
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.snapshots import (
    SnapshotManager,
    apply_snapshot_to_telemetry,
    apply_snapshot_to_world,
    snapshot_from_world,
)
from townlet.stability.monitor import StabilityMonitor
from townlet.stability.promotion import PromotionManager
from townlet.utils import decode_rng_state
from townlet.world.affordances import AffordanceRuntimeContext, DefaultAffordanceRuntime
from townlet.world.core import WorldContext, WorldRuntimeAdapter
from townlet.world.dto import build_observation_envelope
from townlet.world.dto.observation import ObservationEnvelope
from townlet.world.grid import WorldState
from townlet.policy.runner import PolicyRuntime
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.orchestration import ConsoleRouter, HealthMonitor, PolicyController
from townlet.world.observations.context import (
    agent_context as observation_agent_context,
)

logger = logging.getLogger(__name__)


@dataclass
class SimulationLoopHealth:
    """Tracks loop health information for telemetry and debugging."""

    last_tick: int = 0
    last_duration_ms: float = 0.0
    last_error: str | None = None
    last_traceback: str | None = None
    failure_count: int = 0
    last_failure_ts: float | None = None
    last_snapshot_path: str | None = None


class SimulationLoopError(RuntimeError):
    """Raised when the simulation loop encounters an unrecoverable failure."""

    def __init__(self, tick: int, message: str, *, cause: BaseException | None = None) -> None:
        super().__init__(f"{message} (tick={tick})")
        self.tick = tick
        if cause is not None:
            self.__cause__ = cause


@dataclass
class TickArtifacts:
    """Collects per-tick data for logging and testing."""

    envelope: ObservationEnvelope
    rewards: dict[str, float]


class SimulationLoop:
    """Orchestrates the Townlet simulation tick-by-tick."""

    def __init__(
        self,
        config: SimulationConfig,
        *,
        affordance_runtime_factory: Callable[
            [WorldState, AffordanceRuntimeContext],
            DefaultAffordanceRuntime,
        ]
        | None = None,
        world_provider: str | None = None,
        world_options: Mapping[str, object] | None = None,
        policy_provider: str | None = None,
        policy_options: Mapping[str, object] | None = None,
        telemetry_provider: str | None = None,
        telemetry_options: Mapping[str, object] | None = None,
    ) -> None:
        self.config = config
        self.config.register_snapshot_migrations()
        self._runtime_config: AffordanceRuntimeConfig = self.config.affordances.runtime
        if affordance_runtime_factory is not None:
            self._affordance_runtime_factory = affordance_runtime_factory
        else:
            self._affordance_runtime_factory = self._load_affordance_runtime_factory(self._runtime_config)
        self.runtime: WorldRuntimeProtocol | None = None
        self._world_provider = (world_provider or "default").strip()
        self._world_provider_locked = world_provider is not None
        self._world_options = dict(world_options or {})
        self._world_options_locked = world_options is not None
        self._policy_provider = (policy_provider or "scripted").strip()
        self._policy_provider_locked = policy_provider is not None
        self._policy_options = dict(policy_options or {})
        self._policy_options_locked = policy_options is not None
        self._telemetry_provider = (telemetry_provider or "stdout").strip()
        self._telemetry_provider_locked = telemetry_provider is not None
        self._telemetry_options = dict(telemetry_options or {})
        self._telemetry_options_locked = telemetry_options is not None
        self._runtime_variant: str = "facade"
        self._resolved_providers: dict[str, str] = {}
        self._failure_handlers: list[Callable[[SimulationLoop, int, BaseException], None]] = []
        self._health = SimulationLoopHealth()
        self._world_adapter: WorldRuntimeAdapter | None = None
        self._world_port = None
        self._policy_port = None
        self._telemetry_port = None
        self._policy_controller: PolicyController | None = None
        self._console_router: ConsoleRouter | None = None
        self._health_monitor: HealthMonitor | None = None
        self._rivalry_history: list[dict[str, object]] = []
        self._policy_observation_envelope = None
        self._last_policy_metadata_event: dict[str, object] | None = None
        self._last_policy_possession_agents: tuple[str, ...] | None = None
        self._last_policy_anneal_event: dict[str, object] | None = None
        self._last_transport_status: dict[str, object] = {
            "provider": "port",
            "queue_length": 0,
            "dropped_messages": 0,
            "last_flush_duration_ms": None,
            "worker_alive": True,
            "worker_error": None,
            "worker_restart_count": 0,
            "payloads_flushed_total": 0,
            "bytes_flushed_total": 0,
            "auth_enabled": False,
        }
        self._apply_runtime_overrides_from_config()
        self._build_components()

    def __setattr__(self, name: str, value: object) -> None:  # pragma: no cover - delegation glue
        super().__setattr__(name, value)
        if name == "world":
            runtime = getattr(self, "runtime", None)
            if isinstance(value, WorldState):
                super().__setattr__("_world_adapter", WorldRuntimeAdapter(value))
                if isinstance(runtime, WorldRuntimeProtocol):
                    runtime.bind_world(value)
                    bind_adapter = getattr(runtime, "bind_world_adapter", None)
                    if callable(bind_adapter):  # pragma: no cover - delegation glue
                        bind_adapter(self._world_adapter)

    def _build_components(self) -> None:
        """Instantiate runtime dependencies based on the simulation config."""

        previous_telemetry = getattr(self, "telemetry", None)
        if previous_telemetry is not None:
            close = getattr(previous_telemetry, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:  # pragma: no cover - best effort
                    logger.debug("Failed to close previous telemetry sink", exc_info=True)
        self._rng_world = random.Random(self._derive_seed("world"))
        self._rng_events = random.Random(self._derive_seed("events"))
        self._rng_policy = random.Random(self._derive_seed("policy"))
        self._rivalry_history = []
        self._last_policy_metadata_event = None
        self._last_policy_possession_agents = None
        self._last_policy_anneal_event = None
        self.world = WorldState.from_config(
            self.config,
            rng=self._rng_world,
            affordance_runtime_factory=self._affordance_runtime_factory,
            affordance_runtime_config=self._runtime_config,
        )
        self.lifecycle = LifecycleManager(config=self.config)
        self.perturbations = PerturbationScheduler(
            config=self.config,
            rng=self._rng_events,
        )
        self._observation_builder = ObservationBuilder(config=self.config)
        context = getattr(self.world, "context", None)
        if context is not None and getattr(context, "observation_service", None) is None:
            context.observation_service = self._observation_builder
        policy_kwargs = {"config": self.config, **self._policy_options}
        policy_backend = PolicyRuntime(**policy_kwargs)
        self._policy_port = create_policy(
            provider=self._policy_provider,
            backend=policy_backend,
        )
        backend_for_controller = getattr(self._policy_port, "backend", policy_backend)
        self.policy = backend_for_controller
        self._policy_controller = PolicyController(backend=backend_for_controller, port=self._policy_port)
        if self._policy_controller is not None:
            self._policy_controller.bind_world_supplier(lambda: self.world)
        self._resolved_providers["policy"] = self._policy_provider
        controller = self._policy_controller
        if controller is not None:
            controller.register_ctx_reset_callback(self.world.request_ctx_reset)
            if self.config.training.anneal_enable_policy_blend:
                controller.enable_anneal_blend(True)
        else:  # pragma: no cover - defensive
            self.policy.register_ctx_reset_callback(self.world.request_ctx_reset)
            if self.config.training.anneal_enable_policy_blend:
                self.policy.enable_anneal_blend(True)
        self.rewards = RewardEngine(config=self.config)
        telemetry_kwargs = {"config": self.config, **self._telemetry_options}
        telemetry_publisher = TelemetryPublisher(**telemetry_kwargs)
        self._telemetry_port = create_telemetry(
            provider=self._telemetry_provider,
            publisher=telemetry_publisher,
        )
        self.telemetry = telemetry_publisher
        self._resolved_providers["telemetry"] = self._telemetry_provider
        self.stability = StabilityMonitor(config=self.config)
        log_path = Path("logs/promotion_history.jsonl")
        self.promotion = PromotionManager(config=self.config, log_path=log_path)
        self.tick = 0
        cfg = getattr(self.config, "observations_config", None)
        if cfg is not None and getattr(cfg, "hybrid", None) is not None:
            ticks_per_day = getattr(cfg.hybrid, "time_ticks_per_day", 1440)
        else:
            ticks_per_day = getattr(self._observation_builder.hybrid_cfg, "time_ticks_per_day", 1440)
        self._ticks_per_day = max(1, int(ticks_per_day))
        self._world_port = create_world(
            provider=self._world_provider,
            world=self.world,
            lifecycle=self.lifecycle,
            perturbations=self.perturbations,
            ticks_per_day=self._ticks_per_day,
            world_kwargs=self._world_options,
            observation_builder=self._observation_builder,
        )
        self.runtime = self._world_port
        self._resolved_providers["world"] = self._world_provider
        self._console_router = ConsoleRouter(
            world=self._world_port,
            telemetry=self._telemetry_port,
        )
        monitor_config = getattr(self.config, "monitor", None)
        monitor_window = getattr(monitor_config, "window", 100) if monitor_config is not None else 100
        self._health_monitor = HealthMonitor(window=monitor_window)
        if self._world_adapter is not None:
            bind_adapter = getattr(self.runtime, "bind_world_adapter", None)
            if callable(bind_adapter):
                bind_adapter(self._world_adapter)
        self._runtime_variant = "facade"
        self.telemetry.set_runtime_variant(self._runtime_variant)
        self._health = SimulationLoopHealth(last_tick=self.tick)
        # Seed an initial DTO envelope so policy backends can operate before the
        # first tick produces a DTO envelope.
        bootstrap_envelope = self._build_bootstrap_policy_envelope()
        self._set_policy_observation_envelope(bootstrap_envelope)

    @property
    def health(self) -> SimulationLoopHealth:
        """Return a snapshot of the loop health state."""

        return SimulationLoopHealth(**asdict(self._health))

    @property
    def provider_info(self) -> dict[str, str]:
        """Expose the currently resolved providers for world, policy, and telemetry."""

        return dict(self._resolved_providers)

    @property
    def world_context(self) -> WorldContext:
        """Return a façade over the active world services."""

        return self.world.context

    @property
    def world_adapter(self) -> WorldRuntimeAdapter:
        """Return the read-only adapter for the active world instance."""

        adapter = self._world_adapter
        if adapter is None:
            adapter = WorldRuntimeAdapter(self.world)
            super().__setattr__("_world_adapter", adapter)
        return adapter

    @property
    def policy_controller(self) -> PolicyController | None:
        """Expose the policy controller facade (transitional)."""

        return self._policy_controller

    def register_failure_handler(self, handler: Callable[[SimulationLoop, int, BaseException], None]) -> None:
        """Register a callback that runs whenever the loop records a failure."""

        self._failure_handlers.append(handler)

    def reset(self) -> None:
        """Reset the simulation loop to its initial state."""
        self._build_components()

    def set_anneal_ratio(self, ratio: float | None) -> None:
        controller = self._policy_controller
        if controller is not None:
            controller.set_anneal_ratio(ratio)
        else:  # pragma: no cover - defensive
            self.policy.set_anneal_ratio(ratio)

    # ------------------------------------------------------------------
    # Snapshot helpers
    # ------------------------------------------------------------------
    def save_snapshot(self, root: Path | None = None) -> Path:
        """Persist the current world relationships and tick to ``root``."""

        target_root = Path(root).expanduser() if root is not None else self.config.snapshot_root()
        manager = SnapshotManager(root=target_root)
        controller = self._policy_controller
        policy_hash = controller.active_policy_hash() if controller is not None else self.policy.active_policy_hash()
        anneal_ratio = (
            controller.current_anneal_ratio()
            if controller is not None
            else self.policy.current_anneal_ratio()
        )
        identity_payload = self.config.build_snapshot_identity(
            policy_hash=policy_hash,
            runtime_observation_variant=self.config.observation_variant,
            runtime_anneal_ratio=anneal_ratio,
        )
        self.telemetry.update_policy_identity(identity_payload)
        state = snapshot_from_world(
            self.config,
            self.world,
            lifecycle=self.lifecycle,
            telemetry=self.telemetry,
            perturbations=self.perturbations,
            stability=self.stability,
            promotion=self.promotion,
            rng_streams={
                "world": self._rng_world,
                "events": self._rng_events,
                "policy": self._rng_policy,
            },
            identity=identity_payload,
        )
        return manager.save(state)

    def load_snapshot(self, path: Path) -> None:
        """Restore world relationships and tick from the snapshot at ``path``."""

        manager = SnapshotManager(root=path.parent)
        state = manager.load(
            path,
            self.config,
            allow_migration=self.config.snapshot.migrations.auto_apply,
            allow_downgrade=self.config.snapshot.guardrails.allow_downgrade,
            require_exact_config=self.config.snapshot.guardrails.require_exact_config,
        )
        controller = self._policy_controller
        if controller is not None:
            controller.reset_state()
        else:  # pragma: no cover - defensive
            self.policy.reset_state()
        self.perturbations.reset_state()
        apply_snapshot_to_world(
            self.world,
            state,
            lifecycle=self.lifecycle,
        )
        apply_snapshot_to_telemetry(self.telemetry, state)
        self.perturbations.import_state(state.perturbations)
        if state.stability:
            self.stability.import_state(state.stability)
        else:
            self.stability.reset_state()
        if state.promotion:
            self.promotion.import_state(state.promotion)
        else:
            self.promotion.reset()
        stability_metrics = self.stability.latest_metrics()
        stability_metrics["promotion_state"] = self.promotion.snapshot()
        if self._telemetry_port is not None:
            self._telemetry_port.emit_event("stability.metrics", stability_metrics)
        else:  # pragma: no cover - defensive
            self.telemetry.emit_event("stability.metrics", stability_metrics)
        self.tick = state.tick
        rng_streams = dict(state.rng_streams)
        if state.rng_state and "world" not in rng_streams:
            rng_streams["world"] = state.rng_state
        if world_rng_str := rng_streams.get("world"):
            world_state = decode_rng_state(world_rng_str)
            self.world.set_rng_state(world_state)
        if events_rng_str := rng_streams.get("events"):
            events_state = decode_rng_state(events_rng_str)
            self.perturbations.set_rng_state(events_state)
        if policy_rng_str := rng_streams.get("policy"):
            policy_state = decode_rng_state(policy_rng_str)
            self._rng_policy.setstate(policy_state)

    def run(self, max_ticks: int | None = None) -> Iterable[TickArtifacts]:
        """Run the loop until ``max_ticks`` or indefinitely."""
        while max_ticks is None or self.tick < max_ticks:
            yield self.step()

    def run_for_ticks(self, max_ticks: int, *, collect: bool = False) -> list[TickArtifacts]:
        """Advance the simulation by ``max_ticks`` and optionally collect artifacts."""

        if max_ticks < 0:
            raise ValueError("max_ticks must be non-negative")
        artifacts: list[TickArtifacts] = []
        for _ in range(max_ticks):
            result = self.step()
            if collect:
                artifacts.append(result)
        return artifacts

    def run_for(self, max_ticks: int) -> None:
        """Execute exactly ``max_ticks`` iterations of the simulation loop."""

        self.run_for_ticks(max_ticks, collect=False)

    def step(self) -> TickArtifacts:
        """Advance the simulation loop by one tick and return the DTO envelope and rewards."""
        tick_start = time.perf_counter()
        next_tick = self.tick + 1
        console_ops = list(self.telemetry.drain_console_buffer())
        if self._console_router is not None:
            for command in console_ops:
                try:
                    self._console_router.enqueue(command)
                except ValueError:
                    logger.warning("Ignoring invalid console command payload: %r", command)
        runtime = self.runtime
        if runtime is None:  # pragma: no cover - defensive guard
            raise RuntimeError("WorldRuntime is not initialised")

        controller = self._policy_controller
        try:
            self.tick = next_tick
            runtime.queue_console(console_ops)

            if self._policy_observation_envelope is None:
                bootstrap_envelope = self._build_bootstrap_policy_envelope()
                self._set_policy_observation_envelope(bootstrap_envelope)

            def _action_provider(world: WorldState, current_tick: int) -> Mapping[str, object]:
                envelope = self._ensure_policy_envelope()
                if controller is not None:
                    return controller.decide(
                        world,
                        current_tick,
                        envelope=envelope,
                    )
                return self.policy.decide(
                    world,
                    current_tick,
                    envelope=envelope,
                )

            runtime_result = runtime.tick(
                tick=self.tick,
                action_provider=_action_provider,
            )
            console_results = runtime_result.console_results
            events = runtime_result.events
            terminated = runtime_result.terminated
            termination_reasons = runtime_result.termination_reasons
            if self._console_router is not None:
                self._console_router.run_pending(tick=self.tick)

            if self._telemetry_port is not None:
                for result in console_results:
                    self._telemetry_port.emit_event("console.result", result.to_dict())
            else:  # pragma: no cover - defensive
                for result in console_results:
                    self.telemetry.emit_event("console.result", result.to_dict())
            episode_span = self._ticks_per_day
            for snapshot in self.world.agents.values():
                snapshot.episode_tick = (snapshot.episode_tick + 1) % episode_span
            rewards = self.rewards.compute(self.world, terminated, termination_reasons)
            reward_breakdown = self.rewards.latest_reward_breakdown()
            if controller is not None:
                controller.post_step(rewards, terminated)
            else:  # pragma: no cover - defensive
                self.policy.post_step(rewards, terminated)
            if controller is not None:
                policy_snapshot = controller.latest_policy_snapshot()
                possessed_agents = controller.possessed_agents()
                option_switch_counts = controller.consume_option_switch_counts()
            else:  # pragma: no cover - defensive fallback
                policy_snapshot = self.policy.latest_policy_snapshot()
                possessed_agents = self.policy.possessed_agents()
                option_switch_counts = self.policy.consume_option_switch_counts()
            hunger_levels = {agent_id: float(snapshot.needs.get("hunger", 1.0)) for agent_id, snapshot in self.world.agents.items()}
            stability_inputs = {
                "hunger_levels": hunger_levels,
                "option_switch_counts": option_switch_counts,
                "reward_samples": dict(rewards),
            }
            perturbation_state = self.perturbations.latest_state()
            policy_hash = controller.active_policy_hash() if controller is not None else self.policy.active_policy_hash()
            anneal_ratio = controller.current_anneal_ratio() if controller is not None else self.policy.current_anneal_ratio()
            policy_identity = self.config.build_snapshot_identity(
                policy_hash=policy_hash,
                runtime_observation_variant=self.config.observation_variant,
                runtime_anneal_ratio=anneal_ratio,
            )
            possessed_agents_list = sorted(str(agent) for agent in possessed_agents)
            policy_metadata = {
                "identity": policy_identity,
                "possessed_agents": possessed_agents_list,
                "option_switch_counts": {
                    str(agent): int(count)
                    for agent, count in sorted(option_switch_counts.items())
                },
                "anneal_ratio": anneal_ratio,
            }
            adapter = self.world_adapter
            queue_metrics = self._collect_queue_metrics()
            embedding_metrics = self._collect_embedding_metrics(adapter)
            job_snapshot = self._collect_job_snapshot(adapter)
            employment_metrics = self._collect_employment_metrics()
            rivalry_events = self._collect_rivalry_events(adapter)
            snapshot_for_health: dict[str, Any] = {
                "tick": self.tick,
                "events": list(events),
            }
            queues_snapshot: dict[str, object] = {}
            try:
                queue_export = self.world.queue_manager.export_state()
                if isinstance(queue_export, dict):
                    queues_snapshot = queue_export
                    queues_payload = queue_export.get("queues", {})
                    if isinstance(queues_payload, dict):
                        queue_length = float(
                            sum(len(entries or []) for entries in queues_payload.values())
                        )
                    else:
                        queue_length = 0.0
                else:  # pragma: no cover - defensive
                    queue_length = 0.0
            except Exception:  # pragma: no cover - defensive
                queue_length = 0.0
                queues_snapshot = {}
            snapshot_for_health["metrics"] = {"queue_length": queue_length}
            if self._health_monitor is not None and self._telemetry_port is not None:
                self._health_monitor.on_tick(snapshot_for_health, self._telemetry_port)
            self.stability.track(
                tick=self.tick,
                rewards=rewards,
                terminated=terminated,
                queue_metrics=queue_metrics,
                embedding_metrics=embedding_metrics,
                job_snapshot=job_snapshot,
                events=events,
                employment_metrics=employment_metrics,
                hunger_levels=hunger_levels,
                option_switch_counts=option_switch_counts,
                rivalry_events=rivalry_events,
            )
            stability_metrics = self.stability.latest_metrics()
            self.promotion.update_from_metrics(stability_metrics, tick=self.tick)
            promotion_state = self.promotion.snapshot()
            stability_metrics["promotion_state"] = promotion_state
            anneal_context = {}
            try:
                anneal_context = self.policy.anneal_context()
            except Exception:  # pragma: no cover - defensive
                logger.debug("anneal_context_unavailable", exc_info=True)

            if self._telemetry_port is not None:
                self._emit_policy_events(
                    policy_metadata=policy_metadata,
                    possessed_agents=possessed_agents_list,
                    anneal_ratio=anneal_ratio,
                    anneal_context=anneal_context,
                )

            dto_envelope = self._try_context_observe(
                actions=runtime_result.actions,
                terminated=terminated,
                termination_reasons=termination_reasons,
                queue_metrics=queue_metrics,
                rewards=rewards,
                reward_breakdown=reward_breakdown,
                perturbations=perturbation_state,
                policy_snapshot=policy_snapshot,
                policy_metadata=policy_metadata,
                rivalry_events=rivalry_events,
                stability_metrics=stability_metrics,
                promotion_state=promotion_state,
                anneal_context=anneal_context,
            )

            if dto_envelope is None:
                observation_batch = self._observation_builder.build_batch(self.world_adapter, terminated)
                running_affordances = adapter.running_affordances_snapshot()
                relationship_snapshot = adapter.relationships_snapshot()
                relationship_metrics = adapter.relationship_metrics_snapshot()
                agent_snapshots_map = dict(adapter.agent_snapshots_view())
                agent_contexts = {
                    agent: observation_agent_context(adapter, agent)
                    for agent in agent_snapshots_map.keys()
                }
                queue_affinity_metrics = self._collect_queue_affinity_metrics()
                economy_snapshot = self._collect_economy_snapshot()

                dto_envelope = build_observation_envelope(
                    tick=self.tick,
                    observations=observation_batch,
                    actions=runtime_result.actions,
                    terminated=terminated,
                    termination_reasons=termination_reasons,
                    queue_metrics=queue_metrics,
                    rewards=rewards,
                    reward_breakdown=reward_breakdown,
                    perturbations=perturbation_state,
                    policy_snapshot=policy_snapshot,
                    policy_metadata=policy_metadata,
                    rivalry_events=rivalry_events,
                    stability_metrics=stability_metrics,
                    promotion_state=promotion_state,
                    rng_seed=getattr(self.world, "rng_seed", None),
                    queues=queues_snapshot,
                    running_affordances=running_affordances,
                    relationship_snapshot=relationship_snapshot,
                    relationship_metrics=relationship_metrics,
                    agent_snapshots=agent_snapshots_map,
                    job_snapshot=job_snapshot,
                    queue_affinity_metrics=queue_affinity_metrics,
                    employment_snapshot=employment_metrics,
                    economy_snapshot=economy_snapshot,
                    anneal_context=anneal_context,
                    agent_contexts=agent_contexts,
                )
            else:
                observation_batch = {
                    agent.agent_id: agent.metadata
                    for agent in dto_envelope.agents
                }
            if controller is not None:
                frames = controller.flush_transitions(envelope=dto_envelope)
            else:  # pragma: no cover - defensive fallback
                frames = self.policy.flush_transitions(envelope=dto_envelope)
            frames = list(frames or [])
            if frames:
                anneal_ctx = dto_envelope.global_context.anneal_context or {}
                metadata_copy = dict(policy_metadata)
                for frame in frames:
                    frame.setdefault("anneal_context", anneal_ctx)
                    meta = frame.setdefault("metadata", {})
                    if isinstance(meta, dict):
                        meta.update(metadata_copy)
            self._set_policy_observation_envelope(dto_envelope)
            if self._telemetry_port is not None:
                tick_event_payload = {
                    "tick": self.tick,
                    "world": self.world,
                    "rewards": rewards,
                    "events": events,
                    "policy_snapshot": policy_snapshot,
                    "kpi_history": True,
                    "reward_breakdown": reward_breakdown,
                    "stability_inputs": stability_inputs,
                    "perturbations": perturbation_state,
                    "policy_identity": policy_identity,
                    "policy_metadata": policy_metadata,
                    "possessed_agents": possessed_agents_list,
                    "social_events": self.rewards.latest_social_events(),
                    "runtime_variant": self._runtime_variant,
                    "observations_dto": dto_envelope.model_dump(by_alias=True),
                }
                self._telemetry_port.emit_event("loop.tick", tick_event_payload)
            if self._telemetry_port is not None:
                self._telemetry_port.emit_event("stability.metrics", stability_metrics)
            else:  # pragma: no cover - defensive
                self.telemetry.emit_event("stability.metrics", stability_metrics)
            self.lifecycle.finalize(self.world, tick=self.tick, terminated=terminated)
            duration_ms = (time.perf_counter() - tick_start) * 1000.0
            transport_status = self._build_transport_status(queue_length=len(console_results))
            health_payload = {
                "tick": self.tick,
                "status": "ok",
                "tick_duration_ms": duration_ms,
                "failure_count": self._health.failure_count,
                "telemetry_queue": transport_status.get("queue_length", 0),
                "telemetry_dropped": transport_status.get("dropped_messages", 0),
                "telemetry_flush_ms": transport_status.get("last_flush_duration_ms"),
                "telemetry_worker_alive": bool(transport_status.get("worker_alive", False)),
                "telemetry_worker_error": transport_status.get("worker_error"),
                "telemetry_worker_restart_count": transport_status.get("worker_restart_count", 0),
                "telemetry_console_auth_enabled": bool(transport_status.get("auth_enabled", False)),
                "telemetry_payloads_total": transport_status.get("payloads_flushed_total", 0),
                "telemetry_bytes_total": transport_status.get("bytes_flushed_total", 0),
                "perturbations_pending": self.perturbations.pending_count(),
                "perturbations_active": self.perturbations.active_count(),
                "employment_exit_queue": self.world.employment.exit_queue_length(),
            }
            if self._telemetry_port is not None:
                self._telemetry_port.emit_event("loop.health", health_payload)
            else:  # pragma: no cover - defensive
                self.telemetry.emit_event("loop.health", health_payload)
            if logger.isEnabledFor(logging.INFO):
                logger.info(
                    (
                        "tick_health tick=%s duration_ms=%.2f queue=%s dropped=%s "
                        "flush_ms=%s payloads_total=%s bytes_total=%s "
                        "perturbations_pending=%s perturbations_active=%s exit_queue=%s"
                    ),
                    self.tick,
                    duration_ms,
                    health_payload["telemetry_queue"],
                    health_payload["telemetry_dropped"],
                    health_payload["telemetry_flush_ms"],
                    health_payload["telemetry_payloads_total"],
                    health_payload["telemetry_bytes_total"],
                    health_payload["perturbations_pending"],
                    health_payload["perturbations_active"],
                    health_payload["employment_exit_queue"],
                )
            self._record_step_success(duration_ms)
            return TickArtifacts(envelope=dto_envelope, rewards=rewards)
        except Exception as exc:
            duration_ms = (time.perf_counter() - tick_start) * 1000.0
            self.tick = max(0, self.tick - 1)
            self._handle_step_failure(next_tick, duration_ms, exc)
            raise SimulationLoopError(next_tick, "Simulation step failed", cause=exc) from exc

    def _record_step_success(self, duration_ms: float) -> None:
        """Update health metadata after a successful tick."""
        self._health.last_tick = self.tick
        self._health.last_duration_ms = duration_ms
        self._health.last_error = None
        self._health.last_traceback = None
        self._health.last_snapshot_path = None

    def _handle_step_failure(self, tick: int, duration_ms: float, exc: BaseException) -> None:
        """Record failure metadata, emit telemetry, and invoke failure handlers."""
        error_message = f"{exc.__class__.__name__}: {exc}"
        self._health.last_tick = max(self._health.last_tick, tick)
        self._health.last_duration_ms = duration_ms
        self._health.last_error = error_message
        self._health.last_traceback = "".join(traceback.format_exception(exc.__class__, exc, exc.__traceback__))
        self._health.failure_count += 1
        self._health.last_failure_ts = time.time()
        snapshot_path: str | None = None
        if getattr(self.config.snapshot, "capture_on_failure", False):
            try:
                timestamp = time.strftime("%Y%m%dT%H%M%S")
                failure_root = self.config.snapshot_root() / "failures" / f"tick_{tick:09d}_{timestamp}"
                snapshot_path = str(self.save_snapshot(root=failure_root))
            except Exception:  # pragma: no cover - snapshot capture best effort
                logger.exception("Failed to capture failure snapshot")
                snapshot_path = None
        self._health.last_snapshot_path = snapshot_path
        transport_status = self._last_transport_status
        payload = {
            "tick": tick,
            "status": "error",
            "tick_duration_ms": duration_ms,
            "failure_count": self._health.failure_count,
            "error": error_message,
            "telemetry_queue": transport_status.get("queue_length", 0),
            "telemetry_dropped": transport_status.get("dropped_messages", 0),
        }
        if snapshot_path:
            payload["snapshot_path"] = snapshot_path
        if self._telemetry_port is not None:
            self._telemetry_port.emit_event("loop.failure", payload)
        else:  # pragma: no cover - defensive
            self.telemetry.emit_event("loop.failure", payload)
        for handler in list(self._failure_handlers):
            try:
                handler(self, tick, exc)
            except Exception:  # pragma: no cover - handlers should not break the loop
                logger.exception("Simulation loop failure handler raised")

    def _ensure_policy_envelope(self) -> "ObservationEnvelope":
        """Ensure a DTO envelope is available for policy decisions."""

        envelope = self._policy_observation_envelope
        if envelope is not None:
            return envelope
        bootstrap = self._build_bootstrap_policy_envelope()
        self._set_policy_observation_envelope(bootstrap)
        logger.debug("policy_envelope_bootstrap", extra={"tick": self.tick})
        return bootstrap

    def _set_policy_observation_envelope(self, envelope: "ObservationEnvelope") -> None:
        """Persist the current observation envelope and notify the backend."""

        self._policy_observation_envelope = envelope
        backend_consumer = getattr(self.policy, "update_observation_envelope", None)
        if callable(backend_consumer):
            backend_consumer(envelope)

    def _emit_policy_events(
        self,
        *,
        policy_metadata: Mapping[str, object],
        possessed_agents: Iterable[str],
        anneal_ratio: float | None,
        anneal_context: Mapping[str, object] | None,
    ) -> None:
        telemetry = self._telemetry_port
        if telemetry is None:
            return

        metadata_copy = copy.deepcopy(dict(policy_metadata))
        option_counts = metadata_copy.get("option_switch_counts")
        if isinstance(option_counts, Mapping):
            metadata_copy["option_switch_counts"] = {
                str(agent): int(count)
                for agent, count in sorted(option_counts.items())
            }
        sorted_agents = tuple(sorted(str(agent) for agent in possessed_agents))
        metadata_copy["possessed_agents"] = list(sorted_agents)
        metadata_payload: dict[str, object] = {
            "tick": self.tick,
            "provider": str(self._policy_provider),
            "metadata": metadata_copy,
        }
        if metadata_payload != self._last_policy_metadata_event:
            telemetry.emit_event("policy.metadata", metadata_payload)
            self._last_policy_metadata_event = copy.deepcopy(metadata_payload)

        if (
            self._last_policy_possession_agents is None
            or sorted_agents != self._last_policy_possession_agents
        ):
            possession_payload: dict[str, object] = {
                "tick": self.tick,
                "provider": str(self._policy_provider),
                "agents": list(sorted_agents),
                "possessed_agents": list(sorted_agents),
            }
            telemetry.emit_event("policy.possession", possession_payload)
            self._last_policy_possession_agents = sorted_agents

        context_payload: dict[str, object] = {}
        if isinstance(anneal_context, Mapping):
            context_payload = copy.deepcopy(dict(anneal_context))
        anneal_payload: dict[str, object] = {
            "tick": self.tick,
            "provider": str(self._policy_provider),
            "ratio": float(anneal_ratio) if anneal_ratio is not None else None,
            "context": context_payload,
        }
        if anneal_payload != self._last_policy_anneal_event:
            telemetry.emit_event("policy.anneal.update", anneal_payload)
            self._last_policy_anneal_event = copy.deepcopy(anneal_payload)

    def _build_bootstrap_policy_envelope(self) -> "ObservationEnvelope":
        """Build a DTO envelope from the current world when none has been recorded."""

        adapter = self.world_adapter
        observation_batch = self._observation_builder.build_batch(adapter, {})
        agent_ids = list(observation_batch.keys())
        terminated = {agent_id: False for agent_id in agent_ids}
        rewards = {agent_id: 0.0 for agent_id in agent_ids}
        reward_breakdown = {agent_id: {} for agent_id in agent_ids}
        queue_metrics = self._collect_queue_metrics()
        queue_affinity_metrics = self._collect_queue_affinity_metrics()
        employment_metrics = self._collect_employment_metrics()
        economy_snapshot = self._collect_economy_snapshot()
        job_snapshot = self._collect_job_snapshot(adapter)
        running_affordances = adapter.running_affordances_snapshot()
        relationship_snapshot = adapter.relationships_snapshot()
        relationship_metrics = adapter.relationship_metrics_snapshot()
        agent_snapshots_map = dict(adapter.agent_snapshots_view())
        agent_contexts = {
            agent: observation_agent_context(adapter, agent)
            for agent in agent_snapshots_map.keys()
        }
        perturbation_state = self.perturbations.latest_state()
        try:
            policy_snapshot = self.policy.latest_policy_snapshot()
        except Exception:  # pragma: no cover - defensive
            logger.debug("policy_snapshot_unavailable_bootstrap", exc_info=True)
            policy_snapshot = {}
        try:
            anneal_ratio = self.policy.current_anneal_ratio()
        except Exception:  # pragma: no cover - defensive
            anneal_ratio = None
        try:
            possessed_agents = list(self.policy.possessed_agents())
        except Exception:  # pragma: no cover - defensive
            possessed_agents = []
        try:
            policy_hash = self.policy.active_policy_hash()
        except Exception:  # pragma: no cover - defensive
            policy_hash = None
        identity_payload = self.config.build_snapshot_identity(
            policy_hash=policy_hash,
            runtime_observation_variant=self.config.observation_variant,
            runtime_anneal_ratio=anneal_ratio,
        )
        policy_metadata = {
            "identity": identity_payload,
            "possessed_agents": possessed_agents,
            "option_switch_counts": {},
            "anneal_ratio": anneal_ratio,
        }
        promotion_state = self.promotion.snapshot()
        try:
            queue_snapshot = self.world.queue_manager.export_state()
        except Exception:  # pragma: no cover - defensive
            logger.debug("queue_snapshot_unavailable_bootstrap", exc_info=True)
            queue_snapshot = {}
        try:
            anneal_context = self.policy.anneal_context()
        except Exception:  # pragma: no cover - defensive
            anneal_context = {}

        return build_observation_envelope(
            tick=self.tick,
            observations=observation_batch,
            actions={},
            terminated=terminated,
            termination_reasons={},
            queue_metrics=queue_metrics,
            rewards=rewards,
            reward_breakdown=reward_breakdown,
            perturbations=perturbation_state,
            policy_snapshot=policy_snapshot,
            policy_metadata=policy_metadata,
            rivalry_events=[],
            stability_metrics=self.stability.latest_metrics(),
            promotion_state=promotion_state,
            rng_seed=getattr(self.world, "rng_seed", None),
            queues=queue_snapshot,
            running_affordances=running_affordances,
            relationship_snapshot=relationship_snapshot,
            relationship_metrics=relationship_metrics,
            agent_snapshots=agent_snapshots_map,
            job_snapshot=job_snapshot,
            queue_affinity_metrics=queue_affinity_metrics,
            employment_snapshot=employment_metrics,
            economy_snapshot=economy_snapshot,
            anneal_context=anneal_context,
            agent_contexts=agent_contexts,
        )

    def _collect_queue_metrics(self) -> dict[str, int]:
        metrics: dict[str, int] = {}
        try:
            raw = self.world.queue_manager.metrics()
            metrics = {str(key): int(value) for key, value in raw.items()}
        except Exception:  # pragma: no cover - defensive
            logger.debug("queue_metrics_unavailable", exc_info=True)
        return metrics

    def _collect_queue_affinity_metrics(self) -> dict[str, int]:
        try:
            raw = self.world.queue_manager.performance_metrics()
            return {str(key): int(value) for key, value in raw.items()}
        except Exception:  # pragma: no cover - defensive
            logger.debug("queue_affinity_metrics_unavailable", exc_info=True)
            return {}

    def _try_context_observe(
        self,
        *,
        actions: Mapping[str, Any],
        terminated: Mapping[str, bool],
        termination_reasons: Mapping[str, str],
        queue_metrics: Mapping[str, int],
        rewards: Mapping[str, float],
        reward_breakdown: Mapping[str, Mapping[str, float]],
        perturbations: Mapping[str, Any],
        policy_snapshot: Mapping[str, Any],
        policy_metadata: Mapping[str, Any],
        rivalry_events: Iterable[Mapping[str, Any]],
        stability_metrics: Mapping[str, Any],
        promotion_state: Mapping[str, Any] | None,
        anneal_context: Mapping[str, Any],
    ) -> ObservationEnvelope | None:
        context = getattr(self.world, "context", None)
        if context is None:
            return None
        if getattr(context, "observation_service", None) is None:
            return None
        try:
            return context.observe(
                actions=actions,
                policy_snapshot=policy_snapshot,
                policy_metadata=policy_metadata,
                rivalry_events=rivalry_events,
                stability_metrics=stability_metrics,
                promotion_state=promotion_state,
                anneal_context=anneal_context,
                terminated=terminated,
                termination_reasons=termination_reasons,
                rewards=rewards,
                reward_breakdown=reward_breakdown,
            )
        except Exception:  # pragma: no cover - defensive fallback
            logger.debug("context_observe_failed", exc_info=True)
            return None

    def _collect_embedding_metrics(self, adapter: WorldRuntimeAdapter) -> dict[str, float]:
        try:
            metrics = adapter.embedding_allocator.metrics()
            return {str(key): float(value) for key, value in metrics.items()}
        except Exception:  # pragma: no cover - defensive
            logger.debug("embedding_metrics_unavailable", exc_info=True)
            return {}

    def _collect_job_snapshot(self, adapter: WorldRuntimeAdapter) -> dict[str, dict[str, object]]:
        snapshot: dict[str, dict[str, object]] = {}
        for agent_id, agent in adapter.agent_snapshots_view().items():
            inventory = agent.inventory or {}
            snapshot[str(agent_id)] = {
                "job_id": agent.job_id,
                "on_shift": bool(agent.on_shift),
                "wallet": float(agent.wallet),
                "lateness_counter": int(agent.lateness_counter),
                "wages_earned": int(inventory.get("wages_earned", 0) or 0),
                "meals_cooked": int(inventory.get("meals_cooked", 0) or 0),
                "meals_consumed": int(inventory.get("meals_consumed", 0) or 0),
                "basket_cost": float(inventory.get("basket_cost", 0.0) or 0.0),
                "shift_state": agent.shift_state,
                "attendance_ratio": float(agent.attendance_ratio),
                "late_ticks_today": int(agent.late_ticks_today),
                "absent_shifts_7d": int(agent.absent_shifts_7d),
                "wages_withheld": float(agent.wages_withheld),
                "exit_pending": bool(agent.exit_pending),
                "needs": {
                    str(need): float(value)
                    for need, value in agent.needs.items()
                },
            }
        return snapshot

    def _collect_employment_metrics(self) -> dict[str, object]:
        try:
            metrics = self.world.employment_queue_snapshot()
            if isinstance(metrics, Mapping):
                return {str(key): value for key, value in metrics.items()}
        except Exception:  # pragma: no cover - defensive
            logger.debug("employment_metrics_unavailable", exc_info=True)
        return {}

    def _collect_rivalry_events(self, adapter: WorldRuntimeAdapter) -> list[dict[str, object]]:
        try:
            raw_events = adapter.consume_rivalry_events()
        except Exception:  # pragma: no cover - defensive
            logger.debug("rivalry_events_unavailable", exc_info=True)
            raw_events = []
        clean_events: list[dict[str, object]] = []
        for event in raw_events:
            if not isinstance(event, Mapping):
                continue
            clean_events.append(
                {
                    "tick": int(event.get("tick", self.tick)),
                    "agent_a": str(event.get("agent_a", "")),
                    "agent_b": str(event.get("agent_b", "")),
                    "intensity": float(event.get("intensity", 0.0)),
                    "reason": str(event.get("reason", "")),
                }
            )
        if clean_events:
            self._rivalry_history.extend(clean_events)
            if len(self._rivalry_history) > 120:
                self._rivalry_history = self._rivalry_history[-120:]
        return list(self._rivalry_history)

    def _collect_economy_snapshot(self) -> dict[str, object]:
        snapshot: dict[str, object] = {}
        try:
            snapshot["settings"] = self.world.economy_settings()
        except Exception:  # pragma: no cover - defensive
            logger.debug("economy_settings_unavailable", exc_info=True)
        try:
            snapshot["active_price_spikes"] = self.world.active_price_spikes()
        except Exception:  # pragma: no cover - defensive
            logger.debug("economy_price_spikes_unavailable", exc_info=True)
        try:
            snapshot["utility_snapshot"] = self.world.utility_snapshot()
        except Exception:  # pragma: no cover - defensive
            logger.debug("economy_utility_snapshot_unavailable", exc_info=True)
        return snapshot

    def _build_transport_status(self, *, queue_length: int) -> dict[str, object]:
        status = dict(self._last_transport_status)
        telemetry_status: Mapping[str, object] | None = None
        publisher = getattr(self, "telemetry", None)
        getter = getattr(publisher, "latest_transport_status", None)
        if callable(getter):
            try:
                telemetry_status = dict(getter())
            except Exception:  # pragma: no cover - telemetry may be stubbed
                telemetry_status = None
        if telemetry_status:
            status.update(telemetry_status)
        status.update(
            {
                "provider": status.get("provider", "port"),
                "queue_length": queue_length,
                "dropped_messages": status.get("dropped_messages", 0),
                "last_flush_duration_ms": status.get("last_flush_duration_ms"),
                "worker_alive": status.get("worker_alive", True),
                "worker_error": status.get("worker_error"),
                "worker_restart_count": status.get("worker_restart_count", 0),
                "payloads_flushed_total": status.get("payloads_flushed_total", 0),
                "bytes_flushed_total": status.get("bytes_flushed_total", 0),
                "auth_enabled": status.get("auth_enabled", False),
            }
        )
        self._last_transport_status = status
        return status

    def _load_affordance_runtime_factory(
        self, runtime_config: AffordanceRuntimeConfig
    ) -> Callable[[WorldState, AffordanceRuntimeContext], DefaultAffordanceRuntime] | None:
        if not runtime_config.factory:
            return None
        factory_callable = self._import_symbol(runtime_config.factory)

        def _factory(world: WorldState, context: AffordanceRuntimeContext):
            return factory_callable(world=world, context=context, config=runtime_config)

        return _factory

    def _apply_runtime_overrides_from_config(self) -> None:
        runtime_section = getattr(self.config, "runtime", None)
        if runtime_section is None:
            return
        if hasattr(runtime_section, "model_dump"):
            data = runtime_section.model_dump()
        elif isinstance(runtime_section, Mapping):
            data = runtime_section
        else:
            return

        def _extract(
            key: str,
            current_provider: str,
            provider_locked: bool,
            current_options: dict[str, object],
            options_locked: bool,
        ) -> tuple[str, dict[str, object]]:
            raw = data.get(key)
            if not isinstance(raw, Mapping):
                return current_provider, current_options
            provider = current_provider
            if not provider_locked:
                provider = str(raw.get("provider", current_provider)).strip() or current_provider
            options = dict(current_options)
            if not options_locked:
                raw_options = raw.get("options")
                if isinstance(raw_options, Mapping):
                    options.update({str(k): v for k, v in raw_options.items()})
            return provider, options

        self._world_provider, self._world_options = _extract(
            "world",
            self._world_provider,
            self._world_provider_locked,
            self._world_options,
            self._world_options_locked,
        )
        self._policy_provider, self._policy_options = _extract(
            "policy",
            self._policy_provider,
            self._policy_provider_locked,
            self._policy_options,
            self._policy_options_locked,
        )
        self._telemetry_provider, self._telemetry_options = _extract(
            "telemetry",
            self._telemetry_provider,
            self._telemetry_provider_locked,
            self._telemetry_options,
            self._telemetry_options_locked,
        )

    @staticmethod
    def _import_symbol(path: str):
        module_name, separator, attribute = path.partition(":")
        if separator != ":" or not module_name or not attribute:
            raise ValueError(f"Invalid runtime factory path '{path}'. Use 'module:callable' format.")
        module = import_module(module_name)
        try:
            return getattr(module, attribute)
        except AttributeError as exc:  # pragma: no cover - defensive
            raise AttributeError(f"Runtime factory '{attribute}' not found in module '{module_name}'") from exc

    def close(self) -> None:
        """Release resources held by the loop (telemetry, runtime, policy)."""

        telemetry = getattr(self, "telemetry", None)
        if telemetry is not None:
            close = getattr(telemetry, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:  # pragma: no cover - defensive cleanup
                    logger.debug("Telemetry close raised during loop shutdown", exc_info=True)

    def __enter__(self) -> "SimulationLoop":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False

    def _derive_seed(self, stream: str) -> int:
        digest = hashlib.sha256(f"{self.config.config_id}:{stream}".encode())
        return int.from_bytes(digest.digest()[:8], "big")
