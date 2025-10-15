"""Unit tests for StarvationDetector.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
"""

from __future__ import annotations

from townlet.stability.analyzers.starvation import StarvationDetector


def test_starvation_no_hunger_data() -> None:
    """Detector should handle no hunger data."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    metrics = detector.analyze(tick=1, hunger_levels=None, terminated=None)
    alert = detector.check_alert()

    assert metrics["starvation_incidents"] == 0
    assert alert is None


def test_starvation_healthy_agents() -> None:
    """Detector should not trigger for healthy agents."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    # All agents have healthy hunger levels
    for tick in range(200):
        metrics = detector.analyze(
            tick=tick,
            hunger_levels={
                "alice": 0.8,
                "bob": 0.9,
                "carol": 0.7,
            },
            terminated={},
        )

    alert = detector.check_alert()

    assert metrics["starvation_incidents"] == 0
    assert alert is None


def test_starvation_short_hunger_spike() -> None:
    """Detector should not trigger for brief hunger spikes."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    # Agent hungry for 50 ticks (below min_duration)
    for tick in range(50):
        metrics = detector.analyze(
            tick=tick,
            hunger_levels={"alice": 0.15},
            terminated={},
        )

    # Agent recovers
    metrics = detector.analyze(
        tick=50,
        hunger_levels={"alice": 0.8},
        terminated={},
    )

    alert = detector.check_alert()

    assert metrics["starvation_incidents"] == 0
    assert alert is None


def test_starvation_sustained_incident() -> None:
    """Detector should record sustained starvation incident."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    # Agent hungry for 150 ticks (above min_duration)
    for tick in range(150):
        metrics = detector.analyze(
            tick=tick,
            hunger_levels={"alice": 0.15},
            terminated={},
        )

    alert = detector.check_alert()

    # One incident recorded but not enough to alert (need > 5)
    assert metrics["starvation_incidents"] == 1
    assert alert is None


def test_starvation_multiple_incidents_alert() -> None:
    """Detector should alert when incidents exceed threshold."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    # Create 6 sustained starvation incidents (different agents)
    agents = ["alice", "bob", "carol", "dave", "eve", "frank"]
    for i, agent in enumerate(agents):
        start_tick = i * 100
        for tick in range(start_tick, start_tick + 101):
            metrics = detector.analyze(
                tick=tick,
                hunger_levels={agent: 0.15},
                terminated={},
            )

    alert = detector.check_alert()

    assert metrics["starvation_incidents"] == 6  # 6 incidents
    assert alert == "starvation_spike", "6 incidents should trigger alert (threshold is 5)"


def test_starvation_recovery_clears_streak() -> None:
    """Detector should clear streak when agent recovers."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    # Agent hungry for 50 ticks
    for tick in range(50):
        detector.analyze(
            tick=tick,
            hunger_levels={"alice": 0.15},
            terminated={},
        )

    # Agent recovers for 10 ticks
    for tick in range(50, 60):
        detector.analyze(
            tick=tick,
            hunger_levels={"alice": 0.8},
            terminated={},
        )

    # Agent hungry again for 50 more ticks
    for tick in range(60, 110):
        metrics = detector.analyze(
            tick=tick,
            hunger_levels={"alice": 0.15},
            terminated={},
        )

    alert = detector.check_alert()

    # Should not have incident (streak was reset)
    assert metrics["starvation_incidents"] == 0
    assert alert is None


def test_starvation_termination_clears_state() -> None:
    """Detector should clear agent state on termination."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    # Agent hungry for 150 ticks (creates incident)
    for tick in range(150):
        detector.analyze(
            tick=tick,
            hunger_levels={"alice": 0.15},
            terminated={},
        )

    # Agent terminates
    metrics = detector.analyze(
        tick=150,
        hunger_levels={},
        terminated={"alice": True},
    )

    # Incident is still recorded but agent streak should be cleared
    assert metrics["starvation_incidents"] == 1
    assert "alice" not in detector._starvation_streaks
    assert "alice" not in detector._starvation_active


def test_starvation_window_pruning() -> None:
    """Detector should prune old incidents outside window."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=1000,  # Small window for testing
max_incidents=5,
    )

    # Create incident at tick 0-100
    for tick in range(101):
        detector.analyze(
            tick=tick,
            hunger_levels={"alice": 0.15},
            terminated={},
        )

    # Jump far ahead (outside window)
    metrics = detector.analyze(
        tick=2000,
        hunger_levels={},
        terminated={},
    )

    # Old incident should be pruned
    assert metrics["starvation_incidents"] == 0


def test_starvation_disabled_threshold() -> None:
    """Detector with max_incidents < 0 should never alert."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=-1,  # Disabled
    )

    # Create many incidents
    for i in range(10):
        start_tick = i * 100
        for tick in range(start_tick, start_tick + 101):
            detector.analyze(
                tick=tick,
                hunger_levels={f"agent_{i}": 0.15},
                terminated={},
            )

    alert = detector.check_alert()

    # Should never alert (disabled)
    assert alert is None


def test_starvation_reset() -> None:
    """Reset should clear all state."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    # Build up state
    for i in range(6):
        start_tick = i * 100
        for tick in range(start_tick, start_tick + 101):
            detector.analyze(
                tick=tick,
                hunger_levels={f"agent_{i}": 0.15},
                terminated={},
            )
    assert detector.check_alert() == "starvation_spike"

    # Reset
    detector.reset()

    # Should behave as if no previous state
    metrics = detector.analyze(tick=1, hunger_levels=None, terminated=None)
    alert = detector.check_alert()

    assert metrics["starvation_incidents"] == 0
    assert alert is None


def test_starvation_export_import_state() -> None:
    """State export/import should preserve detector state."""
    detector1 = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    # Build up state
    for tick in range(50):
        detector1.analyze(
            tick=tick,
            hunger_levels={"alice": 0.15, "bob": 0.10},
            terminated={},
        )

    # Export state
    state = detector1.export_state()

    # Create new detector and import state
    detector2 = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )
    detector2.import_state(state)

    # Should have same state
    assert detector2._starvation_streaks == detector1._starvation_streaks
    assert detector2._starvation_active == detector1._starvation_active
    assert list(detector2._starvation_incidents) == list(detector1._starvation_incidents)


def test_starvation_exact_threshold_boundary() -> None:
    """Detector should handle exact threshold boundary correctly."""
    detector = StarvationDetector(
        hunger_threshold=0.2,
        min_duration_ticks=100,
        window_ticks=10000,
        max_incidents=5,
    )

    # Agent at exact threshold
    for tick in range(150):
        metrics = detector.analyze(
            tick=tick,
            hunger_levels={"alice": 0.2},  # Exactly at threshold
            terminated={},
        )

    alert = detector.check_alert()

    # Hunger <= threshold should trigger incident
    assert metrics["starvation_incidents"] == 1
    assert alert is None
