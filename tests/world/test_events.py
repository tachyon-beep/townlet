from __future__ import annotations

from townlet.world.events import Event, EventDispatcher


def test_event_to_dict_contains_required_fields() -> None:
    event = Event(type="domain.rivalry.started", payload={"agent_a": "alice"}, tick=5, ts=1.5)

    serialised = event.to_dict()
    assert serialised["type"] == "domain.rivalry.started"
    assert serialised["payload"] == {"agent_a": "alice"}
    assert serialised["tick"] == 5
    assert serialised["ts"] == 1.5


def test_dispatcher_buffers_and_drains_events() -> None:
    dispatcher = EventDispatcher()
    seen: list[Event] = []
    dispatcher.register(seen.append)

    created = dispatcher.emit(type="system.tick", payload={"tick": 10}, tick=10, ts=2.0)

    assert len(dispatcher) == 1
    assert seen == [created]

    drained = dispatcher.drain()
    assert drained == [created]
    assert len(dispatcher) == 0


def test_dispatcher_clear_discards_events() -> None:
    dispatcher = EventDispatcher()
    dispatcher.emit(type="console.result", payload={"result": "ok"})

    dispatcher.clear()
    assert dispatcher.drain() == []
