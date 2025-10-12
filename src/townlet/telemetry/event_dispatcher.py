"""Event dispatcher and cache for telemetry sink."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping
from typing import Any


class TelemetryEventDispatcher:
    """Normalises telemetry events, maintains bounded caches, and notifies subscribers."""

    def __init__(
        self,
        *,
        queue_history_limit: int = 120,
        rivalry_history_limit: int = 120,
    ) -> None:
        if queue_history_limit <= 0:
            raise ValueError("queue_history_limit must be positive")
        if rivalry_history_limit <= 0:
            raise ValueError("rivalry_history_limit must be positive")
        self._queue_history_limit = queue_history_limit
        self._rivalry_history_limit = rivalry_history_limit
        self._queue_history: list[dict[str, Any]] = []
        self._rivalry_history: list[dict[str, Any]] = []
        self._possessed_agents: list[str] = []
        self._latest_tick: dict[str, Any] | None = None
        self._latest_health: dict[str, Any] | None = None
        self._latest_failure: dict[str, Any] | None = None
        self._subscribers: list[Callable[[str, Mapping[str, Any]], None]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        """Normalise ``payload``, update caches, and notify subscribers."""

        event_payload = self._coerce_payload(payload)
        self._update_caches(name, event_payload)
        for subscriber in list(self._subscribers):
            try:
                subscriber(name, event_payload)
            except Exception:  # pragma: no cover - defensive
                # Subscribers are best-effort; failure should not break dispatch.
                continue
        return event_payload

    def register_subscriber(self, callback: Callable[[str, Mapping[str, Any]], None]) -> None:
        """Register a callback invoked for every event."""

        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unregister_subscriber(self, callback: Callable[[str, Mapping[str, Any]], None]) -> None:
        """Remove a previously registered callback."""

        try:
            self._subscribers.remove(callback)
        except ValueError:  # pragma: no cover - defensive
            pass

    # ------------------------------------------------------------------
    # Cache accessors
    # ------------------------------------------------------------------
    @property
    def queue_history(self) -> list[dict[str, Any]]:
        return [dict(entry) for entry in self._queue_history]

    @property
    def rivalry_history(self) -> list[dict[str, Any]]:
        return [dict(entry) for entry in self._rivalry_history]

    @property
    def possessed_agents(self) -> list[str]:
        return list(self._possessed_agents)

    @property
    def latest_tick(self) -> dict[str, Any] | None:
        return None if self._latest_tick is None else dict(self._latest_tick)

    @property
    def latest_health(self) -> dict[str, Any] | None:
        return None if self._latest_health is None else dict(self._latest_health)

    @property
    def latest_failure(self) -> dict[str, Any] | None:
        return None if self._latest_failure is None else dict(self._latest_failure)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _coerce_payload(self, payload: Mapping[str, Any] | None) -> dict[str, Any]:
        if payload is None:
            return {}
        if isinstance(payload, MutableMapping):
            return dict(payload)
        if isinstance(payload, Mapping):
            return {str(key): value for key, value in payload.items()}
        raise TypeError("event payload must be a mapping or None")

    def _update_caches(self, name: str, payload: Mapping[str, Any]) -> None:
        if name == "loop.tick":
            self._latest_tick = dict(payload)
        elif name == "loop.health":
            self._latest_health = dict(payload)
            self._append_queue_history(payload)
        elif name == "loop.failure":
            self._latest_failure = dict(payload)
        elif name == "policy.possession":
            agents = payload.get("agents", payload.get("possessed_agents", []))
            if isinstance(agents, list):
                self._possessed_agents = sorted({str(agent) for agent in agents})
        elif name == "rivalry.events":
            events = payload.get("events", [])
            self._append_rivalry_history(events, payload.get("tick"))

        # Also inspect loop tick events for embedded rivalry data.
        if name == "loop.tick":
            embedded_events = payload.get("events", [])
            self._append_rivalry_history(embedded_events, payload.get("tick"))

    def _append_queue_history(self, payload: Mapping[str, Any]) -> None:
        queue_metrics = payload.get("queue_metrics")
        if not isinstance(queue_metrics, Mapping):
            global_context = payload.get("global_context")
            if isinstance(global_context, Mapping):
                queue_metrics = global_context.get("queue_metrics")
        if not isinstance(queue_metrics, Mapping):
            return
        entry = {
            "tick": int(payload.get("tick", -1)),
            "metrics": {str(key): int(value) for key, value in queue_metrics.items()},
        }
        self._queue_history.append(entry)
        if len(self._queue_history) > self._queue_history_limit:
            overflow = len(self._queue_history) - self._queue_history_limit
            if overflow > 0:
                self._queue_history = self._queue_history[overflow:]

    def _append_rivalry_history(self, events: Any, tick: Any) -> None:
        if not events:
            return
        event_tick = int(tick) if tick is not None else None
        for raw in events:
            if not isinstance(raw, Mapping):
                continue
            payload = {
                "tick": int(raw.get("tick", event_tick or -1)),
                "agent_a": str(raw.get("agent_a", "")),
                "agent_b": str(raw.get("agent_b", "")),
                "intensity": float(raw.get("intensity", 0.0)),
                "reason": str(raw.get("reason", "")),
            }
            self._rivalry_history.append(payload)
        if len(self._rivalry_history) > self._rivalry_history_limit:
            keep = self._rivalry_history_limit
            self._rivalry_history = self._rivalry_history[-keep:]


__all__ = ["TelemetryEventDispatcher"]
