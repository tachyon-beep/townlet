from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.world.queue_manager import QueueManager


def _make_queue_manager() -> QueueManager:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    return QueueManager(config=config)


def test_cooldown_blocks_repeat_entry_and_tracks_metric() -> None:
    queue = _make_queue_manager()
    tick = 0
    assert queue.request_access("shower", "alice", tick) is True
    assert queue.active_agent("shower") == "alice"

    # Release successfully, applying cooldown to the agent/object pair.
    tick = 5
    queue.release("shower", "alice", tick)
    assert queue.active_agent("shower") is None

    # Agent cannot immediately reclaim the reservation; metric should increment.
    assert queue.request_access("shower", "alice", tick) is False
    assert queue.metrics()["cooldown_events"] == 1

    # Advance time so the cooldown expires; access should be granted again.
    tick += queue._settings.cooldown_ticks
    queue.on_tick(tick)
    assert queue.request_access("shower", "alice", tick) is True


@pytest.mark.parametrize("ghost_limit", [1, 2, 3])
def test_ghost_step_promotes_waiter_after_blockages(ghost_limit: int) -> None:
    queue = _make_queue_manager()
    queue._settings.ghost_step_after = ghost_limit
    tick = 0

    assert queue.request_access("stove", "alice", tick) is True
    assert queue.request_access("stove", "bob", tick) is False

    # Simulate repeated blocks; once the limit is hit, the ghost step fires and
    # the waiting agent should take over without accruing cooldown.
    for offset in range(ghost_limit):
        should_release = queue.record_blocked_attempt("stove")
        if should_release:
            queue.release("stove", "alice", tick + offset + 1, success=False)
            break
    else:
        # If no release triggered inside the loop, the limit must be zero; guard against regressions.
        pytest.fail("ghost step was never triggered")

    assert queue.active_agent("stove") == "bob"
    assert queue.metrics()["ghost_step_events"] >= 1


def test_queue_snapshot_reflects_waiting_order() -> None:
    queue = _make_queue_manager()
    tick = 0

    assert queue.request_access("bed", "alice", tick)
    assert not queue.request_access("bed", "bob", tick)
    tick += 1
    assert not queue.request_access("bed", "charlie", tick)

    waiting = queue.queue_snapshot("bed")
    assert waiting == ["bob", "charlie"]

    queue.release("bed", "alice", tick, success=False)
    assert queue.active_agent("bed") == "bob"
    waiting_after = queue.queue_snapshot("bed")
    assert waiting_after == ["charlie"]


def test_queue_performance_metrics_accumulate_time() -> None:
    queue = _make_queue_manager()
    tick = 0
    assert queue.request_access("shower", "alice", tick)
    queue.release("shower", "alice", tick + 1, success=False)
    metrics = queue.performance_metrics()
    assert metrics["requests"] >= 1
    assert metrics["releases"] >= 1
    assert metrics["request_ns"] > 0
    assert metrics["release_ns"] > 0
    assert metrics["assign_calls"] >= 1
