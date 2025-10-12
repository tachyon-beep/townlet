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

    adapter = ensure_world_adapter(world)
    snapshots = adapter.agent_snapshots_view()
    snapshot = snapshots.get(agent_id)
    if snapshot is None:
        return {}
    try:
        wages_paid = float(adapter._employment_context_wages(agent_id))
    except AttributeError as error:
        raise RuntimeError(
            "World runtime adapter is missing employment context wages hook"
        ) from error
    except Exception:  # pragma: no cover - defensive fallback for adapter bugs
        wages_paid = 0.0
    try:
        punctuality_bonus = float(adapter._employment_context_punctuality(agent_id))
    except AttributeError as error:
        raise RuntimeError(
            "World runtime adapter is missing employment punctuality hook"
        ) from error
    except Exception:  # pragma: no cover - defensive fallback for adapter bugs
        punctuality_bonus = 0.0
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
