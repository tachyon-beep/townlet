"""Affordance hook plug-in namespace."""

from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - avoid circular import
    from townlet.world.grid import WorldState


def load_modules(world: "WorldState", module_paths: Iterable[str]) -> None:
    """Import hook modules and let them register against the given world."""

    from importlib import import_module

    for path in module_paths:
        module = import_module(path)
        register = getattr(module, "register_hooks", None)
        if callable(register):
            register(world)
