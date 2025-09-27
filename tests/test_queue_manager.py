from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.world.queue_manager import QueueManager


@pytest.fixture()
def queue_manager() -> QueueManager:
    config_path = Path("configs/examples/poc_hybrid.yaml")
    config = load_config(config_path)
    return QueueManager(config)


def test_queue_cooldown_enforced(queue_manager: QueueManager) -> None:
    assert queue_manager.request_access("shower", "alice", tick=0) is True
    queue_manager.release("shower", "alice", tick=10)

    assert queue_manager.request_access("shower", "alice", tick=20) is False
    assert queue_manager.metrics()["cooldown_events"] == 1

    assert queue_manager.request_access("shower", "alice", tick=75) is True


def test_queue_prioritises_wait_time(queue_manager: QueueManager) -> None:
    assert queue_manager.request_access("shower", "alice", tick=0) is True
    assert queue_manager.request_access("shower", "bob", tick=5) is False
    assert queue_manager.request_access("shower", "carol", tick=6) is False

    queue_manager.release("shower", "alice", tick=10)
    assert queue_manager.active_agent("shower") in {"bob", "carol"}
    active_first = queue_manager.active_agent("shower")
    queue_manager.release("shower", active_first, tick=20)
    assert queue_manager.active_agent("shower") in {"bob", "carol"}
    assert queue_manager.active_agent("shower") != active_first
    active_second = queue_manager.active_agent("shower")
    queue_manager.release("shower", active_second, tick=30)
    assert queue_manager.active_agent("shower") is None
    assert queue_manager.queue_snapshot("shower") == []


def test_ghost_step_trigger(queue_manager: QueueManager) -> None:
    starting_events = queue_manager.metrics()["ghost_step_events"]
    assert queue_manager.request_access("shower", "alice", tick=0) is True

    fired = False
    for _ in range(10):
        fired = queue_manager.record_blocked_attempt("shower")
        if fired:
            break

    assert fired is True
    assert queue_manager.metrics()["ghost_step_events"] == starting_events + 1


def test_requeue_to_tail_rotates_agent(queue_manager: QueueManager) -> None:
    queue_manager._settings.ghost_step_after = 1
    assert queue_manager.request_access("shower", "alice", tick=0) is True
    assert queue_manager.request_access("shower", "bob", tick=1) is False
    assert queue_manager.request_access("shower", "carol", tick=2) is False

    # Simulate ghost-step: release current occupant without success and rotate to tail
    queue_manager.release("shower", "alice", tick=3, success=False)
    queue_manager.requeue_to_tail("shower", "alice", tick=3)

    queue = queue_manager.queue_snapshot("shower")
    assert queue[-1] == "alice"
    assert queue_manager.metrics()["rotation_events"] == 1
    active = queue_manager.active_agent("shower")
    assert active in {"bob", "carol"}

    # Re-adding the same agent should not duplicate entries
    queue_manager.requeue_to_tail("shower", "alice", tick=4)
    assert queue_manager.metrics()["rotation_events"] == 1
    queue = queue_manager.queue_snapshot("shower")
    assert queue.count("alice") == 1

def test_record_blocked_attempt_counts_and_triggers(queue_manager: QueueManager) -> None:
    queue_manager._settings.ghost_step_after = 2
    assert queue_manager.record_blocked_attempt("shower") is False
    assert queue_manager.record_blocked_attempt("shower") is True
    assert queue_manager.metrics()["ghost_step_events"] >= 1


def test_cooldown_expiration_clears_entries(queue_manager: QueueManager) -> None:
    queue_manager._settings.cooldown_ticks = 3
    assert queue_manager.request_access("shower", "alice", tick=0)
    queue_manager.release("shower", "alice", tick=0)
    assert queue_manager.request_access("shower", "alice", tick=1) is False
    queue_manager.on_tick(5)
    assert queue_manager.request_access("shower", "alice", tick=6) is True
