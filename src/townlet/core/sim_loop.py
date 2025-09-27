"""Top-level simulation loop wiring.

The loop follows the order defined in docs/HIGH_LEVEL_DESIGN.md and delegates to
feature-specific subsystems. Each dependency is a thin façade around the actual
implementation, allowing tests to substitute stubs while the real code evolves.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from townlet.config import SimulationConfig
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
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.utils import decode_rng_state
from townlet.world.grid import WorldState


@dataclass
class TickArtifacts:
    """Collects per-tick data for logging and testing."""

    observations: dict[str, object]
    rewards: dict[str, float]


class SimulationLoop:
    """Orchestrates the Townlet simulation tick-by-tick."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.config.register_snapshot_migrations()
        self._build_components()

    def _build_components(self) -> None:
        self._rng_world = random.Random(self._derive_seed("world"))
        self._rng_events = random.Random(self._derive_seed("events"))
        self._rng_policy = random.Random(self._derive_seed("policy"))
        self.world = WorldState.from_config(self.config, rng=self._rng_world)
        self.lifecycle = LifecycleManager(config=self.config)
        self.perturbations = PerturbationScheduler(
            config=self.config,
            rng=self._rng_events,
        )
        self.observations = ObservationBuilder(config=self.config)
        self.policy = PolicyRuntime(config=self.config)
        self.rewards = RewardEngine(config=self.config)
        self.telemetry = TelemetryPublisher(config=self.config)
        self.stability = StabilityMonitor(config=self.config)
        self.tick = 0

    def reset(self) -> None:
        """Reset the simulation loop to its initial state."""
        self._build_components()

    # ------------------------------------------------------------------
    # Snapshot helpers
    # ------------------------------------------------------------------
    def save_snapshot(self, root: Path | None = None) -> Path:
        """Persist the current world relationships and tick to ``root``."""

        target_root = (
            Path(root).expanduser() if root is not None else self.config.snapshot_root()
        )
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
        self.telemetry.record_stability_metrics(self.stability.latest_metrics())
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
        self.tick += 1
        self.world.tick = self.tick
        console_ops = self.telemetry.drain_console_buffer()
        self.world.apply_console(console_ops)
        self.perturbations.tick(self.world, current_tick=self.tick)
        actions = self.policy.decide(self.world, self.tick)
        self.world.apply_actions(actions)
        self.world.resolve_affordances(current_tick=self.tick)
        episode_span = max(1, self.observations.hybrid_cfg.time_ticks_per_day)
        for snapshot in self.world.agents.values():
            snapshot.episode_tick = (snapshot.episode_tick + 1) % episode_span
        terminated = self.lifecycle.evaluate(self.world, tick=self.tick)
        rewards = self.rewards.compute(self.world, terminated)
        reward_breakdown = self.rewards.latest_reward_breakdown()
        self.policy.post_step(rewards, terminated)
        observations = self.observations.build_batch(self.world, terminated)
        self.policy.flush_transitions(observations)
        policy_snapshot = self.policy.latest_policy_snapshot()
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
        )
        self.telemetry.record_stability_metrics(self.stability.latest_metrics())
        return TickArtifacts(observations=observations, rewards=rewards)

    def _derive_seed(self, stream: str) -> int:
        digest = hashlib.sha256(f"{self.config.config_id}:{stream}".encode("utf-8"))
        return int.from_bytes(digest.digest()[:8], "big")
