"""Affordance hook plug-in namespace."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - avoid circular import
    from townlet.world.grid import WorldState


logger = logging.getLogger(__name__)


def load_modules(
    world: WorldState, module_paths: Iterable[str]
) -> tuple[list[str], list[tuple[str, str]]]:
    """Import hook modules and let them register against the given world.

    Returns a tuple of (accepted_modules, rejected_modules_with_reason).
    """

    from importlib import import_module

    loaded: list[str] = []
    rejected: list[tuple[str, str]] = []

    for path in module_paths:
        if not path:
            continue
        try:
            module = import_module(path)
        except Exception as exc:  # pragma: no cover - defensive
            reason = f"import_error: {exc}"
            rejected.append((path, reason))
            logger.warning("affordance_hook_import_failed module=%s error=%s", path, exc)
            continue

        register = getattr(module, "register_hooks", None)
        if not callable(register):
            reason = "missing_register_hooks"
            rejected.append((path, reason))
            logger.warning(
                "affordance_hook_missing_register module=%s", path
            )
            continue

        try:
            register(world)
        except Exception as exc:  # pragma: no cover - defensive
            reason = f"register_failed: {exc}"
            rejected.append((path, reason))
            logger.warning(
                "affordance_hook_register_failed module=%s error=%s", path, exc
            )
            continue

        loaded.append(path)
        logger.info("affordance_hook_loaded module=%s", path)

    return loaded, rejected
