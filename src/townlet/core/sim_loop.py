"""Top-level simulation loop wiring.

The loop follows the order defined in docs/HIGH_LEVEL_DESIGN.md and delegates to
feature-specific subsystems. Each dependency is a thin façade around the actual
implementation, allowing tests to substitute stubs while the real code evolves.
"""

from __future__ import annotations

import hashlib
import logging
import random
import time
import traceback
from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path

from townlet.config import AffordanceRuntimeConfig, SimulationConfig
from townlet.core.factory_registry import (
    resolve_policy,
    resolve_telemetry,
    resolve_world,
)
from townlet.core.interfaces import (
    PolicyBackendProtocol,
    TelemetrySinkProtocol,
    WorldRuntimeProtocol,
)
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
from townlet.world.grid import WorldState

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

    observations: dict[str, object]
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
        self.observations = ObservationBuilder(config=self.config)
        policy_kwargs = {"config": self.config, **self._policy_options}
        policy_instance: PolicyBackendProtocol = resolve_policy(self._policy_provider, **policy_kwargs)
        self.policy = policy_instance
        self._resolved_providers["policy"] = self._policy_provider
        self.policy.register_ctx_reset_callback(self.world.request_ctx_reset)
        if self.config.training.anneal_enable_policy_blend:
            self.policy.enable_anneal_blend(True)
        self.rewards = RewardEngine(config=self.config)
        telemetry_kwargs = {"config": self.config, **self._telemetry_options}
        telemetry_instance: TelemetrySinkProtocol = resolve_telemetry(self._telemetry_provider, **telemetry_kwargs)
        self.telemetry = telemetry_instance
        self._resolved_providers["telemetry"] = self._telemetry_provider
        self.stability = StabilityMonitor(config=self.config)
        log_path = Path("logs/promotion_history.jsonl")
        self.promotion = PromotionManager(config=self.config, log_path=log_path)
        self.tick = 0
        self._ticks_per_day = max(1, self.observations.hybrid_cfg.time_ticks_per_day)
        world_kwargs = {
            "world": self.world,
            "lifecycle": self.lifecycle,
            "perturbations": self.perturbations,
            "ticks_per_day": self._ticks_per_day,
            **self._world_options,
        }
        runtime_instance: WorldRuntimeProtocol = resolve_world(self._world_provider, **world_kwargs)
        self.runtime = runtime_instance
        self._resolved_providers["world"] = self._world_provider
        if self._world_adapter is not None:
            bind_adapter = getattr(runtime_instance, "bind_world_adapter", None)
            if callable(bind_adapter):
                bind_adapter(self._world_adapter)
        self._runtime_variant = "facade"
        self.telemetry.set_runtime_variant(self._runtime_variant)
        self._health = SimulationLoopHealth(last_tick=self.tick)

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

    def register_failure_handler(self, handler: Callable[[SimulationLoop, int, BaseException], None]) -> None:
        """Register a callback that runs whenever the loop records a failure."""

        self._failure_handlers.append(handler)

    def reset(self) -> None:
        """Reset the simulation loop to its initial state."""
        self._build_components()

    def set_anneal_ratio(self, ratio: float | None) -> None:
        self.policy.set_anneal_ratio(ratio)

    # ------------------------------------------------------------------
    # Snapshot helpers
    # ------------------------------------------------------------------
    def save_snapshot(self, root: Path | None = None) -> Path:
        """Persist the current world relationships and tick to ``root``."""

        target_root = Path(root).expanduser() if root is not None else self.config.snapshot_root()
        manager = SnapshotManager(root=target_root)
        identity_payload = self.config.build_snapshot_identity(
            policy_hash=self.policy.active_policy_hash(),
            runtime_observation_variant=self.config.observation_variant,
            runtime_anneal_ratio=self.policy.current_anneal_ratio(),
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
        self.telemetry.record_stability_metrics(stability_metrics)
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
        """Advance the simulation loop by one tick and return observations/rewards."""
        tick_start = time.perf_counter()
        next_tick = self.tick + 1
        console_ops = self.telemetry.drain_console_buffer()
        runtime = self.runtime
        if runtime is None:  # pragma: no cover - defensive guard
            raise RuntimeError("WorldRuntime is not initialised")

        try:
            self.tick = next_tick
            runtime.queue_console(console_ops)

            def _action_provider(world: WorldState, current_tick: int) -> Mapping[str, object]:
                return self.policy.decide(world, current_tick)

            runtime_result = runtime.tick(
                tick=self.tick,
                action_provider=_action_provider,
            )
            console_results = runtime_result.console_results
            events = runtime_result.events
            terminated = runtime_result.terminated
            termination_reasons = runtime_result.termination_reasons

            self.telemetry.record_console_results(console_results)
            episode_span = max(1, self.observations.hybrid_cfg.time_ticks_per_day)
            for snapshot in self.world.agents.values():
                snapshot.episode_tick = (snapshot.episode_tick + 1) % episode_span
            rewards = self.rewards.compute(self.world, terminated, termination_reasons)
            reward_breakdown = self.rewards.latest_reward_breakdown()
            self.policy.post_step(rewards, terminated)
            observations = self.observations.build_batch(self.world_adapter, terminated)
            self.policy.flush_transitions(observations)
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
            policy_identity = self.config.build_snapshot_identity(
                policy_hash=self.policy.active_policy_hash(),
                runtime_observation_variant=self.config.observation_variant,
                runtime_anneal_ratio=self.policy.current_anneal_ratio(),
            )
            self.telemetry.publish_tick(
                tick=self.tick,
                world=self.world,
                observations=observations,
                rewards=rewards,
                events=events,
                policy_snapshot=policy_snapshot,
                kpi_history=True,
                reward_breakdown=reward_breakdown,
                stability_inputs=stability_inputs,
                perturbations=perturbation_state,
                policy_identity=policy_identity,
                possessed_agents=possessed_agents,
                social_events=self.rewards.latest_social_events(),
                runtime_variant=self._runtime_variant,
            )
            self.stability.track(
                tick=self.tick,
                rewards=rewards,
                terminated=terminated,
                queue_metrics=self.telemetry.latest_queue_metrics(),
                embedding_metrics=self.telemetry.latest_embedding_metrics(),
                job_snapshot=self.telemetry.latest_job_snapshot(),
                events=self.telemetry.latest_events(),
                employment_metrics=self.telemetry.latest_employment_metrics(),
                hunger_levels=hunger_levels,
                option_switch_counts=option_switch_counts,
                rivalry_events=self.telemetry.latest_rivalry_events(),
            )
            stability_metrics = self.stability.latest_metrics()
            self.promotion.update_from_metrics(stability_metrics, tick=self.tick)
            stability_metrics["promotion_state"] = self.promotion.snapshot()
            self.telemetry.record_stability_metrics(stability_metrics)
            self.lifecycle.finalize(self.world, tick=self.tick, terminated=terminated)
            duration_ms = (time.perf_counter() - tick_start) * 1000.0
            transport_status = self.telemetry.latest_transport_status()
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
            self.telemetry.record_health_metrics(health_payload)
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
            return TickArtifacts(observations=observations, rewards=rewards)
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
        transport_status = self.telemetry.latest_transport_status()
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
        self.telemetry.record_loop_failure(payload)
        for handler in list(self._failure_handlers):
            try:
                handler(self, tick, exc)
            except Exception:  # pragma: no cover - handlers should not break the loop
                logger.exception("Simulation loop failure handler raised")

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
