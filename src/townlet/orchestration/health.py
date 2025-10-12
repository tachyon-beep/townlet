"""Health/stability monitoring based on world snapshots and events."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Mapping
from typing import Any

from townlet.ports.telemetry import TelemetrySink


class HealthMonitor:
    """Simple rolling metrics computed from world snapshots/events."""

    def __init__(self, window: int = 100) -> None:
        self._window = max(1, int(window))
        self._queue_lengths: deque[float] = deque(maxlen=self._window)
        self._event_counts: deque[int] = deque(maxlen=self._window)

    def on_tick(self, snapshot: Mapping[str, Any], telemetry: TelemetrySink) -> None:
        tick = int(snapshot.get("tick", 0))
        events: Iterable[Mapping[str, Any]] = snapshot.get("events", [])  # type: ignore[assignment]
        event_list = list(events)
        self._event_counts.append(len(event_list))

        metrics = snapshot.get("metrics", {})
        queue_length = metrics.get("queue_length") if isinstance(metrics, Mapping) else None
        if queue_length is not None:
            try:
                self._queue_lengths.append(float(queue_length))
            except (TypeError, ValueError):  # pragma: no cover - defensive
                pass

        telemetry.emit_metric("world.events.count", float(self._event_counts[-1]), tick=tick)
        telemetry.emit_metric(
            "world.events.avg",
            self._rolling_average(self._event_counts),
            tick=tick,
        )
        if self._queue_lengths:
            telemetry.emit_metric("queue.length.latest", self._queue_lengths[-1], tick=tick)
            telemetry.emit_metric(
                "queue.length.avg",
                self._rolling_average(self._queue_lengths),
                tick=tick,
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _rolling_average(buffer: Iterable[float]) -> float:
        values = list(buffer)
        if not values:
            return 0.0
        return sum(values) / len(values)


__all__ = ["HealthMonitor"]
