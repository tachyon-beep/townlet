"""Context helpers for observation feature assembly (WP-C Phase 4)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.world.core.runtime_adapter import ensure_world_adapter
from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


def agent_context(
    world: WorldRuntimeAdapterProtocol | object,
    agent_id: str,
) -> dict[str, Any]:
    """Return scalar context fields consumed by observation builders."""

    try:
        adapter = ensure_world_adapter(world)
    except TypeError:
        adapter = None

    snapshot = _resolve_agent_snapshot(adapter, world, agent_id)
    if snapshot is None:
        return {}
    return {
        "needs": dict(getattr(snapshot, "needs", {})),
        "wallet": float(getattr(snapshot, "wallet", 0.0)),
        "lateness_counter": getattr(snapshot, "lateness_counter", 0),
        "on_shift": bool(getattr(snapshot, "on_shift", False)),
        "attendance_ratio": float(getattr(snapshot, "attendance_ratio", 0.0)),
        "wages_withheld": float(getattr(snapshot, "wages_withheld", 0.0)),
        "shift_state": getattr(snapshot, "shift_state", "pre_shift"),
        "last_action_id": getattr(snapshot, "last_action_id", ""),
        "last_action_success": bool(getattr(snapshot, "last_action_success", False)),
        "last_action_duration": getattr(snapshot, "last_action_duration", 0),
        "wages_paid": _maybe_call(
            adapter or world,
            "_employment_context_wages",
            getattr(snapshot, "agent_id", agent_id),
            default=float(getattr(snapshot, "wages_paid", 0.0)),
        ),
        "punctuality_bonus": _maybe_call(
            adapter or world,
            "_employment_context_punctuality",
            getattr(snapshot, "agent_id", agent_id),
            default=float(getattr(snapshot, "punctuality_bonus", 0.0)),
        ),
    }


def snapshot_precondition_context(context: Mapping[str, Any]) -> dict[str, Any]:
    """Deep-copy precondition context into a JSON-serialisable structure."""

    def _clone(value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): _clone(val) for key, val in value.items()}
        if isinstance(value, list):
            return [_clone(item) for item in value]
        if isinstance(value, tuple):
            return [_clone(item) for item in value]
        return value

    return {str(key): _clone(val) for key, val in context.items()}


def _maybe_call(world: object, attr: str, *args: object, default: float = 0.0) -> float:
    func = getattr(world, attr, None)
    if callable(func):
        try:
            return float(func(*args))
        except Exception:  # pragma: no cover - defensive fallback
            return default
    return default


def _resolve_agent_snapshot(
    adapter: WorldRuntimeAdapterProtocol | None,
    world: object,
    agent_id: str,
) -> Any:
    if adapter is not None:
        view = adapter.agent_snapshots_view()
        return view.get(agent_id)

    fallback = getattr(world, "agent_snapshots_view", lambda: {})
    try:
        view = fallback() if callable(fallback) else fallback
    except Exception:  # pragma: no cover - legacy surface defensive guard
        return None

    if isinstance(view, Mapping):
        return view.get(agent_id)
    if hasattr(view, "get"):
        return view.get(agent_id)
    return None


__all__ = ["agent_context", "snapshot_precondition_context"]
