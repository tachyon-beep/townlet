"""Factories for creating modular world runtime adapters."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.adapters.world_default import DefaultWorldAdapter
from townlet.observations.builder import ObservationBuilder
from townlet.ports.world import WorldRuntime
from townlet.world.runtime import WorldRuntime as LegacyWorldRuntime
from townlet.world.grid import WorldState

from .registry import register, resolve


def create_world(provider: str = "default", **kwargs: Any) -> WorldRuntime:
    return resolve("world", provider, **kwargs)


@register("world", "default")
@register("world", "facade")
def _build_default_world(
    *,
    runtime: LegacyWorldRuntime | None = None,
    config: Any | None = None,
    lifecycle: Any | None = None,
    perturbations: Any | None = None,
    ticks_per_day: int | None = None,
    world_kwargs: Mapping[str, Any] | None = None,
    observation_builder: ObservationBuilder | None = None,
    **legacy_kwargs: Any,
) -> WorldRuntime:
    if runtime is None:
        missing = [
            name
            for name, value in (
                ("config", config),
                ("lifecycle", lifecycle),
                ("perturbations", perturbations),
            )
            if value is None
        ]
        if missing:
            raise TypeError(
                "create_world requires runtime or ({})".format(", ".join(missing))
            )
        world_options = dict(world_kwargs or {})
        world = WorldState.from_config(config, **world_options)  # type: ignore[arg-type]
        runtime = LegacyWorldRuntime(
            world=world,
            lifecycle=lifecycle,
            perturbations=perturbations,
            ticks_per_day=ticks_per_day or 0,
            **legacy_kwargs,
        )
    elif legacy_kwargs:
        raise TypeError(
            "Unexpected arguments for pre-built runtime: {}".format(", ".join(legacy_kwargs))
        )

    builder = observation_builder or ObservationBuilder(runtime.world.config)
    return DefaultWorldAdapter(runtime=runtime, observation_builder=builder)


__all__ = ["create_world"]
