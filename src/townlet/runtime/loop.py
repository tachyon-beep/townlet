"""Lightweight simulation loop that depends solely on public ports."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.factories.policy_factory import create_policy
from townlet.factories.telemetry_factory import create_telemetry
from townlet.factories.world_factory import create_world
from townlet.ports.policy import PolicyBackend
from townlet.ports.telemetry import TelemetrySink
from townlet.ports.world import WorldRuntime


class SimulationLoop:
    """Tiny orchestration helper coordinating world, policy, and telemetry."""

    def __init__(
        self,
        world_cfg: Mapping[str, Any] | None = None,
        policy_cfg: Mapping[str, Any] | None = None,
        telemetry_cfg: Mapping[str, Any] | None = None,
    ) -> None:
        self.world: WorldRuntime = create_world(world_cfg)
        self.policy: PolicyBackend = create_policy(policy_cfg)
        self.telemetry: TelemetrySink = create_telemetry(telemetry_cfg)

    def run(self, ticks: int, *, seed: int | None = None) -> None:
        """Execute ``ticks`` iterations of the simulation loop."""

        if ticks < 0:
            raise ValueError("ticks must be non-negative")
        self.telemetry.start()
        try:
            self.world.reset(seed)
            agent_ids = tuple(self.world.agents())
            self.policy.on_episode_start(agent_ids)
            for _ in range(ticks):
                observations = self.world.observe()
                actions = self.policy.decide(observations)
                self.world.apply_actions(actions)
                self.world.tick()
                snapshot = self.world.snapshot()
                self.telemetry.emit_event("tick", snapshot)
            self.policy.on_episode_end()
        finally:
            self.telemetry.stop()
