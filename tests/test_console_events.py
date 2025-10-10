from pathlib import Path

from townlet.config import load_config
from townlet.console.handlers import EventStream
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

    publisher.emit_event(
        "loop.tick",
        {
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
    )
    latest = stream.latest()
    assert latest and latest[0]["event"] == "affordance_start"


def test_event_stream_handles_empty_batch() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)
    stream = EventStream()
    stream.connect(publisher)

    world = WorldState.from_config(config)
    publisher.emit_event(
        "loop.tick",
        {
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
    )
    assert stream.latest() == []
