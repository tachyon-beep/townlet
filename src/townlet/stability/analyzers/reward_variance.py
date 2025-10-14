"""Reward variance analyzer - detects excessive reward variance spikes.

Tracks rolling window of reward samples and triggers alerts when
variance exceeds the threshold with sufficient sample size.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
Extracted from: monitor.py lines 192-201, 388-412
"""

from __future__ import annotations

from collections import deque
from typing import Any


class RewardVarianceAnalyzer:
    """Analyzes reward variance across a rolling window.

    Monitors per-agent rewards and triggers an alert when variance
    exceeds the threshold with sufficient samples.

    Alert triggered: "reward_variance_spike"
    Threshold: variance > 0.25 with >= 20 samples
    Window: 1000 ticks

    State:
        - reward_samples: Rolling deque of (tick, reward) tuples

    Example:
        ```python
        analyzer = RewardVarianceAnalyzer(
            window_ticks=1000,
            max_variance=0.25,
            min_samples=20
        )

        # Low variance - no alert
        metrics = analyzer.analyze(
            tick=1,
            rewards={"alice": 0.1, "bob": 0.12, "carol": 0.11}
        )
        alert = analyzer.check_alert()  # None

        # High variance spike - alert
        metrics = analyzer.analyze(
            tick=2,
            rewards={"alice": 1.5, "bob": -0.8, "carol": 2.0}
        )
        alert = analyzer.check_alert()  # "reward_variance_spike"
        ```
    """

    def __init__(
        self,
        *,
        window_ticks: int = 1000,
        max_variance: float = 0.25,
        min_samples: int = 20,
    ) -> None:
        """Initialize reward variance analyzer.

        Args:
            window_ticks: Size of rolling window in ticks
            max_variance: Variance threshold to trigger alert
            min_samples: Minimum samples required before checking variance
        """
        self._window_ticks = window_ticks
        self._max_variance = max_variance
        self._min_samples = min_samples
        self._reward_samples: deque[tuple[int, float]] = deque()
        self._last_variance = 0.0
        self._last_mean = 0.0
        self._last_sample_count = 0

    def analyze(
        self,
        *,
        tick: int,
        rewards: dict[str, float] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compute reward variance metrics.

        Args:
            tick: Current simulation tick
            rewards: Per-agent reward dict
            **kwargs: Ignored (for protocol compatibility)

        Returns:
            Dict with variance, mean, and sample count
        """
        # Add new reward samples
        if rewards:
            for reward in rewards.values():
                if isinstance(reward, (int, float)):
                    self._reward_samples.append((tick, float(reward)))

        # Remove samples outside window
        cutoff = tick - self._window_ticks
        while self._reward_samples and self._reward_samples[0][0] < cutoff:
            self._reward_samples.popleft()

        # Calculate variance
        if len(self._reward_samples) >= 2:
            values = [r for _, r in self._reward_samples]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            self._last_variance = variance
            self._last_mean = mean
            self._last_sample_count = len(values)
        else:
            self._last_variance = 0.0
            self._last_mean = 0.0
            self._last_sample_count = len(self._reward_samples)

        return {
            "reward_variance": self._last_variance,
            "reward_mean": self._last_mean,
            "reward_samples": self._last_sample_count,
        }

    def check_alert(self) -> str | None:
        """Check if reward variance exceeds threshold.

        Returns:
            "reward_variance_spike" if variance > max_variance with sufficient samples
            None otherwise
        """
        if (
            self._last_sample_count >= self._min_samples
            and self._last_variance > self._max_variance
        ):
            return "reward_variance_spike"
        return None

    def reset(self) -> None:
        """Reset analyzer state for new simulation."""
        self._reward_samples.clear()
        self._last_variance = 0.0
        self._last_mean = 0.0
        self._last_sample_count = 0

    def export_state(self) -> dict[str, Any]:
        """Export state for snapshotting.

        Returns:
            Dict with reward_samples, last_variance, last_mean, last_sample_count
        """
        return {
            "reward_samples": list(self._reward_samples),
            "last_variance": self._last_variance,
            "last_mean": self._last_mean,
            "last_sample_count": self._last_sample_count,
        }

    def import_state(self, state: dict[str, Any]) -> None:
        """Import state from snapshot.

        Args:
            state: State dict from export_state()
        """
        samples = state.get("reward_samples")
        if isinstance(samples, list):
            self._reward_samples = deque(
                (int(t), float(r))
                for t, r in samples
                if isinstance(t, int) and isinstance(r, (int, float))
            )
        else:
            self._reward_samples = deque()

        variance = state.get("last_variance")
        if isinstance(variance, (int, float)):
            self._last_variance = float(variance)
        else:
            self._last_variance = 0.0

        mean = state.get("last_mean")
        if isinstance(mean, (int, float)):
            self._last_mean = float(mean)
        else:
            self._last_mean = 0.0

        sample_count = state.get("last_sample_count")
        if isinstance(sample_count, int):
            self._last_sample_count = sample_count
        else:
            self._last_sample_count = 0
