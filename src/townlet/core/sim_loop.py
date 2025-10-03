"""Top-level simulation loop wiring.

The loop follows the order defined in docs/HIGH_LEVEL_DESIGN.md and delegates to
feature-specific subsystems. Each dependency is a thin façade around the actual
implementation, allowing tests to substitute stubs while the real code evolves.
"""

from __future__ import annotations

import hashlib
from importlib import import_module
import logging
import random
import time
from collections.abc import Iterable
from typing import Callable
from dataclasses import dataclass
from pathlib import Path

from townlet.config import AffordanceRuntimeConfig, SimulationConfig
from townlet.lifecycle.manager import LifecycleManager
from townlet.observations.builder import ObservationBuilder
from townlet.policy.runner import PolicyRuntime
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
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.utils import decode_rng_state
from townlet.world.affordances import AffordanceRuntimeContext, DefaultAffordanceRuntime
from townlet.world.grid import WorldState

logger = logging.getLogger(__name__)


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
        affordance_runtime_factory: Callable[[WorldState, AffordanceRuntimeContext], DefaultAffordanceRuntime] | None = None,
    ) -> None:
        self.config = config
        self.config.register_snapshot_migrations()
        self._runtime_config: AffordanceRuntimeConfig = self.config.affordances.runtime
        if affordance_runtime_factory is not None:
            self._affordance_runtime_factory = affordance_runtime_factory
        else:
            self._affordance_runtime_factory = self._load_affordance_runtime_factory(
                self._runtime_config
            )
        self._build_components()

    def _build_components(self) -> None:
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
        self.policy = PolicyRuntime(config=self.config)
        self.policy.register_ctx_reset_callback(self.world.request_ctx_reset)
        if self.config.training.anneal_enable_policy_blend:
            self.policy.enable_anneal_blend(True)
        self.rewards = RewardEngine(config=self.config)
        self.telemetry = TelemetryPublisher(config=self.config)
        self.stability = StabilityMonitor(config=self.config)
        log_path = Path("logs/promotion_history.jsonl")
        self.promotion = PromotionManager(config=self.config, log_path=log_path)
        self.tick = 0
        self._ticks_per_day = max(1, self.observations.hybrid_cfg.time_ticks_per_day)

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
        """Run the loop until `max_ticks` or indefinitely."""
        while max_ticks is None or self.tick < max_ticks:
            artifacts = self.step()
            yield artifacts

    def step(self) -> TickArtifacts:
        tick_start = time.perf_counter()
        self.tick += 1
        self.world.tick = self.tick
        self.lifecycle.process_respawns(self.world, tick=self.tick)
        console_ops = self.telemetry.drain_console_buffer()
        self.world.apply_console(console_ops)
        console_results = self.world.consume_console_results()
        self.telemetry.record_console_results(console_results)
        self.perturbations.tick(self.world, current_tick=self.tick)
        actions = self.policy.decide(self.world, self.tick)
        self.world.apply_actions(actions)
        self.world.resolve_affordances(current_tick=self.tick)
        if self._ticks_per_day and self.tick % self._ticks_per_day == 0:
            self.world.apply_nightly_reset()
        episode_span = max(1, self.observations.hybrid_cfg.time_ticks_per_day)
        for snapshot in self.world.agents.values():
            snapshot.episode_tick = (snapshot.episode_tick + 1) % episode_span
        terminated = self.lifecycle.evaluate(self.world, tick=self.tick)
        termination_reasons = self.lifecycle.termination_reasons()
        rewards = self.rewards.compute(self.world, terminated, termination_reasons)
        reward_breakdown = self.rewards.latest_reward_breakdown()
        self.policy.post_step(rewards, terminated)
        observations = self.observations.build_batch(self.world, terminated)
        self.policy.flush_transitions(observations)
        policy_snapshot = self.policy.latest_policy_snapshot()
        possessed_agents = self.policy.possessed_agents()
        events = self.world.drain_events()
        option_switch_counts = self.policy.consume_option_switch_counts()
        hunger_levels = {
            agent_id: float(snapshot.needs.get("hunger", 1.0))
            for agent_id, snapshot in self.world.agents.items()
        }
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
            "tick_duration_ms": duration_ms,
            "telemetry_queue": transport_status.get("queue_length", 0),
            "telemetry_dropped": transport_status.get("dropped_messages", 0),
            "perturbations_pending": self.perturbations.pending_count(),
            "perturbations_active": self.perturbations.active_count(),
            "employment_exit_queue": len(getattr(self.world, "_employment_exit_queue", [])),
        }
        self.telemetry.record_health_metrics(health_payload)
        if logger.isEnabledFor(logging.INFO):
            logger.info(
                "tick_health tick=%s duration_ms=%.2f queue=%s dropped=%s perturbations_pending=%s perturbations_active=%s exit_queue=%s",
                self.tick,
                duration_ms,
                health_payload["telemetry_queue"],
                health_payload["telemetry_dropped"],
                health_payload["perturbations_pending"],
                health_payload["perturbations_active"],
                health_payload["employment_exit_queue"],
            )
        return TickArtifacts(observations=observations, rewards=rewards)

    def _load_affordance_runtime_factory(
        self, runtime_config: AffordanceRuntimeConfig
    ) -> Callable[[WorldState, AffordanceRuntimeContext], DefaultAffordanceRuntime] | None:
        if not runtime_config.factory:
            return None
        factory_callable = self._import_symbol(runtime_config.factory)

        def _factory(world: WorldState, context: AffordanceRuntimeContext):
            return factory_callable(world=world, context=context, config=runtime_config)

        return _factory

    @staticmethod
    def _import_symbol(path: str):
        module_name, separator, attribute = path.partition(":")
        if separator != ":" or not module_name or not attribute:
            raise ValueError(
                f"Invalid runtime factory path '{path}'. Use 'module:callable' format."
            )
        module = import_module(module_name)
        try:
            return getattr(module, attribute)
        except AttributeError as exc:  # pragma: no cover - defensive
            raise AttributeError(
                f"Runtime factory '{attribute}' not found in module '{module_name}'"
            ) from exc

    def _derive_seed(self, stream: str) -> int:
        digest = hashlib.sha256(f"{self.config.config_id}:{stream}".encode())
        return int.from_bytes(digest.digest()[:8], "big")
