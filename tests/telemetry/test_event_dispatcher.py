from __future__ import annotations

from collections.abc import Mapping

from townlet.telemetry.event_dispatcher import TelemetryEventDispatcher


def test_queue_history_is_bounded() -> None:
    dispatcher = TelemetryEventDispatcher(queue_history_limit=2)
    dispatcher.emit_event("loop.health", {"tick": 1, "queue_metrics": {"cooldown_events": 1}})
    dispatcher.emit_event("loop.health", {"tick": 2, "queue_metrics": {"cooldown_events": 2}})
    dispatcher.emit_event("loop.health", {"tick": 3, "queue_metrics": {"cooldown_events": 3}})

    history = dispatcher.queue_history
    assert len(history) == 2
    assert [entry["tick"] for entry in history] == [2, 3]


def test_rivalry_history_accumulates_from_events() -> None:
    dispatcher = TelemetryEventDispatcher(rivalry_history_limit=3)
    dispatcher.emit_event(
        "rivalry.events",
        {
            "tick": 10,
            "events": [
                {"agent_a": "alice", "agent_b": "bob", "intensity": 0.8},
            ],
        },
    )
    dispatcher.emit_event(
        "loop.tick",
        {
            "tick": 11,
            "events": [
                {"agent_a": "carol", "agent_b": "dan", "intensity": 0.4, "reason": "queue"},
            ],
        },
    )

    history = dispatcher.rivalry_history
    assert len(history) == 2
    assert history[0]["agent_a"] == "alice"
    assert history[1]["agent_b"] == "dan"


def test_possession_event_updates_cache() -> None:
    dispatcher = TelemetryEventDispatcher()
    dispatcher.emit_event("policy.possession", {"agents": ["bob", "alice"]})
    assert dispatcher.possessed_agents == ["alice", "bob"]


def test_subscriber_invoked_for_events() -> None:
    recorder: list[tuple[str, Mapping[str, object]]] = []
    dispatcher = TelemetryEventDispatcher()

    def subscriber(name: str, payload: Mapping[str, object]) -> None:
        recorder.append((name, payload))

    dispatcher.register_subscriber(subscriber)
    dispatcher.emit_event("loop.tick", {"tick": 1})
    dispatcher.emit_event("loop.health", {"tick": 1, "queue_metrics": {}})

    assert len(recorder) == 2
    assert recorder[0][0] == "loop.tick"
    assert recorder[1][0] == "loop.health"
