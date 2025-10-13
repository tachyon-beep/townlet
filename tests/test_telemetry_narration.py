from pathlib import Path

from townlet.config import (
    NarrationThrottleConfig,
    PersonalityNarrationConfig,
    RelationshipNarrationConfig,
    load_config,
)
from townlet.dto.telemetry import TelemetryEventDTO, TelemetryMetadata
from townlet.telemetry.narration import NarrationRateLimiter
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.world.grid import WorldState


def test_narration_rate_limiter_enforces_cooldowns() -> None:
    cfg = NarrationThrottleConfig(
        global_cooldown_ticks=5,
        category_cooldown_ticks={"queue_conflict": 10},
        dedupe_window_ticks=0,
        global_window_ticks=50,
        global_window_limit=5,
    )
    limiter = NarrationRateLimiter(cfg)
    limiter.begin_tick(0)
    assert limiter.allow("queue_conflict", message="first")
    for tick in range(1, 10):
        limiter.begin_tick(tick)
        allowed = limiter.allow("queue_conflict", message="repeat")
        if tick < 10:
            assert not allowed
        else:
            assert allowed
            break


def test_narration_rate_limiter_priority_bypass() -> None:
    cfg = NarrationThrottleConfig(
        global_cooldown_ticks=20,
        category_cooldown_ticks={"queue_conflict": 20},
        dedupe_window_ticks=0,
        global_window_ticks=100,
        global_window_limit=5,
    )
    limiter = NarrationRateLimiter(cfg)
    limiter.begin_tick(0)
    assert limiter.allow("queue_conflict", message="start")
    limiter.begin_tick(1)
    assert not limiter.allow("queue_conflict", message="normal")
    limiter.begin_tick(2)
    assert limiter.allow("queue_conflict", message="priority", priority=True)


