"""Factories for creating world runtime adapters."""

from __future__ import annotations

from typing import Any

from townlet.adapters.world_default import DefaultWorldAdapter
from townlet.observations.builder import ObservationBuilder
from townlet.ports.world import WorldRuntime
from townlet.world.runtime import WorldRuntime as LegacyWorldRuntime

from .registry import register, resolve


def create_world(provider: str = "default", **kwargs: Any) -> WorldRuntime:
    return resolve("world", provider, **kwargs)


@register("world", "default")
@register("world", "facade")
def _build_default_world(
    *,
    runtime: LegacyWorldRuntime,
    observation_builder: ObservationBuilder | None = None,
) -> WorldRuntime:
    builder = observation_builder or ObservationBuilder(runtime.world.config)
    return DefaultWorldAdapter(runtime=runtime, observation_builder=builder)


__all__ = ["create_world"]
