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
from townlet.console.service import ConsoleService
from townlet.core.interfaces import (
    PolicyBackendProtocol,
    TelemetrySinkProtocol,
)
from townlet.factories import create_policy, create_telemetry, create_world
from townlet.lifecycle.manager import LifecycleManager
from townlet.orchestration import ConsoleRouter, HealthMonitor, PolicyController
from townlet.policy.runner import PolicyRuntime
from townlet.ports.world import WorldRuntime
from townlet.rewards.engine import RewardEngine
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.snapshots import (
    SnapshotManager,
    apply_snapshot_to_telemetry,
    apply_snapshot_to_world,
)
from townlet.stability.monitor import StabilityMonitor
from townlet.stability.promotion import PromotionManager
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.utils import decode_rng_state
from townlet.utils.coerce import coerce_float, coerce_int
from townlet.world.affordances import AffordanceRuntimeContext, DefaultAffordanceRuntime
from townlet.world.core import WorldContext, WorldRuntimeAdapter
from townlet.world.dto.observation import ObservationEnvelope
from townlet.world.grid import WorldState
from townlet.world.observations.interfaces import ObservationServiceProtocol

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WorldComponents:
    world: WorldState
    lifecycle: LifecycleManager
    perturbations: PerturbationScheduler
    observation_service: ObservationServiceProtocol
    world_port: WorldRuntime
    ticks_per_day: int
    provider: str
    console_service: ConsoleService


@dataclass(slots=True)
class PolicyComponents:
    port: PolicyBackendProtocol
    controller: PolicyController | None
    decision_backend: Any
    provider: str


