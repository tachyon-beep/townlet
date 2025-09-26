from pathlib import Path

import pytest

from townlet.config import load_config, NarrationThrottleConfig
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
    publisher.publish_tick(
        tick=0,
        world=world,
        observations={},
        rewards={},
        events=[event],
    )
    narrations = publisher.latest_narrations()
    assert len(narrations) == 1
    assert narrations[0]["category"] == "queue_conflict"

    # Within cooldown window, narration should be suppressed.
    publisher.publish_tick(
        tick=2,
        world=world,
        observations={},
        rewards={},
        events=[event],
    )
    assert publisher.latest_narrations() == []

    # Priority reason bypasses cooldown.
    priority_event = dict(event)
    priority_event["reason"] = "ghost_step"
    publisher.publish_tick(
        tick=3,
        world=world,
        observations={},
        rewards={},
        events=[priority_event],
    )
    narrations = publisher.latest_narrations()
    assert len(narrations) == 1
    assert narrations[0]["data"]["reason"] == "ghost_step"
