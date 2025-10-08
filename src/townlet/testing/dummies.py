"""Minimal dummy implementations useful for tests."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from townlet.factories.registry import register
from townlet.ports.policy import PolicyBackend
from townlet.ports.telemetry import TelemetrySink
from townlet.ports.world import WorldRuntime


class DummyWorld(WorldRuntime):
    """In-memory world used for fast tests."""

    def __init__(self, *, agent_ids: Iterable[str] | None = None) -> None:
        self._agent_ids = tuple(agent_ids or ("agent-0",))
        self._tick = 0
        self._last_actions: dict[str, Any] = {}

    def reset(self, seed: int | None = None) -> None:
        self._tick = 0
        self._last_actions.clear()

    def tick(self) -> None:
        self._tick += 1

    def agents(self) -> Iterable[str]:
        return list(self._agent_ids)

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        targets = list(agent_ids) if agent_ids is not None else list(self._agent_ids)
        payload = {agent_id: {"tick": self._tick} for agent_id in targets}
        payload["__meta__"] = {"tick": self._tick}
        return payload

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        self._last_actions = dict(actions)

    def snapshot(self) -> Mapping[str, Any]:
        return {"tick": self._tick, "actions": dict(self._last_actions)}


class DummyPolicy(PolicyBackend):
    """Policy that always emits a no-op action."""

    def __init__(self) -> None:
        self._agent_ids: list[str] = []
        self.decisions: list[Mapping[str, Any]] = []

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        self._agent_ids = list(agent_ids)

    def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]:
        actions = {agent_id: {"kind": "noop", "tick": observations.get("__meta__", {}).get("tick", 0)} for agent_id in self._agent_ids}
        self.decisions.append(actions)
        return actions

    def on_episode_end(self) -> None:
        self._agent_ids = []


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
        self.events.append((name, payload))

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        self.metrics.append((name, float(value), dict(tags)))


@register("world", "dummy")
def _build_dummy_world(*, cfg: Any | None = None, **options: Any) -> DummyWorld:
    agent_ids = options.get("agents") if isinstance(options, Mapping) else None
    return DummyWorld(agent_ids=agent_ids)


@register("policy", "dummy")
def _build_dummy_policy(*, cfg: Any | None = None, **options: Any) -> DummyPolicy:
    return DummyPolicy()


@register("telemetry", "dummy")
@register("telemetry", "stub")
def _build_dummy_telemetry(*, cfg: Any | None = None, **options: Any) -> DummyTelemetry:
    return DummyTelemetry()


__all__ = ["DummyPolicy", "DummyTelemetry", "DummyWorld"]
