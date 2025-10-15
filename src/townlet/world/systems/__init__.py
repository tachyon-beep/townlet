"""World systems registry and sequencing helpers."""

from __future__ import annotations

from . import affordances, economy, employment, perturbations, queues, relationships
from .base import SystemContext, SystemStep


def default_systems() -> tuple[SystemStep, ...]:
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
