"""World systems registry and sequencing helpers."""

from __future__ import annotations

from typing import Iterable, Tuple

from .base import SystemContext, SystemStep

from . import queues, affordances, employment, relationships, economy, perturbations


def default_systems() -> Tuple[SystemStep, ...]:
    """Return the ordered list of system steps (placeholders for now)."""

    return (
        queues.step,
        affordances.step,
        employment.step,
        relationships.step,
        economy.step,
        perturbations.step,
    )


__all__ = ["SystemContext", "SystemStep", "default_systems"]
