"""Helpers for tracking relationship churn and eviction telemetry.

These utilities let the simulation publish per-window counts of relationship
edge evictions so drift or rapid churn can be observed by soak tests and the
operations dashboards.
"""

from __future__ import annotations

from collections import Counter, deque
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Optional


def _advance_window(
    *,
    current_tick: int,
    window_ticks: int,
    window_start: int,
) -> int:
    """Move the window start forward until it covers ``current_tick``."""
    if current_tick < window_start:
        return window_start
    if window_ticks <= 0:
        return window_start
    while current_tick >= window_start + window_ticks:
        window_start += window_ticks
    return window_start


@dataclass
class RelationshipEvictionSample:
    """Aggregated eviction counts captured for a completed window."""

    window_start: int
    window_end: int
    total_evictions: int
    per_owner: dict[str, int]
    per_reason: dict[str, int]

    def to_payload(self) -> dict[str, object]:
        """Serialise the sample into a telemetry-friendly payload."""
        return {
            "window_start": self.window_start,
            "window_end": self.window_end,
            "total": self.total_evictions,
            "owners": dict(self.per_owner),
            "reasons": dict(self.per_reason),
        }


class RelationshipChurnAccumulator:
    """Tracks relationship eviction activity over fixed tick windows."""

    def __init__(
        self,
        *,
        window_ticks: int,
        max_samples: int = 8,
    ) -> None:
        if window_ticks <= 0:
            raise ValueError("window_ticks must be positive")
        if max_samples <= 0:
            raise ValueError("max_samples must be positive")
        self.window_ticks = window_ticks
        self._window_start = 0
        self._per_owner: Counter[str] = Counter()
        self._per_reason: Counter[str] = Counter()
        self._total = 0
        self._history: deque[RelationshipEvictionSample] = deque(maxlen=max_samples)

    def record_eviction(
        self,
        *,
        tick: int,
        owner_id: str,
        evicted_id: str,
        reason: Optional[str] = None,
    ) -> None:
        """Record an eviction event for churn tracking.

        Parameters
        ----------
        tick:
            Simulation tick when the eviction occurred.
        owner_id:
            Agent whose relationship ledger evicted ``evicted_id``.
        evicted_id:
            Agent removed from the ledger (unused for aggregation but captured
            to support future diagnostics).
        reason:
            Optional categorical tag (e.g. ``capacity`` or ``decay``) to aid in
            telemetry analysis. ``None`` is grouped under ``"unknown"``.
        """

        if tick < 0:
            raise ValueError("tick must be non-negative")
        self._roll_window(tick)
        tag = reason or "unknown"
        self._per_owner[owner_id] += 1
        self._per_reason[tag] += 1
        self._total += 1

    def _roll_window(self, tick: int) -> None:
        window_start = _advance_window(
            current_tick=tick,
            window_ticks=self.window_ticks,
            window_start=self._window_start,
        )
        if window_start == self._window_start:
            return
        sample = RelationshipEvictionSample(
            window_start=self._window_start,
            window_end=window_start,
            total_evictions=self._total,
            per_owner=dict(self._per_owner),
            per_reason=dict(self._per_reason),
        )
        if sample.total_evictions:
            self._history.append(sample)
        self._window_start = window_start
        self._per_owner.clear()
        self._per_reason.clear()
        self._total = 0

    def snapshot(self) -> dict[str, object]:
        """Return aggregates for the active window."""
        return {
            "window_start": self._window_start,
            "window_end": self._window_start + self.window_ticks,
            "total": self._total,
            "owners": dict(self._per_owner),
            "reasons": dict(self._per_reason),
        }

    def history(self) -> Iterable[RelationshipEvictionSample]:
        """Return a snapshot of the recorded history."""
        return list(self._history)

    def history_payload(self) -> list[dict[str, object]]:
        """Convert history samples into telemetry payloads."""
        return [sample.to_payload() for sample in self._history]

    def latest_payload(self) -> dict[str, object]:
        """Return the live window payload for telemetry publishing."""
        payload = self.snapshot()
        payload["history"] = self.history_payload()
        return payload

    def ingest_payload(self, payload: dict[str, object]) -> None:
        """Restore the accumulator from an external payload.

        This helper allows soak harnesses to persist state across sessions.
        """

        window_start = int(payload.get("window_start", 0))
        window_end = int(payload.get("window_end", window_start))
        if window_end < window_start:
            raise ValueError("window_end must be >= window_start")
        self._window_start = window_start
        # Derive the active window width in case the payload came from a
        # different configuration.
        self.window_ticks = max(window_end - window_start, 1)
        owners = payload.get("owners", {})
        reasons = payload.get("reasons", {})
        self._per_owner = Counter({str(k): int(v) for k, v in owners.items()})
        self._per_reason = Counter({str(k): int(v) for k, v in reasons.items()})
        self._total = int(payload.get("total", 0))
        history: list[RelationshipEvictionSample] = []
        for entry in payload.get("history", []):
            sample = RelationshipEvictionSample(
                window_start=int(entry.get("window_start", 0)),
                window_end=int(entry.get("window_end", 0)),
                total_evictions=int(entry.get("total", 0)),
                per_owner={str(k): int(v) for k, v in entry.get("owners", {}).items()},
                per_reason={
                    str(k): int(v) for k, v in entry.get("reasons", {}).items()
                },
            )
            history.append(sample)
        maxlen = self._history.maxlen or len(history)
        self._history = deque(history[-maxlen:], maxlen=maxlen)
