"""Promotion gate state tracking."""

from __future__ import annotations

from collections import deque
from typing import Any, Mapping

from townlet.config import SimulationConfig


class PromotionManager:
    """Tracks promotion readiness and release/shadow state."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self._required_passes = config.stability.promotion.required_passes
        self._state = "monitoring"
        self._pass_streak = 0
        self._candidate_ready = False
        self._candidate_ready_tick: int | None = None
        self._last_result: str | None = None
        self._last_evaluated_tick: int | None = None
        self._history: deque[dict[str, object]] = deque(maxlen=50)
        self._current_release: dict[str, object] = {
            "policy_hash": getattr(config, "policy_hash", None),
            "config_id": config.config_id,
        }
        self._candidate_metadata: dict[str, object] | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def update_from_metrics(self, metrics: Mapping[str, object], *, tick: int) -> None:
        """Update state based on the latest stability metrics."""

        promotion_block = metrics.get("promotion")
        if not isinstance(promotion_block, Mapping):
            return
        self._pass_streak = int(promotion_block.get("pass_streak", 0))
        last_result = promotion_block.get("last_result")
        self._last_result = str(last_result) if last_result is not None else None
        last_tick = promotion_block.get("last_evaluated_tick")
        self._last_evaluated_tick = int(last_tick) if last_tick is not None else None

        candidate_ready = bool(promotion_block.get("candidate_ready", False))
        if candidate_ready:
            if self._state not in {"ready", "promoted"}:
                self._state = "ready"
                self._candidate_ready_tick = tick
        else:
            if self._state == "ready":
                self._state = "monitoring"
                self._candidate_ready_tick = None
        self._candidate_ready = candidate_ready

    def mark_promoted(
        self,
        *,
        tick: int,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        """Record a promotion event and update release metadata."""

        record = {
            "event": "promoted",
            "tick": tick,
            "metadata": dict(metadata) if metadata is not None else {},
        }
        self._history.append(record)
        if metadata is not None:
            self._current_release = dict(metadata)
        self._state = "promoted"
        self._candidate_ready = False
        self._candidate_ready_tick = None
        self._pass_streak = 0

    def register_rollback(
        self,
        *,
        tick: int,
        metadata: Mapping[str, object] | None = None,
    ) -> None:
        """Record a rollback event and return to monitoring state."""

        record = {
            "event": "rollback",
            "tick": tick,
            "metadata": dict(metadata) if metadata is not None else {},
        }
        self._history.append(record)
        if metadata is not None:
            self._current_release.update(dict(metadata))
        self._state = "monitoring"
        self._candidate_ready = False
        self._candidate_ready_tick = None
        self._pass_streak = 0

    def set_candidate_metadata(self, metadata: Mapping[str, object] | None) -> None:
        self._candidate_metadata = dict(metadata) if metadata is not None else None

    def snapshot(self) -> dict[str, object]:
        return {
            "state": self._state,
            "pass_streak": self._pass_streak,
            "required_passes": self._required_passes,
            "candidate_ready": self._candidate_ready,
            "candidate_ready_tick": self._candidate_ready_tick,
            "last_result": self._last_result,
            "last_evaluated_tick": self._last_evaluated_tick,
            "current_release": dict(self._current_release),
            "candidate": dict(self._candidate_metadata)
            if self._candidate_metadata is not None
            else None,
            "history": [dict(entry) for entry in self._history],
        }

    def export_state(self) -> dict[str, object]:
        return self.snapshot()

    def import_state(self, payload: Mapping[str, object]) -> None:
        self._state = str(payload.get("state", "monitoring"))
        self._pass_streak = int(payload.get("pass_streak", 0))
        self._required_passes = int(payload.get("required_passes", self._required_passes))
        self._candidate_ready = bool(payload.get("candidate_ready", False))
        ready_tick = payload.get("candidate_ready_tick")
        self._candidate_ready_tick = int(ready_tick) if ready_tick is not None else None
        last_result = payload.get("last_result")
        self._last_result = str(last_result) if last_result is not None else None
        last_tick = payload.get("last_evaluated_tick")
        self._last_evaluated_tick = int(last_tick) if last_tick is not None else None
        current_release = payload.get("current_release")
        if isinstance(current_release, Mapping):
            self._current_release = dict(current_release)
        candidate = payload.get("candidate")
        self._candidate_metadata = dict(candidate) if isinstance(candidate, Mapping) else None
        history = payload.get("history", [])
        self._history.clear()
        if isinstance(history, list):
            for entry in history:
                if isinstance(entry, Mapping):
                    self._history.append(dict(entry))

    def reset(self) -> None:
        self._state = "monitoring"
        self._pass_streak = 0
        self._candidate_ready = False
        self._candidate_ready_tick = None
        self._last_result = None
        self._last_evaluated_tick = None
        self._history.clear()
        self._candidate_metadata = None

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------
    @property
    def state(self) -> str:
        return self._state

    @property
    def candidate_ready(self) -> bool:
        return self._candidate_ready

    @property
    def pass_streak(self) -> int:
        return self._pass_streak
