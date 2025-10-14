"""Shared types and helpers for world systems."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from townlet.world.events import EventDispatcher
from townlet.world.rng import RngStreamManager
@dataclass(slots=True)
class SystemContext:
    """Context passed to each system step during tick orchestration."""

    state: Any
    rng: RngStreamManager
    events: EventDispatcher


class System(Protocol):
    """Protocol implemented by system modules."""

    def step(self, ctx: SystemContext) -> None:  # pragma: no cover - structural protocol
        ...


SystemStep = Callable[[SystemContext], None]

__all__ = ["System", "SystemContext", "SystemStep"]
