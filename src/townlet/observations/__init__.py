"""Observation builders and utilities."""

from __future__ import annotations

from townlet.config import SimulationConfig

from .builder import ObservationBuilder

__all__ = ["ObservationBuilder", "create_observation_builder"]


def create_observation_builder(*, config: SimulationConfig) -> ObservationBuilder:
    """Factory returning the standard observation builder implementation."""

    return ObservationBuilder(config=config)
