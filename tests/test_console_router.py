from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.console.command import ConsoleCommandEnvelope
from townlet.orchestration import ConsoleRouter
from townlet.ports.telemetry import TelemetrySink
from townlet.ports.world import WorldRuntime


class _StubWorld(WorldRuntime):
    def __init__(self) -> None:
        self.snapshots: list[dict[str, Any]] = []

    def reset(self, seed: int | None = None) -> None:  # pragma: no cover - unused
        _ = seed

    def tick(self) -> None:  # pragma: no cover - unused
        pass

    def agents(self):  # pragma: no cover - unused
        return ()

    def observe(self, agent_ids=None):  # pragma: no cover - unused
        _ = agent_ids
        return {}

    def apply_actions(self, actions: Mapping[str, Any]) -> None:  # pragma: no cover - unused
        _ = actions

    def snapshot(self) -> Mapping[str, Any]:
        payload = {"tick": len(self.snapshots)}
        self.snapshots.append(payload)
        return payload


class _StubTelemetry(TelemetrySink):
    def __init__(self) -> None:
        self.events: list[tuple[str, Mapping[str, Any] | None]] = []
        self.metrics: list[tuple[str, float, Mapping[str, Any]]] = []

    def start(self) -> None:  # pragma: no cover - unused
        pass

    def stop(self) -> None:  # pragma: no cover - unused
        pass

    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None:
        self.events.append((name, payload or {}))

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        self.metrics.append((name, float(value), dict(tags)))


def test_console_router_emits_snapshot_event() -> None:
    world = _StubWorld()
    telemetry = _StubTelemetry()
    router = ConsoleRouter(world=world, telemetry=telemetry)

    envelope = ConsoleCommandEnvelope(name="snapshot", args=[], kwargs={})
    router.enqueue(envelope)
    router.run_pending(tick=7)

    assert telemetry.events, "router should emit telemetry event"
    name, payload = telemetry.events[0]
    assert name == "console.result"
    assert payload["result"]["status"] == "ok"
    assert payload["result"]["tick"] == 7
    assert payload["result"]["result"] == {"tick": 0}


def test_console_router_handles_unknown_command() -> None:
    world = _StubWorld()
    telemetry = _StubTelemetry()
    router = ConsoleRouter(world=world, telemetry=telemetry)

    router.enqueue(ConsoleCommandEnvelope(name="unknown"))
    router.run_pending(tick=1)

    name, payload = telemetry.events[-1]
    assert name == "console.result"
    assert payload["result"]["status"] == "error"
    assert payload["result"]["error"]["code"] == "unknown_command"
