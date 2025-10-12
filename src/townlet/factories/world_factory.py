"""Factories for creating modular world runtime adapters."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Any

from townlet.adapters.world_default import DefaultWorldAdapter
from townlet.lifecycle.manager import LifecycleManager
from townlet.ports.world import WorldRuntime
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.testing import DummyWorldRuntime
from townlet.world.core.context import WorldContext
from townlet.world.grid import WorldState, build_console_service
from townlet.world.rng import RngStreamManager

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
    world: WorldState | None = None,
    config: Any | None = None,
    ticks_per_day: int | None = None,
    world_kwargs: Mapping[str, Any] | None = None,
    affordance_runtime_factory: Callable[
        [WorldState, Any],
        Any,
    ]
    | None = None,
    affordance_runtime_config: Any | None = None,
    **unexpected_kwargs: Any,
) -> WorldRuntime:
    if unexpected_kwargs:
        raise TypeError(
            "Unsupported arguments for modular world builder: {}".format(", ".join(unexpected_kwargs))
        )

    target_world: WorldState | None = world
    if target_world is None:
        if config is None:
            raise TypeError("create_world requires 'config' when 'world' is not supplied")
        world_options = dict(world_kwargs or {})
        if affordance_runtime_factory is not None:
            world_options["affordance_runtime_factory"] = affordance_runtime_factory
        if affordance_runtime_config is not None:
            world_options["affordance_runtime_config"] = affordance_runtime_config
        target_world = WorldState.from_config(
            config,
            attach_console=False,
            **world_options,
        )  # type: ignore[arg-type]
    else:
        if config is None:
            config = getattr(target_world, "config", None)

    if config is None:
        raise TypeError("WorldState missing configuration; cannot build modular world runtime")

    context: WorldContext | None = getattr(target_world, "context", None)
    if context is None:
        console_service = build_console_service(target_world)
        target_world.attach_console_service(console_service)
        context = target_world.context
    else:
        console_service = getattr(context, "console", None)
        if console_service is None:
            console_service = build_console_service(target_world)
            target_world.attach_console_service(console_service)
            context = target_world.context
    if context is None:
        raise TypeError("WorldState missing context; cannot build modular world runtime")

    rng_manager = context.rng_manager
    if rng_manager is None:
        rng_manager = RngStreamManager.from_seed(getattr(target_world, "rng_seed", None))
        context.rng_manager = rng_manager
    perturbation_rng = rng_manager.stream("perturbations")

    lifecycle = LifecycleManager(config=config)
    perturbations = PerturbationScheduler(config=config, rng=perturbation_rng)
    ticks = _derive_ticks_per_day(config, ticks_per_day)

    return DefaultWorldAdapter(
        context=context,
        lifecycle=lifecycle,
        perturbations=perturbations,
        ticks_per_day=ticks,
    )


@register("world", "dummy")
def _build_dummy_world(
    *,
    agents: Iterable[str] | None = None,
    config_id: str = "dummy-config",
    **unexpected_kwargs: Any,
) -> WorldRuntime:
    if unexpected_kwargs:
        raise TypeError(
            "Unsupported arguments for dummy world provider: {}".format(
                ", ".join(unexpected_kwargs)
            )
        )
    return DummyWorldRuntime(agents_list=tuple(agents or ()), config_id=config_id)


__all__ = ["create_world"]
