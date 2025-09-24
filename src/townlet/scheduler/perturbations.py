"""Perturbation scheduler scaffolding."""
from __future__ import annotations

from typing import Iterable

from townlet.config import SimulationConfig
from townlet.world.grid import WorldState


class PerturbationScheduler:
    """Injects bounded random events into the world."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.pending: list[object] = []

    def tick(self, world: WorldState, current_tick: int) -> None:
        # TODO(@townlet): Emit price spikes, outages, and arranged meets.
        _ = world, current_tick

    def enqueue(self, events: Iterable[object]) -> None:
        self.pending.extend(events)
