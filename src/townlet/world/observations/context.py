"""Context helpers for observation feature assembly (WP-C Phase 4)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.world.core.runtime_adapter import ensure_world_adapter
from townlet.world.observations.interfaces import AdapterSource


def _as_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _as_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def agent_context(
    world: AdapterSource,
    agent_id: str,
) -> dict[str, Any]:
    """Return scalar context fields consumed by observation builders."""

    adapter = ensure_world_adapter(world)
    snapshots = adapter.agent_snapshots_view()
    snapshot = snapshots.get(agent_id)
    if snapshot is None:
        return {}
    wages_fn = getattr(adapter, "_employment_context_wages", None)
    if wages_fn is None:
        raise RuntimeError(
            "World runtime adapter is missing employment context wages hook"
        )
    punctuality_fn = getattr(adapter, "_employment_context_punctuality", None)
    if punctuality_fn is None:
        raise RuntimeError(
            "World runtime adapter is missing employment punctuality hook"
        )
    wages_paid = _as_float(wages_fn(agent_id))
    punctuality_bonus = _as_float(punctuality_fn(agent_id))
    return {
        "needs": dict(getattr(snapshot, "needs", {})),
        "wallet": _as_float(getattr(snapshot, "wallet", 0.0)),
        "lateness_counter": _as_int(getattr(snapshot, "lateness_counter", 0)),
        "on_shift": bool(getattr(snapshot, "on_shift", False)),
        "attendance_ratio": _as_float(getattr(snapshot, "attendance_ratio", 0.0)),
        "wages_withheld": _as_float(getattr(snapshot, "wages_withheld", 0.0)),
        "shift_state": getattr(snapshot, "shift_state", "pre_shift"),
        "last_action_id": getattr(snapshot, "last_action_id", ""),
        "last_action_success": bool(getattr(snapshot, "last_action_success", False)),
        "last_action_duration": _as_int(getattr(snapshot, "last_action_duration", 0)),
        "wages_paid": wages_paid,
        "punctuality_bonus": punctuality_bonus,
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


__all__ = ["agent_context", "snapshot_precondition_context"]
