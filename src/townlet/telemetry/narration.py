"""Narration throttling utilities."""

from __future__ import annotations

from collections import deque

from townlet.config import NarrationThrottleConfig


class NarrationRateLimiter:
    """Apply global and per-category narration cooldowns with dedupe."""

    def __init__(self, config: NarrationThrottleConfig) -> None:
        self.config = config
        self._current_tick: int = 0
        self._last_category_tick: dict[str, int] = {}
        self._last_global_tick: int = -10_000
        self._recent_entries: dict[str, int] = {}
        self._window_emissions: deque[int] = deque()

    def begin_tick(self, tick: int) -> None:
        self._current_tick = int(tick)
        self._expire_recent_entries()
        self._expire_window()

    def allow(
        self,
        category: str,
        *,
        message: str,
        priority: bool = False,
        dedupe_key: str | None = None,
    ) -> bool:
        """Return True if a narration may be emitted for the given category."""

        key = dedupe_key or message
        dedupe_window = int(self.config.dedupe_window_ticks)
        if dedupe_window >= 0:
            last_tick = self._recent_entries.get(key)
            if (
                last_tick is not None
                and self._current_tick - last_tick <= dedupe_window
            ):
                return False

        if not priority:
            if not self._check_global_cooldown():
                return False
            if not self._check_category_cooldown(category):
                return False
            if not self._check_window_limit():
                return False
        else:
            # Priority events still respect the global window limit to keep volume bounded.
            if not self._check_window_limit():
                return False

        self._record_emission(category, key)
        return True

    def export_state(self) -> dict[str, object]:
        return {
            "last_category_tick": dict(self._last_category_tick),
            "last_global_tick": int(self._last_global_tick),
            "recent_entries": dict(self._recent_entries),
            "window_emissions": list(self._window_emissions),
        }

    def import_state(self, payload: dict[str, object]) -> None:
        last_category = payload.get("last_category_tick", {})
        if isinstance(last_category, dict):
            self._last_category_tick = {
                str(cat): int(tick) for cat, tick in last_category.items()
            }
        last_global = payload.get("last_global_tick")
        if isinstance(last_global, (int, float)):
            self._last_global_tick = int(last_global)
        recent = payload.get("recent_entries", {})
        if isinstance(recent, dict):
            self._recent_entries = {str(key): int(tick) for key, tick in recent.items()}
        window = payload.get("window_emissions", [])
        if isinstance(window, list):
            self._window_emissions = deque(int(tick) for tick in window)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _expire_recent_entries(self) -> None:
        if not self._recent_entries:
            return
        window = int(self.config.dedupe_window_ticks)
        if window < 0:
            self._recent_entries.clear()
            return
        cutoff = self._current_tick - window
        for key, tick in list(self._recent_entries.items()):
            if tick <= cutoff:
                self._recent_entries.pop(key, None)

    def _expire_window(self) -> None:
        if not self._window_emissions:
            return
        window_ticks = int(self.config.global_window_ticks)
        cutoff = self._current_tick - window_ticks
        while self._window_emissions and self._window_emissions[0] <= cutoff:
            self._window_emissions.popleft()

    def _check_global_cooldown(self) -> bool:
        cooldown = int(self.config.global_cooldown_ticks)
        if cooldown <= 0:
            return True
        return self._current_tick - self._last_global_tick >= cooldown

    def _check_category_cooldown(self, category: str) -> bool:
        cooldown = int(self.config.get_category_cooldown(category))
        if cooldown <= 0:
            return True
        last_tick = self._last_category_tick.get(category, -cooldown)
        return self._current_tick - last_tick >= cooldown

    def _check_window_limit(self) -> bool:
        limit = int(self.config.global_window_limit)
        if limit <= 0:
            return True
        return len(self._window_emissions) < limit

    def _record_emission(self, category: str, dedupe_key: str) -> None:
        self._last_category_tick[category] = self._current_tick
        self._last_global_tick = self._current_tick
        self._recent_entries[dedupe_key] = self._current_tick
        limit = int(self.config.global_window_limit)
        if limit > 0:
            self._window_emissions.append(self._current_tick)
