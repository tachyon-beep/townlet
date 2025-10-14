"""Unit tests for RivalryTracker.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
"""

from __future__ import annotations

from townlet.stability.analyzers.rivalry import RivalryTracker


def test_rivalry_tracker_no_events() -> None:
    """Tracker should handle no rivalry events."""
    tracker = RivalryTracker(alert_limit=5, intensity_threshold=0.8)

    metrics = tracker.analyze(tick=1, rivalry_events=None)
    alert = tracker.check_alert()

    assert metrics["rivalry_events"] == []
    assert alert is None


def test_rivalry_tracker_low_intensity() -> None:
    """Tracker should not alert for low-intensity events."""
    tracker = RivalryTracker(alert_limit=5, intensity_threshold=0.8)

    metrics = tracker.analyze(
        tick=1,
        rivalry_events=[
            {"intensity": 0.5, "agent_a": "alice", "agent_b": "bob"},
            {"intensity": 0.6, "agent_a": "alice", "agent_b": "carol"},
            {"intensity": 0.7, "agent_a": "bob", "agent_b": "carol"},
        ],
    )
    alert = tracker.check_alert()

    assert len(metrics["rivalry_events"]) == 3
    assert alert is None, "Low-intensity events should not trigger alert"


def test_rivalry_tracker_high_intensity_spike() -> None:
    """Tracker should alert when high-intensity events >= threshold."""
    tracker = RivalryTracker(alert_limit=5, intensity_threshold=0.8)

    # Create 6 high-intensity events (above threshold)
    high_intensity_events = [
        {"intensity": 1.0, "agent_a": "alice", "agent_b": "bob"},
        {"intensity": 0.9, "agent_a": "alice", "agent_b": "carol"},
        {"intensity": 0.85, "agent_a": "bob", "agent_b": "dave"},
        {"intensity": 1.2, "agent_a": "carol", "agent_b": "eve"},
        {"intensity": 0.95, "agent_a": "dave", "agent_b": "eve"},
        {"intensity": 0.8, "agent_a": "alice", "agent_b": "dave"},
    ]

    metrics = tracker.analyze(tick=1, rivalry_events=high_intensity_events)
    alert = tracker.check_alert()

    assert len(metrics["rivalry_events"]) == 6
    assert alert == "rivalry_spike", "6 high-intensity events should trigger alert"


def test_rivalry_tracker_mixed_intensity() -> None:
    """Tracker should only count high-intensity events."""
    tracker = RivalryTracker(alert_limit=3, intensity_threshold=0.8)

    mixed_events = [
        {"intensity": 0.5, "agent_a": "alice", "agent_b": "bob"},  # Low
        {"intensity": 0.9, "agent_a": "alice", "agent_b": "carol"},  # High
        {"intensity": 0.6, "agent_a": "bob", "agent_b": "dave"},  # Low
        {"intensity": 1.0, "agent_a": "carol", "agent_b": "eve"},  # High
        {"intensity": 0.85, "agent_a": "dave", "agent_b": "eve"},  # High
    ]

    metrics = tracker.analyze(tick=1, rivalry_events=mixed_events)
    alert = tracker.check_alert()

    assert len(metrics["rivalry_events"]) == 5  # All events tracked
    assert alert == "rivalry_spike", "3 high-intensity events (out of 5) should trigger alert"


def test_rivalry_tracker_reset() -> None:
    """Reset should clear all state."""
    tracker = RivalryTracker(alert_limit=5, intensity_threshold=0.8)

    # Build up state
    tracker.analyze(
        tick=1,
        rivalry_events=[{"intensity": 1.0, "agent_a": "alice", "agent_b": "bob"}] * 6,
    )
    assert tracker.check_alert() == "rivalry_spike"

    # Reset
    tracker.reset()

    # Should behave as if no previous state
    metrics = tracker.analyze(tick=1, rivalry_events=[])
    alert = tracker.check_alert()

    assert metrics["rivalry_events"] == []
    assert alert is None


def test_rivalry_tracker_export_import_state() -> None:
    """State export/import should preserve tracker state."""
    tracker1 = RivalryTracker(alert_limit=5, intensity_threshold=0.8)

    # Build up state
    events = [{"intensity": 0.9, "agent_a": "alice", "agent_b": "bob"}] * 3
    tracker1.analyze(tick=1, rivalry_events=events)

    # Export state
    state = tracker1.export_state()

    # Create new tracker and import state
    tracker2 = RivalryTracker(alert_limit=5, intensity_threshold=0.8)
    tracker2.import_state(state)

    # Should have same state
    assert len(tracker2._last_rivalry_events) == 3
    assert tracker2._last_high_intensity_count == 3
