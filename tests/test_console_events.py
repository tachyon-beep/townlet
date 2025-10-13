from pathlib import Path

from townlet.config import load_config
from townlet.console.handlers import EventStream
from townlet.dto.telemetry import TelemetryEventDTO, TelemetryMetadata
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.world.grid import WorldState


def test_event_stream_receives_published_events() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)
    stream = EventStream()
    stream.connect(publisher)

    world = WorldState.from_config(config)
    events = [
        {
            "event": "affordance_start",
            "agent_id": "alice",
            "object_id": "shower",
            "affordance_id": "use_shower",
        }
    ]

    event = TelemetryEventDTO(
        event_type="loop.tick",
        tick=0,
        payload={
            "tick": 0,
            "world": world,
            "rewards": {},
            "events": events,
            "policy_snapshot": {},
            "kpi_history": False,
            "reward_breakdown": {},
            "stability_inputs": {},
            "perturbations": {},
            "policy_identity": {},
            "possessed_agents": [],
            "social_events": [],
        },
        metadata=TelemetryMetadata(),
    )
    publisher.emit_event(event)
    latest = stream.latest()
    assert latest and latest[0]["event"] == "affordance_start"


def test_event_stream_handles_empty_batch() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)
    stream = EventStream()
    stream.connect(publisher)

    world = WorldState.from_config(config)
    event = TelemetryEventDTO(
        event_type="loop.tick",
        tick=0,
        payload={
            "tick": 0,
            "world": world,
            "rewards": {},
            "events": [],
            "policy_snapshot": {},
            "kpi_history": False,
            "reward_breakdown": {},
            "stability_inputs": {},
            "perturbations": {},
            "policy_identity": {},
            "possessed_agents": [],
            "social_events": [],
        },
        metadata=TelemetryMetadata(),
    )
    publisher.emit_event(event)
    assert stream.latest() == []


def test_console_event_ingestion_handles_router_payload() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)

    payload = {
        "command": {
            "name": "snapshot",
            "args": [],
            "kwargs": {},
            "cmd_id": "cmd-123",
            "issuer": "viewer",
        },
        "result": {
            "name": "snapshot",
            "status": "ok",
            "result": {"tick": 1},
            "cmd_id": "cmd-123",
            "issuer": "viewer",
            "tick": 5,
            "latency_ms": 3,
        },
    }
    event = TelemetryEventDTO(
        event_type="console.result",
        tick=5,
        payload=payload,
        metadata=TelemetryMetadata(),
    )
    publisher.emit_event(event)

    results = publisher.latest_console_results()
    assert results, "expected console result to be ingested"
    recorded = results[-1]
    assert recorded["name"] == "snapshot"
    assert recorded["status"] == "ok"
    assert recorded["result"] == {"tick": 1}
    assert recorded["cmd_id"] == "cmd-123"
    assert recorded["issuer"] == "viewer"
    assert recorded["tick"] == 5


def test_console_event_ingestion_handles_flat_payload() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)

    payload = {
        "name": "snapshot",
        "status": "ok",
        "result": {"tick": 2},
        "cmd_id": "legacy-1",
        "issuer": "viewer",
        "tick": 9,
    }
    event = TelemetryEventDTO(
        event_type="console.result",
        tick=9,
        payload=payload,
        metadata=TelemetryMetadata(),
    )
    publisher.emit_event(event)

    results = publisher.latest_console_results()
    assert results, "expected console result to be ingested"
    recorded = results[-1]
    assert recorded["name"] == "snapshot"
    assert recorded["status"] == "ok"
    assert recorded["result"] == {"tick": 2}
    assert recorded["cmd_id"] == "legacy-1"
    assert recorded["tick"] == 9
