"""Option thrash detector - detects excessive option switching.

Tracks rolling window of option switch counts and triggers alerts when
switching rate exceeds the threshold.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
Extracted from: monitor.py lines 166-190, 423-449
"""

from __future__ import annotations

from collections import deque
from typing import Any

from townlet.utils.coerce import coerce_int


class OptionThrashDetector:
    """Analyzes option switching rates across a rolling window.

    Monitors per-agent option switch counts and triggers an alert when
    the mean switching rate exceeds the threshold.

    Alert triggered: "option_thrashing"
    Threshold: mean > 0.4 switches/tick with >= 20 samples
    Window: 1000 ticks

    State:
        - option_samples: Rolling deque of (tick, switch_count) tuples

    Example:
        ```python
        detector = OptionThrashDetector(
            window_ticks=1000,
            max_thrash_rate=0.4,
            min_samples=20
        )

        # Low switching - no alert
        metrics = detector.analyze(
            tick=1,
            option_switch_counts={"alice": 0, "bob": 0, "carol": 0}
        )
        alert = detector.check_alert()  # None

        # High switching rate - alert
        metrics = detector.analyze(
            tick=2,
            option_switch_counts={"alice": 3, "bob": 2, "carol": 4}
        )
        alert = detector.check_alert()  # "option_thrashing"
        ```
    """

    def __init__(
        self,
        *,
        window_ticks: int = 1000,
        max_thrash_rate: float = 0.4,
        min_samples: int = 20,
    ) -> None:
        """Initialize option thrash detector.

        Args:
            window_ticks: Size of rolling window in ticks
            max_thrash_rate: Mean switching rate threshold to trigger alert
            min_samples: Minimum samples required before checking rate
        """
        self._window_ticks = window_ticks
        self._max_thrash_rate = max_thrash_rate
        self._min_samples = min_samples
        self._option_samples: deque[tuple[int, int]] = deque()
        self._last_mean = 0.0
        self._last_sample_count = 0

    def analyze(
        self,
        *,
        tick: int,
        option_switch_counts: dict[str, int] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compute option switching metrics.

        Args:
            tick: Current simulation tick
            option_switch_counts: Per-agent switch count dict
            **kwargs: Ignored (for protocol compatibility)

        Returns:
            Dict with option_thrash_mean and option_samples
        """
        # Add new option samples
        if option_switch_counts:
            for count in option_switch_counts.values():
                switch_count = coerce_int(count)
                self._option_samples.append((tick, switch_count))

        # Remove samples outside window
        cutoff = tick - self._window_ticks
        while self._option_samples and self._option_samples[0][0] < cutoff:
            self._option_samples.popleft()

        # Calculate mean
        if self._option_samples:
            values = [switch_count for _, switch_count in self._option_samples]
            self._last_mean = sum(values) / len(values)
            self._last_sample_count = len(values)
        else:
            self._last_mean = 0.0
            self._last_sample_count = 0

        return {
            "option_thrash_mean": self._last_mean,
            "option_samples": self._last_sample_count,
        }

    def check_alert(self) -> str | None:
        """Check if option switching rate exceeds threshold.

        Returns:
            "option_thrashing" if mean > max_thrash_rate with sufficient samples
            None otherwise
        """
        if (
            self._last_sample_count >= self._min_samples
            and self._last_mean > self._max_thrash_rate
        ):
            return "option_thrashing"
        return None

    def reset(self) -> None:
        """Reset detector state for new simulation."""
        self._option_samples.clear()
        self._last_mean = 0.0
        self._last_sample_count = 0

    def export_state(self) -> dict[str, Any]:
        """Export state for snapshotting.

        Returns:
            Dict with option_samples, last_mean, last_sample_count
        """
        return {
            "option_samples": list(self._option_samples),
            "last_mean": self._last_mean,
            "last_sample_count": self._last_sample_count,
        }

    def import_state(self, state: dict[str, Any]) -> None:
        """Import state from snapshot.

        Args:
            state: State dict from export_state()
        """
        samples = state.get("option_samples")
        if isinstance(samples, list):
            self._option_samples = deque(
                (int(t), int(c))
                for t, c in samples
                if isinstance(t, int) and isinstance(c, int)
            )
        else:
            self._option_samples = deque()

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
