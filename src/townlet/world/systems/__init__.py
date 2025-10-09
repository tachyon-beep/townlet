"""World systems registry (skeleton)."""

from __future__ import annotations

from typing import Callable, Iterable

from ..state import WorldState


SystemStep = Callable[[WorldState], None]


def default_systems() -> Iterable[SystemStep]:
    """Return the ordered list of system steps (placeholder)."""

    return ()


__all__ = ["SystemStep", "default_systems"]
