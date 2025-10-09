"""Action schema and application pipeline (skeleton)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .events import Event
from .state import WorldState


@dataclass
class Action:
    """Placeholder action representation."""

    agent_id: str
    payload: Mapping[str, Any]


def validate_actions(actions: Iterable[Action]) -> None:
    """Validate incoming actions (to be implemented in WP2)."""

    raise NotImplementedError("validate_actions pending WP2 implementation")


def apply_actions(state: WorldState, actions: Iterable[Action]) -> list[Event]:
    """Apply actions to the world state and return emitted events."""

    raise NotImplementedError("apply_actions pending WP2 implementation")


__all__ = ["Action", "validate_actions", "apply_actions"]
