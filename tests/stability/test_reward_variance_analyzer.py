"""Unit tests for RewardVarianceAnalyzer.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
"""

from __future__ import annotations

from townlet.stability.analyzers.reward_variance import RewardVarianceAnalyzer


def test_reward_variance_no_samples() -> None:
    """Analyzer should handle no reward samples."""
    analyzer = RewardVarianceAnalyzer(
        window_ticks=1000, max_variance=0.25, min_samples=20
    )

    metrics = analyzer.analyze(tick=1, rewards=None)
    alert = analyzer.check_alert()

    assert metrics["reward_variance"] == 0.0
    assert metrics["reward_mean"] == 0.0
    assert metrics["reward_samples"] == 0
    assert alert is None


def test_reward_variance_low_variance() -> None:
    """Analyzer should not alert for low variance."""
    analyzer = RewardVarianceAnalyzer(
        window_ticks=1000, max_variance=0.25, min_samples=20
    )

    # Add 30 samples with low variance (all around 0.1)
    for tick in range(30):
        metrics = analyzer.analyze(
            tick=tick,
            rewards={
                "alice": 0.1,
                "bob": 0.11,
                "carol": 0.09,
            },
        )

    alert = analyzer.check_alert()

    assert metrics["reward_samples"] == 90  # 30 ticks * 3 agents
    assert metrics["reward_variance"] < 0.01  # Very low variance
    assert alert is None, "Low variance should not trigger alert"


def test_reward_variance_high_variance_spike() -> None:
    """Analyzer should alert when variance exceeds threshold."""
    analyzer = RewardVarianceAnalyzer(
        window_ticks=1000, max_variance=0.25, min_samples=20
    )

    # Add 10 low-variance samples
    for tick in range(10):
        analyzer.analyze(
            tick=tick,
            rewards={"alice": 0.1, "bob": 0.1},
        )

    # Add 10 high-variance samples
    high_variance_rewards = [
        {"alice": 2.0, "bob": -1.5},
        {"alice": -0.8, "bob": 1.8},
        {"alice": 1.5, "bob": -1.0},
        {"alice": -1.2, "bob": 2.2},
        {"alice": 1.9, "bob": -0.9},
        {"alice": -0.7, "bob": 1.7},
        {"alice": 1.4, "bob": -1.1},
        {"alice": -1.3, "bob": 2.1},
        {"alice": 1.8, "bob": -0.8},
        {"alice": -0.6, "bob": 1.6},
    ]

    for tick_offset, rewards in enumerate(high_variance_rewards, start=10):
        metrics = analyzer.analyze(tick=tick_offset, rewards=rewards)

    alert = analyzer.check_alert()

    assert metrics["reward_samples"] >= 20  # Sufficient samples
    assert metrics["reward_variance"] > 0.25  # High variance
    assert alert == "reward_variance_spike", "High variance should trigger alert"


def test_reward_variance_insufficient_samples() -> None:
    """Analyzer should not alert without sufficient samples."""
    analyzer = RewardVarianceAnalyzer(
        window_ticks=1000, max_variance=0.25, min_samples=20
    )

    # Add only 10 samples with high variance
    for tick in range(5):
        analyzer.analyze(
            tick=tick,
            rewards={"alice": 2.0, "bob": -1.5},
        )

    alert = analyzer.check_alert()

    # Even with high variance, should not alert due to insufficient samples
    assert alert is None, "Insufficient samples should not trigger alert"


def test_reward_variance_window_pruning() -> None:
    """Analyzer should prune old samples outside window."""
    analyzer = RewardVarianceAnalyzer(
        window_ticks=100, max_variance=0.25, min_samples=20
    )

    # Add 50 samples with low variance
    for tick in range(50):
        analyzer.analyze(
            tick=tick,
            rewards={"alice": 0.1, "bob": 0.1},
        )

    # Jump far ahead (outside window)
    metrics = analyzer.analyze(
        tick=200,
        rewards={"alice": 0.1, "bob": 0.1},
    )

    # Should only have the latest 2 samples (tick 200)
    assert metrics["reward_samples"] == 2


def test_reward_variance_reset() -> None:
    """Reset should clear all state."""
    analyzer = RewardVarianceAnalyzer(
        window_ticks=1000, max_variance=0.25, min_samples=20
    )

    # Build up state
    for tick in range(30):
        analyzer.analyze(
            tick=tick,
            rewards={"alice": 2.0, "bob": -1.5},
        )
    assert analyzer.check_alert() == "reward_variance_spike"

    # Reset
    analyzer.reset()

    # Should behave as if no previous state
    metrics = analyzer.analyze(tick=1, rewards=None)
    alert = analyzer.check_alert()

    assert metrics["reward_variance"] == 0.0
    assert metrics["reward_samples"] == 0
    assert alert is None


def test_reward_variance_export_import_state() -> None:
    """State export/import should preserve analyzer state."""
    analyzer1 = RewardVarianceAnalyzer(
        window_ticks=1000, max_variance=0.25, min_samples=20
    )

    # Build up state
    for tick in range(10):
        analyzer1.analyze(
            tick=tick,
            rewards={"alice": 0.5, "bob": 0.6},
        )

    # Export state
    state = analyzer1.export_state()

    # Create new analyzer and import state
    analyzer2 = RewardVarianceAnalyzer(
        window_ticks=1000, max_variance=0.25, min_samples=20
    )
    analyzer2.import_state(state)

    # Should have same state
    assert len(analyzer2._reward_samples) == 20  # 10 ticks * 2 agents
    assert analyzer2._last_variance == analyzer1._last_variance
    assert analyzer2._last_mean == analyzer1._last_mean
    assert analyzer2._last_sample_count == analyzer1._last_sample_count
