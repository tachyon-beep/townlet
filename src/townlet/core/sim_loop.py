"""Simplified simulation loop wired against the new ports."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

from townlet.factories.policy_factory import create_policy
from townlet.factories.telemetry_factory import create_telemetry
from townlet.factories.world_factory import create_world
from townlet.ports.policy import PolicyBackend
from townlet.ports.telemetry import TelemetrySink
from townlet.ports.world import WorldRuntime


class SimulationLoopError(RuntimeError):
    """Raised when the simulation loop encounters a fatal error."""


class SimulationLoop:
    """High-level orchestration of the Townlet runtime."""

    def __init__(self, config: Any) -> None:
        self.config = config
        self.world: WorldRuntime = create_world(config)
        self.policy: PolicyBackend = create_policy(config, world=self.world)
        self.telemetry: TelemetrySink = create_telemetry(config)
        self.tick = 0
        self._episode_started = False

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------
    def _ensure_episode(self) -> None:
        if not self._episode_started:
            self.world.reset(getattr(self.config, "seed", None))
            agent_ids = list(self.world.agents())
            self.policy.on_episode_start(agent_ids)
            self._episode_started = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_for(self, max_ticks: int) -> None:
        """Execute ``max_ticks`` iterations of the simulation loop."""

        self.telemetry.start()
        try:
            self._ensure_episode()
            for _ in range(max_ticks):
                self.step()
        finally:
            try:
                if self._episode_started:
                    self.policy.on_episode_end()
            finally:
                self.telemetry.stop()
                self._episode_started = False

    def step(self) -> Mapping[str, Any]:
        """Advance the simulation by a single tick."""

        start = time.perf_counter()
        try:
            self._ensure_episode()
            observations = self.world.observe()
            actions = self.policy.decide(observations)
            self.world.apply_actions(actions)
            self.world.tick()
            snapshot = self.world.snapshot()
            self.tick = _extract_tick(snapshot, fallback=self.tick + 1)
            payload = _normalise_snapshot(snapshot, tick=self.tick)
            duration_ms = (time.perf_counter() - start) * 1000.0
            self.telemetry.emit_event("tick", payload)
            self.telemetry.emit_metric(
                "tick_duration_ms", duration_ms, tick=self.tick
            )
            return observations
        except Exception as exc:  # pragma: no cover - defensive guard
            raise SimulationLoopError(str(exc)) from exc

    def close(self) -> None:
        """Close the simulation loop, stopping telemetry if required."""

        if self._episode_started:
            self.policy.on_episode_end()
            self._episode_started = False
        self.telemetry.stop()


def _normalise_snapshot(snapshot: Mapping[str, Any] | Any, *, tick: int) -> Mapping[str, Any]:
    if isinstance(snapshot, Mapping):
        data = dict(snapshot)
        data.setdefault("tick", tick)
        return data
    return {"data": snapshot, "tick": tick}


def _extract_tick(snapshot: Mapping[str, Any] | Any, *, fallback: int) -> int:
    if isinstance(snapshot, Mapping):
        value = snapshot.get("tick")
        if isinstance(value, int):
            return value
        meta = snapshot.get("meta")
        if isinstance(meta, Mapping):
            meta_value = meta.get("tick")
            if isinstance(meta_value, int):
                return meta_value
    return int(fallback)


__all__ = ["SimulationLoop", "SimulationLoopError"]