@dataclass(slots=True)
class TelemetryComponents:
    port: TelemetrySinkProtocol
    publisher: TelemetrySinkProtocol
    provider: str


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
        if affordance_runtime_factory is None:
            factory = self._load_affordance_runtime_factory(self._runtime_config)
        else:
            factory = affordance_runtime_factory
        self._affordance_runtime_factory: Callable[
            [WorldState, AffordanceRuntimeContext],
            DefaultAffordanceRuntime,
        ]
        self._affordance_runtime_factory = factory
        self.runtime: WorldRuntime | None = None
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
        self._world_components_override: Callable[[SimulationLoop], WorldComponents] | None = None
        self._policy_components_override: Callable[[SimulationLoop], PolicyComponents] | None = None
        self._telemetry_components_override: Callable[[SimulationLoop], TelemetryComponents] | None = None
        self._observation_service: ObservationServiceProtocol | None = None
        self._runtime_variant: str = "facade"
        self._resolved_providers: dict[str, str] = {}
        self._failure_handlers: list[Callable[[SimulationLoop, int, BaseException], None]] = []
        self._health = SimulationLoopHealth()
        self._world_adapter: WorldRuntimeAdapter | None = None
        self._world_context: WorldContext | None = None
        self._world_port: WorldRuntime | None = None
        self._console_service: ConsoleService | None = None
        self._policy_port: PolicyBackendProtocol | None = None
        self._telemetry_port: TelemetrySinkProtocol | None = None
        self._policy_controller: PolicyController | None = None
        self._console_router: ConsoleRouter | None = None
        self._health_monitor: HealthMonitor | None = None
        self._rivalry_history: list[dict[str, object]] = []
        self._policy_observation_envelope: ObservationEnvelope | None = None
        self._last_policy_metadata_event: dict[str, object] | None = None
        self._last_policy_possession_agents: tuple[str, ...] | None = None
        self._last_policy_anneal_event: dict[str, object] | None = None
        self._last_health_payload: dict[str, object] | None = None
        self._last_global_context: dict[str, object] | None = None
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
                if isinstance(runtime, WorldRuntime):
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
        world_components = self._resolve_world_components()
        self.world = world_components.world
        self.lifecycle = world_components.lifecycle
        self.perturbations = world_components.perturbations
        self._observation_service = world_components.observation_service
        self._ticks_per_day = world_components.ticks_per_day
        self._console_service = world_components.console_service
        self._world_port = world_components.world_port
        context = getattr(self._world_port, "context", None)
        if context is not None:
            self._world_context = context
        self.runtime = self._world_port
        self._resolved_providers["world"] = world_components.provider

        policy_components = self._resolve_policy_components()
        self._policy_port = policy_components.port
        self.policy = policy_components.decision_backend
        self._policy_controller = policy_components.controller
        self._resolved_providers["policy"] = policy_components.provider

        telemetry_components = self._resolve_telemetry_components()
        self._telemetry_port = telemetry_components.port
        self.telemetry = telemetry_components.publisher
        self._resolved_providers["telemetry"] = telemetry_components.provider

        controller = self._policy_controller
        if controller is not None:
            controller.bind_world_supplier(lambda: self.world)
        self.rewards = RewardEngine(config=self.config)
        self.stability = StabilityMonitor(config=self.config)
        log_path = Path("logs/promotion_history.jsonl")
        self.promotion = PromotionManager(config=self.config, log_path=log_path)
        self.tick = 0
        controller = self._policy_controller
        if controller is not None:
            controller.register_ctx_reset_callback(self.world.request_ctx_reset)
            if self.config.training.anneal_enable_policy_blend:
                controller.enable_anneal_blend(True)
        else:  # pragma: no cover - defensive
            self.policy.register_ctx_reset_callback(self.world.request_ctx_reset)
            if self.config.training.anneal_enable_policy_blend:
                self.policy.enable_anneal_blend(True)
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

    def override_world_components(
        self,
        builder: Callable[[SimulationLoop], WorldComponents] | None,
    ) -> None:
        """Override the world component builder (testing seam)."""

        self._world_components_override = builder

    def override_policy_components(
        self,
        builder: Callable[[SimulationLoop], PolicyComponents] | None,
    ) -> None:
        """Override the policy component builder (testing seam)."""

        self._policy_components_override = builder

    def override_telemetry_components(
        self,
        builder: Callable[[SimulationLoop], TelemetryComponents] | None,
    ) -> None:
        """Override the telemetry component builder (testing seam)."""

        self._telemetry_components_override = builder

    def _resolve_world_components(self) -> WorldComponents:
        if self._world_components_override is not None:
            return self._world_components_override(self)
        return self._build_default_world_components()

    def _resolve_policy_components(self) -> PolicyComponents:
        if self._policy_components_override is not None:
            return self._policy_components_override(self)
        return self._build_default_policy_components()

    def _resolve_telemetry_components(self) -> TelemetryComponents:
        if self._telemetry_components_override is not None:
            return self._telemetry_components_override(self)
        return self._build_default_telemetry_components()

    def _build_default_world_components(self) -> WorldComponents:
        cfg = getattr(self.config, "observations_config", None)
        ticks_per_day = 1440
        if cfg is not None and getattr(cfg, "hybrid", None) is not None:
            ticks_per_day = getattr(cfg.hybrid, "time_ticks_per_day", 1440)
        ticks_per_day = max(1, int(ticks_per_day))
        world_port = create_world(
            provider=self._world_provider,
            config=self.config,
            ticks_per_day=ticks_per_day,
            world_kwargs=self._world_options,
            affordance_runtime_factory=self._affordance_runtime_factory,
            affordance_runtime_config=self._runtime_config,
        )
        context = getattr(world_port, "context", None)
        if context is None:
            raise RuntimeError("World provider did not supply a context-backed adapter")
        observation_service = getattr(context, "observation_service", None)
        if observation_service is None:
            raise RuntimeError("World context missing observation service")
        console_service = getattr(context, "console", None)
        if console_service is None:
            raise RuntimeError("World context missing console service")
        world = context.state
        lifecycle = getattr(world_port, "lifecycle_manager", None)
        if lifecycle is None:
            raise RuntimeError("World provider did not expose lifecycle manager")
        perturbations = getattr(world_port, "perturbation_scheduler", None)
        if perturbations is None:
            raise RuntimeError("World provider did not expose perturbation scheduler")
        self._world_context = context
        return WorldComponents(
            world=world,
            lifecycle=lifecycle,
            perturbations=perturbations,
            observation_service=observation_service,
            world_port=world_port,
            ticks_per_day=ticks_per_day,
            provider=self._world_provider,
            console_service=console_service,
        )

    def _build_default_policy_components(self) -> PolicyComponents:
        policy_kwargs = {"config": self.config, **self._policy_options}
        policy_backend = PolicyRuntime(**policy_kwargs)
        policy_port = create_policy(
            provider=self._policy_provider,
            backend=policy_backend,
        )
        controller: PolicyController | None = None
        backend_attr = getattr(policy_port, "backend", None)
        if backend_attr is not None:
            decision_backend = backend_attr
            controller = PolicyController(backend=decision_backend, port=policy_port)
        else:
            decision_backend = policy_port  # type: ignore[assignment]
        return PolicyComponents(
            port=policy_port,
            controller=controller,
            decision_backend=decision_backend,
            provider=self._policy_provider,
        )

    def _build_default_telemetry_components(self) -> TelemetryComponents:
        telemetry_kwargs = {"config": self.config, **self._telemetry_options}
        publisher = TelemetryPublisher(**telemetry_kwargs)
        telemetry_port = create_telemetry(
            provider=self._telemetry_provider,
            publisher=publisher,
        )
        port_publisher = getattr(telemetry_port, "publisher", None)
        if isinstance(port_publisher, TelemetryPublisher):
            publisher_sink: TelemetrySinkProtocol = port_publisher
        else:
            publisher_sink = telemetry_port
            try:  # pragma: no cover - defensive close
                publisher.close()
            except Exception:
                pass
        return TelemetryComponents(
            port=telemetry_port,
            publisher=publisher_sink,
            provider=self._telemetry_provider,
        )

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

        return self._require_world_context()

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

    def _require_world_context(self) -> WorldContext:
        """Return the active world context or raise if unavailable."""

        context = self._world_context
        if context is None and self._world_port is not None:
            context = getattr(self._world_port, "context", None)
        if context is None:
            raise RuntimeError("World context is not initialised")
        self._world_context = context
        return context

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
        state = self.runtime.snapshot(
            config=self.config,
            telemetry=self.telemetry,
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
        rng_streams.pop("context_seed", None)
        if state.rng_state and "world" not in rng_streams:
            rng_streams["world"] = state.rng_state
        if world_rng_str := rng_streams.get("world"):
            world_state = decode_rng_state(world_rng_str)
            self.world.set_rng_state(world_state)
            self._rng_world.setstate(world_state)
        if events_rng_str := rng_streams.get("events"):
            events_state = decode_rng_state(events_rng_str)
            self._rng_events.setstate(events_state)
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
        runtime = self.runtime
        if runtime is None:  # pragma: no cover - defensive guard
            raise RuntimeError("WorldRuntime is not initialised")
        if self._console_router is not None:
            for command in console_ops:
                try:
                    self._console_router.enqueue(command)
                except ValueError:
                    logger.warning("Ignoring invalid console command payload: %r", command)
        elif console_ops:
            logger.warning("ConsoleRouter unavailable; dropping %d buffered commands", len(console_ops))

        controller = self._policy_controller
        try:
            self.tick = next_tick

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
                console_operations=console_ops,
                action_provider=_action_provider,
            )
            console_results = runtime_result.console_results
            events = runtime_result.events
            terminated = runtime_result.terminated
            termination_reasons = runtime_result.termination_reasons
            if self._console_router is not None:
                self._console_router.run_pending(console_results, tick=self.tick)

            if console_results and self._console_router is None:
                emitter = (
                    self._telemetry_port.emit_event
                    if self._telemetry_port is not None
                    else self.telemetry.emit_event  # pragma: no cover - defensive
                )
                for result in console_results:
                    emitter("console.result", {"result": result.to_dict()})
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
            hunger_levels = {
                agent_id: float(snapshot.needs.get("hunger", 1.0))
                for agent_id, snapshot in self.world.agents.items()
            }
            context = self._require_world_context()
            queue_metrics = dict(context.export_queue_metrics())
            job_snapshot = copy.deepcopy(context.export_job_snapshot())
            employment_metrics = copy.deepcopy(context.export_employment_snapshot())
            queue_state_export = context.export_queue_state()
            queues_snapshot: dict[str, object] = {}
            queue_length = 0.0
            if isinstance(queue_state_export, Mapping):
                queues_snapshot = copy.deepcopy(queue_state_export)
                queues_payload = queues_snapshot.get("queues", {})
                if isinstance(queues_payload, Mapping):
                    queue_length = float(
                        sum(len(entries or []) for entries in queues_payload.values())
                    )
            stability_inputs = {
                "hunger_levels": hunger_levels,
                "option_switch_counts": option_switch_counts,
                "reward_samples": dict(rewards),
                "queue_metrics": queue_metrics,
                "employment_snapshot": employment_metrics,
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
            embedding_metrics = self._collect_embedding_metrics(adapter)
            rivalry_events = self._collect_rivalry_events(adapter)
            snapshot_for_health: dict[str, Any] = {
                "tick": self.tick,
                "events": list(events),
            }
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
                policy_snapshot=policy_snapshot,
                policy_metadata=policy_metadata,
                rivalry_events=rivalry_events,
                stability_metrics=stability_metrics,
                promotion_state=promotion_state,
                anneal_context=anneal_context,
            )

            if dto_envelope is None:
                raise SimulationLoopError(self.tick, "World context failed to produce an observation envelope")
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
            global_context = self._build_tick_global_context(
                queue_metrics=queue_metrics,
                queue_state=queues_snapshot,
                employment_snapshot=employment_metrics,
                job_snapshot=job_snapshot,
                dto_envelope=dto_envelope,
                stability_metrics=stability_metrics,
                perturbations=perturbation_state,
                promotion_state=promotion_state,
                anneal_context=anneal_context,
                rivalry_events=rivalry_events,
            )
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
                    "global_context": global_context,
                }
                self._telemetry_port.emit_event("loop.tick", tick_event_payload)
            if self._telemetry_port is not None:
                self._telemetry_port.emit_event("stability.metrics", stability_metrics)
            else:  # pragma: no cover - defensive
                self.telemetry.emit_event("stability.metrics", stability_metrics)
            self.lifecycle.finalize(self.world, tick=self.tick, terminated=terminated)
            duration_ms = (time.perf_counter() - tick_start) * 1000.0
            transport_status = self._build_transport_status(queue_length=len(console_results))
            health_payload = self._build_health_payload(
                duration_ms=duration_ms,
                transport_status=transport_status,
                global_context=global_context,
            )
            if self._telemetry_port is not None:
                self._telemetry_port.emit_event("loop.health", health_payload)
            else:  # pragma: no cover - defensive
                self.telemetry.emit_event("loop.health", health_payload)
            if logger.isEnabledFor(logging.INFO):
                summary = health_payload.get("summary", {})
                logger.info(
                    (
                        "tick_health tick=%s duration_ms=%.2f queue=%s dropped=%s "
                        "flush_ms=%s payloads_total=%s bytes_total=%s "
                        "perturbations_pending=%s perturbations_active=%s exit_queue=%s"
                    ),
                    self.tick,
                    duration_ms,
                    summary.get("queue_length"),
                    summary.get("dropped_messages"),
                    summary.get("last_flush_duration_ms"),
                    summary.get("payloads_flushed_total"),
                    summary.get("bytes_flushed_total"),
                    summary.get("perturbations_pending"),
                    summary.get("perturbations_active"),
                    summary.get("employment_exit_queue"),
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
        failure_payload = self._build_failure_payload(
            tick=tick,
            duration_ms=duration_ms,
            error=error_message,
            transport_status=transport_status,
            snapshot_path=snapshot_path,
            global_context=self._last_global_context,
        )
        if self._telemetry_port is not None:
            self._telemetry_port.emit_event("loop.failure", failure_payload)
        else:  # pragma: no cover - defensive
            self.telemetry.emit_event("loop.failure", failure_payload)
        for handler in list(self._failure_handlers):
            try:
                handler(self, tick, exc)
            except Exception:  # pragma: no cover - handlers should not break the loop
                logger.exception("Simulation loop failure handler raised")

    def _ensure_policy_envelope(self) -> ObservationEnvelope:
        """Ensure a DTO envelope is available for policy decisions."""

        envelope = self._policy_observation_envelope
        if envelope is not None:
            return envelope
        bootstrap = self._build_bootstrap_policy_envelope()
        self._set_policy_observation_envelope(bootstrap)
        logger.debug("policy_envelope_bootstrap", extra={"tick": self.tick})
        return bootstrap

    def _build_tick_global_context(
        self,
        *,
        queue_metrics: Mapping[str, int],
        queue_state: Mapping[str, object],
        employment_snapshot: Mapping[str, object],
        job_snapshot: Mapping[str, Mapping[str, object]],
        dto_envelope: ObservationEnvelope,
        stability_metrics: Mapping[str, object],
        perturbations: Mapping[str, object],
        promotion_state: Mapping[str, object],
        anneal_context: Mapping[str, object],
        rivalry_events: Iterable[Mapping[str, object]],
    ) -> dict[str, object]:
        """Assemble the DTO-first global context payload for telemetry."""

        try:
            base_context = dto_envelope.global_context.model_dump(by_alias=True)
        except Exception:  # pragma: no cover - defensive safeguard
            base_context = {}

        global_context: dict[str, object] = copy.deepcopy(base_context)

        if "queue_metrics" not in global_context:
            global_context["queue_metrics"] = dict(queue_metrics)
        if queue_state:
            global_context["queues"] = copy.deepcopy(queue_state)
        if "employment_snapshot" not in global_context:
            global_context["employment_snapshot"] = copy.deepcopy(employment_snapshot)
        if "job_snapshot" not in global_context:
            global_context["job_snapshot"] = copy.deepcopy(job_snapshot)

        if "stability_metrics" not in global_context:
            global_context["stability_metrics"] = copy.deepcopy(dict(stability_metrics))
        if perturbations:
            global_context.setdefault("perturbations", copy.deepcopy(dict(perturbations)))
        if promotion_state:
            global_context.setdefault("promotion_state", copy.deepcopy(dict(promotion_state)))
        if anneal_context:
            global_context.setdefault("anneal_context", copy.deepcopy(dict(anneal_context)))

        rivalry_list = [dict(event) for event in rivalry_events]
        global_context["rivalry_events"] = rivalry_list

        context = self._world_context
        if context is not None:
            queue_affinity = context.export_queue_affinity_metrics()
            if queue_affinity:
                global_context.setdefault("queue_affinity_metrics", dict(queue_affinity))
            running_affordances = context.export_running_affordances()
            if running_affordances:
                global_context.setdefault("running_affordances", copy.deepcopy(dict(running_affordances)))
            economy_snapshot = context.export_economy_snapshot()
            if economy_snapshot:
                global_context.setdefault("economy_snapshot", copy.deepcopy(dict(economy_snapshot)))
            relationship_snapshot = context.export_relationship_snapshot()
            if relationship_snapshot:
                global_context.setdefault("relationship_snapshot", copy.deepcopy(dict(relationship_snapshot)))
            relationship_metrics = context.export_relationship_metrics()
            if relationship_metrics:
                global_context.setdefault("relationship_metrics", copy.deepcopy(dict(relationship_metrics)))

        self._last_global_context = copy.deepcopy(global_context)
        return global_context

    def _build_health_payload(
        self,
        *,
        duration_ms: float,
        transport_status: Mapping[str, object],
        global_context: Mapping[str, object] | None,
    ) -> dict[str, object]:
        """Compose the loop.health payload using DTO context data."""

        context_payload: dict[str, object] = {}
        if isinstance(global_context, Mapping):
            context_payload = copy.deepcopy(dict(global_context))

        queue_length = coerce_int(transport_status.get("queue_length"), default=0)
        dropped_messages = coerce_int(transport_status.get("dropped_messages"), default=0)
        last_flush_raw = transport_status.get("last_flush_duration_ms")
        last_flush_duration: float | None = None
        if last_flush_raw is not None:
            try:
                last_flush_duration = coerce_float(last_flush_raw)
            except (TypeError, ValueError):
                last_flush_duration = None

        transport_payload: dict[str, object] = {
            "provider": transport_status.get("provider"),
            "queue_length": queue_length,
            "dropped_messages": dropped_messages,
            "last_flush_duration_ms": last_flush_duration,
            "payloads_flushed_total": coerce_int(
                transport_status.get("payloads_flushed_total"), default=0
            ),
            "bytes_flushed_total": coerce_int(
                transport_status.get("bytes_flushed_total"), default=0
            ),
            "auth_enabled": bool(transport_status.get("auth_enabled", False)),
            "worker": {
                "alive": bool(transport_status.get("worker_alive", False)),
                "error": transport_status.get("worker_error"),
                "restart_count": coerce_int(
                    transport_status.get("worker_restart_count"), default=0
                ),
            },
        }

        perturbations_pending = 0
        perturbations_active = 0
        perturbations_payload = context_payload.get("perturbations")
        if isinstance(perturbations_payload, Mapping):
            pending_section = perturbations_payload.get("pending")
            active_section = perturbations_payload.get("active")

            def _coerce_count(value: object) -> int:
                if value is None:
                    return 0
                if isinstance(value, Mapping):
                    return len(value)
                if isinstance(value, (list, tuple, set)):
                    return len(value)
                return coerce_int(value, default=0)

            perturbations_pending = _coerce_count(pending_section)
            perturbations_active = _coerce_count(active_section)
        else:  # Fallback to scheduler counts when context data is absent.
            try:
                perturbations_pending = int(self.perturbations.pending_count())
                perturbations_active = int(self.perturbations.active_count())
            except Exception:  # pragma: no cover - defensive
                perturbations_pending = 0
                perturbations_active = 0

        employment_exit_queue = 0
        employment_snapshot = context_payload.get("employment_snapshot")
        if isinstance(employment_snapshot, Mapping):
            pending_count = employment_snapshot.get("pending_count")
            if isinstance(pending_count, (int, float)):
                employment_exit_queue = int(pending_count)
            else:
                pending_section = employment_snapshot.get("pending")
                if isinstance(pending_section, (list, tuple, set)):
                    employment_exit_queue = len(pending_section)
        else:  # Leverage context export if available.
            context = self._world_context
            snapshot_getter = getattr(context, "export_employment_snapshot", None)
            if callable(snapshot_getter):
                try:
                    snapshot = snapshot_getter()
                    if isinstance(snapshot, Mapping):
                        pending_count = snapshot.get("pending_count")
                        if isinstance(pending_count, (int, float)):
                            employment_exit_queue = int(pending_count)
                except Exception:  # pragma: no cover - defensive
                    employment_exit_queue = 0

        payload: dict[str, object] = {
            "tick": self.tick,
            "status": "ok",
            "duration_ms": duration_ms,
            "failure_count": self._health.failure_count,
            "transport": transport_payload,
            "global_context": context_payload,
        }
        payload["summary"] = {
            "duration_ms": duration_ms,
            "queue_length": queue_length,
            "dropped_messages": dropped_messages,
            "last_flush_duration_ms": transport_payload["last_flush_duration_ms"],
            "payloads_flushed_total": transport_payload["payloads_flushed_total"],
            "bytes_flushed_total": transport_payload["bytes_flushed_total"],
            "auth_enabled": transport_payload["auth_enabled"],
            "worker_alive": transport_payload["worker"]["alive"],
            "worker_error": transport_payload["worker"]["error"],
            "worker_restart_count": transport_payload["worker"]["restart_count"],
            "perturbations_pending": perturbations_pending,
            "perturbations_active": perturbations_active,
            "employment_exit_queue": employment_exit_queue,
        }
        self._last_health_payload = copy.deepcopy(payload)
        return payload

    def _build_failure_payload(
        self,
        *,
        tick: int,
        duration_ms: float,
        error: str,
        transport_status: Mapping[str, object],
        snapshot_path: str | None,
        global_context: Mapping[str, object] | None,
    ) -> dict[str, object]:
        """Compose the loop.failure payload with structured transport/context data."""

        context_payload: dict[str, object] = {}
        if isinstance(global_context, Mapping):
            context_payload = copy.deepcopy(dict(global_context))
        elif isinstance(self._last_global_context, Mapping):
            context_payload = copy.deepcopy(dict(self._last_global_context))

        last_flush_raw = transport_status.get("last_flush_duration_ms")
        last_flush_duration: float | None = None
        if last_flush_raw is not None:
            try:
                last_flush_duration = coerce_float(last_flush_raw)
            except (TypeError, ValueError):
                last_flush_duration = None

        transport_payload: dict[str, object] = {
            "provider": transport_status.get("provider"),
            "queue_length": coerce_int(transport_status.get("queue_length"), default=0),
            "dropped_messages": coerce_int(transport_status.get("dropped_messages"), default=0),
            "last_flush_duration_ms": last_flush_duration,
            "payloads_flushed_total": coerce_int(
                transport_status.get("payloads_flushed_total"), default=0
            ),
            "bytes_flushed_total": coerce_int(
                transport_status.get("bytes_flushed_total"), default=0
            ),
            "auth_enabled": bool(transport_status.get("auth_enabled", False)),
            "worker": {
                "alive": bool(transport_status.get("worker_alive", False)),
                "error": transport_status.get("worker_error"),
                "restart_count": coerce_int(
                    transport_status.get("worker_restart_count"), default=0
                ),
            },
        }

        payload: dict[str, object] = {
            "tick": int(tick),
            "status": "error",
            "duration_ms": duration_ms,
            "failure_count": self._health.failure_count,
            "error": error,
            "snapshot_path": snapshot_path,
            "transport": transport_payload,
            "global_context": context_payload,
        }

        last_health = self._last_health_payload
        if isinstance(last_health, Mapping):
            payload["health"] = copy.deepcopy(dict(last_health))
        payload["summary"] = {
            "duration_ms": duration_ms,
            "queue_length": transport_payload["queue_length"],
            "dropped_messages": transport_payload["dropped_messages"],
        }
        return payload

    def _set_policy_observation_envelope(self, envelope: ObservationEnvelope) -> None:
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

    def _build_bootstrap_policy_envelope(self) -> ObservationEnvelope:
        """Build a DTO envelope from the current world when none has been recorded."""

        context = self._require_world_context()
        if getattr(context, "observation_service", None) is None:
            raise RuntimeError("World context is not configured for observation DTOs")
        terminated: dict[str, bool] = {}
        rewards: dict[str, float] = {}
        reward_breakdown: dict[str, Mapping[str, float]] = {}
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
            anneal_context = self.policy.anneal_context()
        except Exception:  # pragma: no cover - defensive
            anneal_context = {}

        return context.observe(
            actions={},
            terminated=terminated,
            termination_reasons={},
            rewards=rewards,
            reward_breakdown=reward_breakdown,
            policy_snapshot=policy_snapshot,
            policy_metadata=policy_metadata,
            rivalry_events=[],
            stability_metrics=self.stability.latest_metrics(),
            promotion_state=promotion_state,
            anneal_context=anneal_context,
        )

    def _try_context_observe(
        self,
        *,
        actions: Mapping[str, Any],
        terminated: Mapping[str, bool],
        termination_reasons: Mapping[str, str],
        queue_metrics: Mapping[str, int],
        rewards: Mapping[str, float],
        reward_breakdown: Mapping[str, Mapping[str, float]],
        policy_snapshot: Mapping[str, Any],
        policy_metadata: Mapping[str, Any],
        rivalry_events: Iterable[Mapping[str, Any]],
        stability_metrics: Mapping[str, Any],
        promotion_state: Mapping[str, Any] | None,
        anneal_context: Mapping[str, Any],
    ) -> ObservationEnvelope | None:
        context = self._world_context or getattr(self._world_port, "context", None)
        if context is None:
            return None
        self._world_context = context
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

    def _build_transport_status(self, *, queue_length: int) -> dict[str, object]:
        status = dict(self._last_transport_status)
        telemetry_status: Mapping[str, object] | None = None
        port = self._telemetry_port
        getter = getattr(port, "transport_status", None)
        if callable(getter):
            try:
                telemetry_status = dict(getter())
            except Exception:  # pragma: no cover - telemetry may be stubbed
                telemetry_status = None
        elif port is None:
            publisher = getattr(self, "telemetry", None)
            legacy_getter = getattr(publisher, "latest_transport_status", None)
            if callable(legacy_getter):
                try:
                    telemetry_status = dict(legacy_getter())
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

    def __enter__(self) -> SimulationLoop:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False

    def _derive_seed(self, stream: str) -> int:
        digest = hashlib.sha256(f"{self.config.config_id}:{stream}".encode())
        return int.from_bytes(digest.digest()[:8], "big")
