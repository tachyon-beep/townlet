"""Economy system helpers."""

from __future__ import annotations

from townlet.world.economy import EconomyService

from .base import SystemContext 


def step(ctx: SystemContext) -> None:
    """Update economy metrics and utilities (implementation pending)."""

    return


def update_basket_metrics(service: EconomyService) -> None:
    service.update_basket_metrics()


def restock(service: EconomyService) -> None:
    service.restock_economy()


def utility_online(service: EconomyService, utility: str) -> bool:
    return service.utility_online(utility)


def economy_settings(service: EconomyService) -> dict[str, float]:
    return service.economy_settings()


def active_price_spikes(service: EconomyService) -> dict[str, dict[str, object]]:
    return service.active_price_spikes()


def utility_snapshot(service: EconomyService) -> dict[str, bool]:
    return service.utility_snapshot()


__all__ = [
    "active_price_spikes",
    "economy_settings",
    "restock",
    "step",
    "update_basket_metrics",
    "utility_online",
    "utility_snapshot",
]
