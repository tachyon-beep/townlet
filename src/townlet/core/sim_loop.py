"""Top-level simulation loop wiring.

The loop follows the order defined in docs/HIGH_LEVEL_DESIGN.md and delegates to
feature-specific subsystems. Each dependency is a thin façade around the actual
implementation, allowing tests to substitute stubs while the real code evolves.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from townlet.config import SimulationConfig
from townlet.lifecycle.manager import LifecycleManager
from townlet.observations.builder import ObservationBuilder
from townlet.policy.runner import PolicyRuntime
from townlet.rewards.engine import RewardEngine
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.stability.monitor import StabilityMonitor
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
        self.world = WorldState.from_config(config)
        self.lifecycle = LifecycleManager(config=config)
        self.perturbations = PerturbationScheduler(config=config)
        self.observations = ObservationBuilder(config=config)
        self.policy = PolicyRuntime(config=config)
        self.rewards = RewardEngine(config=config)
        self.telemetry = TelemetryPublisher(config=config)
        self.stability = StabilityMonitor(config=config)
        self.tick: int = 0

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
            events=self.telemetry.latest_events(),
        )
        return TickArtifacts(observations=observations, rewards=rewards)
