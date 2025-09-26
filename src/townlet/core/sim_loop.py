"""Top-level simulation loop wiring.

The loop follows the order defined in docs/HIGH_LEVEL_DESIGN.md and delegates to
feature-specific subsystems. Each dependency is a thin façade around the actual
implementation, allowing tests to substitute stubs while the real code evolves.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from townlet.config import SimulationConfig
from townlet.lifecycle.manager import LifecycleManager
from townlet.observations.builder import ObservationBuilder
from townlet.policy.runner import PolicyRuntime
from townlet.rewards.engine import RewardEngine
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.stability.monitor import StabilityMonitor
from townlet.snapshots import (
    SnapshotManager,
    apply_snapshot_to_telemetry,
    apply_snapshot_to_world,
    snapshot_from_world,
)
from townlet.telemetry.publisher import TelemetryPublisher
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
        self._build_components()

    def _build_components(self) -> None:
        self.world = WorldState.from_config(self.config)
        self.lifecycle = LifecycleManager(config=self.config)
        self.perturbations = PerturbationScheduler(config=self.config)
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
    def save_snapshot(self, root: Path) -> Path:
        """Persist the current world relationships and tick to ``root``."""

        manager = SnapshotManager(root=root)
        state = snapshot_from_world(
            self.config,
            self.world,
            lifecycle=self.lifecycle,
            telemetry=self.telemetry,
            perturbations=self.perturbations,
        )
        return manager.save(state)

    def load_snapshot(self, path: Path) -> None:
        """Restore world relationships and tick from the snapshot at ``path``."""

        manager = SnapshotManager(root=path.parent)
        state = manager.load(path, self.config)
        self.policy.reset_state()
        self.perturbations.reset_state()
        apply_snapshot_to_world(
            self.world,
            state,
            lifecycle=self.lifecycle,
        )
        apply_snapshot_to_telemetry(self.telemetry, state)
        self.perturbations.import_state(state.perturbations)
        self.tick = state.tick

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
        terminated = self.lifecycle.evaluate(self.world, tick=self.tick)
        rewards = self.rewards.compute(self.world, terminated)
        self.policy.post_step(rewards, terminated)
        observations = self.observations.build_batch(self.world, terminated)
        self.policy.flush_transitions(observations)
        events = self.world.drain_events()
        self.telemetry.publish_tick(
            tick=self.tick,
            world=self.world,
            observations=observations,
            rewards=rewards,
            events=events,
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
        )
        return TickArtifacts(observations=observations, rewards=rewards)
