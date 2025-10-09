"""Perturbation (events & spikes) helpers."""

from __future__ import annotations

from collections.abc import Iterable

from townlet.world.perturbations.service import PerturbationService

from .base import SystemContext


def step(ctx: SystemContext) -> None:
    """Advance perturbation schedules (implementation pending)."""

    return


def apply_price_spike(
    service: PerturbationService,
    event_id: str,
    *,
    magnitude: float,
    targets: Iterable[str] | None = None,
) -> None:
    service.apply_price_spike(event_id, magnitude=magnitude, targets=targets)


def clear_price_spike(service: PerturbationService, event_id: str) -> None:
    service.clear_price_spike(event_id)


def apply_utility_outage(service: PerturbationService, event_id: str, utility: str) -> None:
    service.apply_utility_outage(event_id, utility)


def clear_utility_outage(service: PerturbationService, event_id: str, utility: str) -> None:
    service.clear_utility_outage(event_id, utility)


def apply_arranged_meet(
    service: PerturbationService,
    *,
    location: str | None,
    targets: Iterable[str] | None = None,
) -> None:
    service.apply_arranged_meet(location=location, targets=targets)


__all__ = [
    "apply_arranged_meet",
    "apply_price_spike",
    "apply_utility_outage",
    "clear_price_spike",
    "clear_utility_outage",
    "step",
]
