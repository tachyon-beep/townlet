"""Factories for creating modular world runtime adapters."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.adapters.world_default import DefaultWorldAdapter
from townlet.lifecycle.manager import LifecycleManager
from townlet.observations.builder import ObservationBuilder
from townlet.ports.world import WorldRuntime
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.world.core.context import WorldContext
from townlet.world.grid import WorldState
from townlet.world.runtime import WorldRuntime as LegacyWorldRuntime

from .registry import register, resolve


def create_world(provider: str = "default", **kwargs: Any) -> WorldRuntime:
    return resolve("world", provider, **kwargs)


def _derive_ticks_per_day(config: Any, explicit: int | None) -> int:
    if explicit is not None:
        return max(0, int(explicit))
    cfg = getattr(config, "observations_config", None)
    if cfg is not None and getattr(cfg, "hybrid", None) is not None:
        value = getattr(cfg.hybrid, "time_ticks_per_day", None)
        if value is not None:
            return max(1, int(value))
    return 1440


@register("world", "default")
@register("world", "facade")
def _build_default_world(
    *,
    runtime: LegacyWorldRuntime | None = None,
    world: WorldState | None = None,
    config: Any | None = None,
    lifecycle: LifecycleManager | None = None,
    perturbations: PerturbationScheduler | None = None,
    ticks_per_day: int | None = None,
    world_kwargs: Mapping[str, Any] | None = None,
    observation_builder: ObservationBuilder | None = None,
    **legacy_kwargs: Any,
) -> WorldRuntime:
    # Legacy pathway for callers providing a pre-built runtime.
    if runtime is not None:
        if legacy_kwargs:
            raise TypeError(
                "Unexpected arguments for pre-built runtime: {}".format(", ".join(legacy_kwargs))
            )
        builder = observation_builder or ObservationBuilder(runtime.world.config)
        return DefaultWorldAdapter(runtime=runtime, observation_builder=builder)

    if legacy_kwargs:
        raise TypeError(
            "Unsupported arguments for modular world builder: {}".format(", ".join(legacy_kwargs))
        )

    target_world: WorldState | None = world
    if target_world is None:
        if config is None:
            raise TypeError("create_world requires 'config' when 'world' is not supplied")
        world_options = dict(world_kwargs or {})
        target_world = WorldState.from_config(config, **world_options)  # type: ignore[arg-type]

    context: WorldContext | None = getattr(target_world, "context", None)
    if context is None:
        raise TypeError("WorldState missing context; cannot build modular world runtime")

    missing = [
        name
        for name, value in (
            ("lifecycle", lifecycle),
            ("perturbations", perturbations),
        )
        if value is None
    ]
    if missing:
        raise TypeError("create_world requires lifecycle/perturbations when building modular world")

    builder = observation_builder or ObservationBuilder(target_world.config)
    ticks = _derive_ticks_per_day(target_world.config, ticks_per_day)

    return DefaultWorldAdapter(
        context=context,
        lifecycle=lifecycle,
        perturbations=perturbations,
        ticks_per_day=ticks,
        observation_builder=builder,
    )


__all__ = ["create_world"]