def test_telemetry_publisher_emits_queue_conflict_narration(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    narration_cfg = config.telemetry.narration.model_copy(
        update={
            "global_cooldown_ticks": 5,
            "category_cooldown_ticks": {"queue_conflict": 5},
            "dedupe_window_ticks": 0,
            "global_window_ticks": 50,
            "global_window_limit": 10,
        }
    )
    config.telemetry = config.telemetry.model_copy(update={"narration": narration_cfg})

    publisher = TelemetryPublisher(config)
    world = WorldState.from_config(config)

    event = {
        "event": "queue_conflict",
        "actor": "alice",
        "rival": "bob",
        "object_id": "shower_1",
        "reason": "handover",
        "queue_length": 2,
        "intensity": 1.5,
    }
    telemetry_event = TelemetryEventDTO(
        event_type="loop.tick",
        tick=0,
        payload={
            "tick": 0,
            "world": world,
            "rewards": {},
            "events": [event],
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
    publisher.emit_event(telemetry_event)
    narrations = publisher.latest_narrations()
    assert len(narrations) == 1
    assert narrations[0]["category"] == "queue_conflict"

    # Within cooldown window, narration should be suppressed.
    telemetry_event = TelemetryEventDTO(
        event_type="loop.tick",
        tick=2,
        payload={
            "tick": 2,
            "world": world,
            "rewards": {},
            "events": [event],
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
    publisher.emit_event(telemetry_event)
    assert publisher.latest_narrations() == []

    # Priority reason bypasses cooldown.
    priority_event = dict(event)
    priority_event["reason"] = "ghost_step"
    telemetry_event = TelemetryEventDTO(
        event_type="loop.tick",
        tick=3,
        payload={
            "tick": 3,
            "world": world,
            "rewards": {},
            "events": [priority_event],
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
    publisher.emit_event(telemetry_event)
    narrations = publisher.latest_narrations()
    assert len(narrations) == 1
    assert narrations[0]["data"]["reason"] == "ghost_step"


def test_relationship_friendship_narration_emits_for_new_tie() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)
    publisher._narration_limiter.begin_tick(10)
    publisher._latest_narrations = []
    publisher._latest_relationship_summary = {}
    updates = [
        {
            "owner": "alice",
            "other": "bob",
            "status": "added",
            "trust": 0.72,
            "familiarity": 0.5,
            "delta": {"trust": 0.72, "familiarity": 0.5},
        }
    ]
    publisher._process_narrations(
        events=[],
        social_events=[],
        relationship_updates=updates,
        tick=10,
    )
    narrations = publisher.latest_narrations()
    assert any(n["category"] == "relationship_friendship" for n in narrations)


def test_relationship_friendship_respects_configured_threshold() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    relationship_cfg = RelationshipNarrationConfig(
        friendship_trust_threshold=0.9,
        friendship_delta_threshold=0.5,
        friendship_priority_threshold=0.95,
        rivalry_avoid_threshold=0.8,
        rivalry_escalation_threshold=0.95,
    )
    config.telemetry = config.telemetry.model_copy(
        update={"relationship_narration": relationship_cfg}
    )
    publisher = TelemetryPublisher(config)
    publisher._narration_limiter.begin_tick(12)
    publisher._latest_narrations = []
    publisher._latest_relationship_summary = {}
    update_payload = {
        "owner": "alice",
        "other": "bob",
        "status": "updated",
        "trust": 0.88,
        "familiarity": 0.4,
        "delta": {"trust": 0.05, "familiarity": 0.05},
    }
    publisher._process_narrations(
        events=[],
        social_events=[],
        relationship_updates=[update_payload],
        tick=12,
    )
    narrations = publisher.latest_narrations()
    assert all(n["category"] != "relationship_friendship" for n in narrations)


def test_relationship_rivalry_narration_tracks_threshold() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)
    publisher._latest_relationship_summary = {
        "alice": {"top_rivals": [{"agent": "bob", "rivalry": 0.92}]}
    }
    publisher._narration_limiter.begin_tick(20)
    publisher._latest_narrations = []
    publisher._process_narrations(
        events=[],
        social_events=[],
        relationship_updates=[],
        tick=20,
    )
    narrations = publisher.latest_narrations()
    rivalry_entries = [n for n in narrations if n["category"] == "relationship_rivalry"]
    assert rivalry_entries
    assert rivalry_entries[0]["priority"] is True


def test_relationship_rivalry_respects_configured_thresholds() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    relationship_cfg = RelationshipNarrationConfig(
        friendship_trust_threshold=0.6,
        friendship_delta_threshold=0.25,
        friendship_priority_threshold=0.9,
        rivalry_avoid_threshold=0.95,
        rivalry_escalation_threshold=0.97,
    )
    config.telemetry = config.telemetry.model_copy(
        update={"relationship_narration": relationship_cfg}
    )
    publisher = TelemetryPublisher(config)
    publisher._latest_relationship_summary = {
        "alice": {"top_rivals": [{"agent": "bob", "rivalry": 0.92}]}
    }
    publisher._narration_limiter.begin_tick(25)
    publisher._latest_narrations = []
    publisher._process_narrations(
        events=[],
        social_events=[],
        relationship_updates=[],
        tick=25,
    )
    narrations = publisher.latest_narrations()
    assert all(n["category"] != "relationship_rivalry" for n in narrations)


def test_social_alert_narrations_for_chat_and_avoidance() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)
    publisher._narration_limiter.begin_tick(30)
    publisher._latest_narrations = []
    social_events = [
        {"type": "chat_failure", "speaker": "alice", "listener": "bob"},
        {"type": "rivalry_avoidance", "agent": "carol", "object": "queue", "reason": "threshold"},
    ]
    publisher._process_narrations(
        events=[],
        social_events=social_events,
        relationship_updates=[],
        tick=30,
    )
    narrations = publisher.latest_narrations()
    categories = [n["category"] for n in narrations]
    assert categories.count("relationship_social_alert") == 2
    priority_flags = [
        n["priority"]
        for n in narrations
        if n["category"] == "relationship_social_alert"
    ]
    assert any(priority_flags)


def test_personality_narration_emits_for_extroversion_chat() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    personality_cfg = config.telemetry.personality_narration.model_copy(
        update={
            "enabled": True,
            "chat_extroversion_threshold": 0.6,
            "chat_priority_threshold": 0.75,
            "chat_quality_threshold": 0.2,
        }
    )
    config.telemetry = config.telemetry.model_copy(
        update={"personality_narration": personality_cfg}
    )
    publisher = TelemetryPublisher(config)
    publisher._latest_personality_snapshot = {
        "avery": {
            "profile": "socialite",
            "traits": {"extroversion": 0.82, "forgiveness": 0.1, "ambition": 0.2},
            "multipliers": {"behaviour": {"conflict_tolerance": 0.7}},
        }
    }
    publisher._narration_limiter.begin_tick(40)
    publisher._latest_narrations = []
    social_events = [
        {
            "type": "chat_success",
            "speaker": "avery",
            "listener": "blair",
            "quality": 0.65,
        }
    ]
    publisher._emit_personality_event_narrations(social_events, tick=40)
    narrations = publisher.latest_narrations()
    assert any(entry["category"] == "personality_event" for entry in narrations)


def test_personality_narration_respects_toggle_and_thresholds() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    personality_cfg = PersonalityNarrationConfig(
        enabled=False,
        chat_extroversion_threshold=0.9,
        chat_priority_threshold=0.95,
        chat_quality_threshold=0.9,
        conflict_tolerance_threshold=0.5,
    )
    config.telemetry = config.telemetry.model_copy(
        update={"personality_narration": personality_cfg}
    )
    publisher = TelemetryPublisher(config)
    publisher._latest_personality_snapshot = {
        "avery": {
            "profile": "socialite",
            "traits": {"extroversion": 0.99, "forgiveness": 0.1, "ambition": 0.2},
            "multipliers": {"behaviour": {"conflict_tolerance": 0.4}},
        }
    }
    publisher._narration_limiter.begin_tick(50)
    publisher._latest_narrations = []
    events = [
        {
            "type": "chat_success",
            "speaker": "avery",
            "listener": "blair",
            "quality": 0.95,
        },
        {
            "type": "rivalry_avoidance",
            "agent": "avery",
            "object": "market",
            "reason": "crowd",
        },
    ]
    publisher._emit_personality_event_narrations(events, tick=50)
    assert not publisher.latest_narrations()
