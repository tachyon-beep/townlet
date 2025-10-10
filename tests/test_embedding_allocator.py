from pathlib import Path

from townlet.config import load_config
from townlet.observations.builder import ObservationBuilder
from townlet.observations.embedding import EmbeddingAllocator
from townlet.stability.monitor import StabilityMonitor
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.world.grid import AgentSnapshot, WorldState


def make_allocator(*, cooldown: int = 5, max_slots: int = 2) -> EmbeddingAllocator:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.embedding_allocator.cooldown_ticks = cooldown
    config.embedding_allocator.max_slots = max_slots
    config.embedding_allocator.reuse_warning_threshold = 0.1
    return EmbeddingAllocator(config)


def test_allocate_reuses_slot_after_cooldown() -> None:
    allocator = make_allocator(cooldown=3, max_slots=1)
    slot_a = allocator.allocate("alice", tick=0)
    assert slot_a == 0
    allocator.release("alice", tick=1)

    # Before cooldown elapsed: forced reuse expected.
    slot_b = allocator.allocate("bob", tick=2)
    assert slot_b == 0
    metrics = allocator.metrics()
    assert metrics["forced_reuse_count"] == 1
    assert metrics["reuse_warning"]

    allocator.release("bob", tick=5)
    slot_c = allocator.allocate("carol", tick=8)
    assert slot_c == 0
    metrics = allocator.metrics()
    assert metrics["forced_reuse_count"] == 1


def test_allocator_respects_multiple_slots() -> None:
    allocator = make_allocator(cooldown=10, max_slots=2)
    slot_a = allocator.allocate("alice", tick=0)
    slot_b = allocator.allocate("bob", tick=0)
    assert slot_a != slot_b

    allocator.release("alice", tick=1)
    allocator.release("bob", tick=1)

    # New agent should receive the slot with longest cooldown elapsed first.
    slot_c = allocator.allocate("carol", tick=12)
    assert slot_c in {slot_a, slot_b}
    allocator.release("carol", tick=13)
    slot_d = allocator.allocate("dave", tick=13)
    assert slot_d in {slot_a, slot_b}

    metrics = allocator.metrics()
    assert metrics["allocations_total"] == 4


def test_observation_builder_releases_on_termination() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.embedding_allocator.cooldown_ticks = 2
    world = WorldState.from_config(config)
    world.tick = 0
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5},
    )
    builder = ObservationBuilder(config)

    obs = builder.build_batch(world, terminated={})
    alice_obs = obs["alice"]
    assert alice_obs["metadata"]["embedding_slot"] == 0
    assert alice_obs["features"].ndim == 1
    assert world.embedding_allocator.has_assignment("alice")

    world.tick = 3
    builder.build_batch(world, terminated={"alice": True})
    assert not world.embedding_allocator.has_assignment("alice")


def test_telemetry_exposes_allocator_metrics() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.tick = 0
    telemetry = TelemetryPublisher(config)
    telemetry.emit_event(
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

    queue_metrics = telemetry.latest_queue_metrics()
    embedding_metrics = telemetry.latest_embedding_metrics()

    assert queue_metrics is not None
    assert embedding_metrics is not None
    assert "forced_reuse_rate" in embedding_metrics


def test_stability_monitor_sets_alert_on_warning() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    monitor = StabilityMonitor(config)
    monitor.track(
        tick=0,
        rewards={},
        terminated={},
        embedding_metrics={"reuse_warning": True},
        queue_metrics=None,
    )
    assert monitor.latest_alert == "embedding_reuse_warning"


def test_telemetry_records_events() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    telemetry = TelemetryPublisher(config)
    events = [
        {
            "event": "affordance_start",
            "agent_id": "alice",
            "object_id": "shower",
            "affordance_id": "use_shower",
        }
    ]
    telemetry.emit_event(
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
    latest = list(telemetry.latest_events())
    assert latest and latest[0]["event"] == "affordance_start"


def test_stability_alerts_on_affordance_failures() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.stability.affordance_fail_threshold = 0
    monitor = StabilityMonitor(config)
    fail_events = [{"event": "affordance_fail", "agent_id": "alice"}]
    monitor.track(
        tick=0,
        rewards={},
        terminated={},
        queue_metrics=None,
        embedding_metrics=None,
        events=fail_events,
    )
    assert monitor.latest_alert == "affordance_failures_exceeded"
