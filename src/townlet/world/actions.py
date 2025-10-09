"""Action schema and application pipeline used by the modular world."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

from townlet.world.events import Event
from townlet.world.state import WorldState

ActionKind = str
IMPLEMENTED_KINDS: frozenset[str] = frozenset({"move", "noop"})
SUPPORTED_KINDS: frozenset[str] = frozenset(
    {"move", "request", "start", "release", "chat", "blocked", "noop"}
)


class ActionValidationError(ValueError):
    """Raised when an incoming action fails schema validation."""


@dataclass(slots=True)
class Action:
    """Normalised action structure consumed by the world."""

    agent_id: str
    kind: ActionKind
    payload: Mapping[str, Any]

    def duration(self) -> int:
        return int(self.payload.get("duration", 1))


def validate_actions(actions: Iterable[Action]) -> list[Action]:
    """Validate and normalise actions, returning the resulting list."""

    normalised: list[Action] = []
    for action in actions:
        normalised.append(_normalise_action(action))
    return normalised


def apply_actions(state: WorldState, actions: Iterable[Action]) -> list[Event]:
    """Apply validated actions to the world state and emit structured events."""

    emitted: list[Event] = []
    agent_view = state.agent_snapshots_view()
    records_view = state.agent_records_view()
    for raw_action in actions:
        try:
            action = _normalise_action(raw_action)
        except ActionValidationError as exc:
            emitted.append(
                state.emit_event(
                    "action.invalid",
                    {
                        "agent_id": getattr(raw_action, "agent_id", None),
                        "error": str(exc),
                    },
                )
            )
            continue

        snapshot = agent_view.get(action.agent_id)
        if snapshot is None:
            emitted.append(
                state.emit_event(
                    "action.unknown_agent",
                    {"agent_id": action.agent_id, "kind": action.kind},
                )
            )
            continue

        payload: MutableMapping[str, Any] = dict(action.payload)
        duration = int(payload.get("duration", 1))
        success = False
        pending = action.kind not in IMPLEMENTED_KINDS

        if action.kind == "move":
            position = payload["position"]
            snapshot.position = position
            success = True
        elif action.kind == "noop":
            success = True

        snapshot.last_action_id = action.kind
        snapshot.last_action_success = success
        snapshot.last_action_duration = duration

        record = records_view.get(action.agent_id)
        if record is not None:
            record.touch(tick=state.tick, metadata={"last_action": action.kind})

        payload.update(
            {
                "agent_id": action.agent_id,
                "success": success,
                "duration": duration,
                "pending": pending,
            }
        )
        emitted.append(state.emit_event(f"action.{action.kind}", payload))

    return emitted


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _normalise_action(raw: Action) -> Action:
    if not isinstance(raw.agent_id, str) or not raw.agent_id.strip():
        raise ActionValidationError("agent_id must be a non-empty string")
    if not isinstance(raw.kind, str):
        raise ActionValidationError("kind must be a string")
    kind = raw.kind.strip().lower()
    if kind not in SUPPORTED_KINDS:
        raise ActionValidationError(f"unsupported action kind '{raw.kind}'")

    payload = dict(raw.payload or {})
    payload["duration"] = _normalise_duration(payload.get("duration"))

    if kind == "move":
        payload["position"] = _normalise_position(payload.get("position"))
    elif kind in {"request", "start", "release", "blocked"}:
        payload["object"] = _require_string(payload.get("object"), "object")
    elif kind == "chat":
        target = payload.get("target") or payload.get("listener")
        payload["target"] = _require_string(target, "target")

    if kind == "release":
        payload["success"] = bool(payload.get("success", True))
    if kind == "chat":
        payload["quality"] = _normalise_float(payload.get("quality", 0.5), "quality")

    return Action(agent_id=raw.agent_id.strip(), kind=kind, payload=payload)


def _normalise_duration(value: Any) -> int:
    try:
        duration = int(value) if value is not None else 1
    except (TypeError, ValueError) as exc:
        raise ActionValidationError("duration must be an integer") from exc
    if duration < 1:
        raise ActionValidationError("duration must be >= 1")
    return duration


def _normalise_position(value: Any) -> tuple[int, int]:
    if not isinstance(value, Sequence):
        raise ActionValidationError("position must be a sequence of two numbers")
    if len(value) != 2:
        raise ActionValidationError("position must contain exactly two coordinates")
    try:
        x = int(value[0])
        y = int(value[1])
    except (TypeError, ValueError) as exc:
        raise ActionValidationError("position values must be integers") from exc
    return (x, y)


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ActionValidationError(f"{field} must be a non-empty string")
    return value.strip()


def _normalise_float(value: Any, field: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ActionValidationError(f"{field} must be coercible to float") from exc


__all__ = [
    "Action",
    "ActionKind",
    "ActionValidationError",
    "apply_actions",
    "validate_actions",
]
