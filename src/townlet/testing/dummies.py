"""Testing dummies implementing the public ports."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from townlet.factories.registry import register
from townlet.ports.policy import PolicyBackend
from townlet.ports.telemetry import TelemetrySink
from townlet.ports.world import WorldRuntime


class DummyWorld(WorldRuntime):
    """Minimal deterministic world for unit tests."""

    def __init__(self, agent_count: int = 1) -> None:
        if agent_count <= 0:
            raise ValueError("agent_count must be positive")
        self._agents = tuple(f"agent-{idx}" for idx in range(agent_count))
        self._tick = 0
        self._pending: dict[str, Any] = {}
        self.reset()

    def reset(self, seed: int | None = None) -> None:
        self._tick = 0
        self._pending.clear()

    def tick(self) -> None:
        self._tick += 1

    def agents(self) -> Iterable[str]:
        return self._agents

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        ids = tuple(agent_ids) if agent_ids is not None else self._agents
        return {agent_id: {"tick": self._tick} for agent_id in ids if agent_id in self._agents}

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        self._pending = dict(actions)

    def snapshot(self) -> Mapping[str, Any]:
        return {"tick": self._tick, "pending": dict(self._pending)}


class DummyPolicy(PolicyBackend):
    """Policy backend that mirrors observations back as actions."""

    def __init__(self, action_name: str = "noop") -> None:
        self._action_name = action_name
        self._agent_ids: tuple[str, ...] = ()

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        self._agent_ids = tuple(agent_ids)

    def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self._agent_ids:
            self._agent_ids = tuple(observations.keys())
        return {agent_id: {"action": self._action_name} for agent_id in self._agent_ids}

    def on_episode_end(self) -> None:
        self._agent_ids = ()


class DummyTelemetry(TelemetrySink):
    """Telemetry sink that records invocations for assertions."""

    def __init__(self) -> None:
        self.started = False
        self.events: list[tuple[str, Mapping[str, Any] | None]] = []
        self.metrics: list[tuple[str, float, dict[str, Any]]] = []

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
        if not self.started:
            raise RuntimeError("Telemetry not started")
        self.events.append((name, dict(payload) if payload is not None else None))

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        if not self.started:
            raise RuntimeError("Telemetry not started")
        self.metrics.append((name, float(value), dict(tags)))


@register("world", "dummy")
def _register_dummy_world(**kwargs: Any) -> WorldRuntime:
    return DummyWorld(**kwargs)


@register("policy", "dummy")
def _register_dummy_policy(**kwargs: Any) -> PolicyBackend:
    return DummyPolicy(**kwargs)


@register("telemetry", "dummy")
def _register_dummy_telemetry(**kwargs: Any) -> TelemetrySink:
    return DummyTelemetry()


@register("telemetry", "stub")
def _register_stub_telemetry(**kwargs: Any) -> TelemetrySink:
    return DummyTelemetry()
