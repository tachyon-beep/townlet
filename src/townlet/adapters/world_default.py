"""Adapter that bridges the legacy world runtime to the new port."""

from __future__ import annotations

import random
from collections.abc import Iterable, Mapping
from typing import Any

from townlet.factories.registry import register
from townlet.lifecycle.manager import LifecycleManager
from townlet.ports.world import WorldRuntime
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.world.grid import WorldState
from townlet.world.runtime import WorldRuntime as LegacyWorldRuntime


class DefaultWorldAdapter(WorldRuntime):
    """Bridge between :class:`LegacyWorldRuntime` and :class:`WorldRuntime`."""

    def __init__(self, cfg: Any, *, seed: int | None = None) -> None:
        self._cfg = cfg
        self._seed = seed
        self._runtime: LegacyWorldRuntime | None = None
        self._world: WorldState | None = None
        self._tick = 0
        self._last_snapshot: dict[str, Any] = {}
        self.reset(seed)

    # ------------------------------------------------------------------
    # WorldRuntime interface
    # ------------------------------------------------------------------
    def reset(self, seed: int | None = None) -> None:
        """Recreate the world runtime from configuration."""

        if seed is not None:
            self._seed = seed
        rng_seed = self._seed if self._seed is not None else getattr(self._cfg, "seed", None)
        rng = random.Random(rng_seed) if rng_seed is not None else random.Random()
        world = WorldState.from_config(
            self._cfg,
            rng=rng,
        )
        lifecycle = LifecycleManager(config=self._cfg)
        perturbations = PerturbationScheduler(config=self._cfg, rng=random.Random(rng_seed) if rng_seed is not None else None)
        ticks_per_day = _resolve_ticks_per_day(self._cfg)
        self._runtime = LegacyWorldRuntime(
            world=world,
            lifecycle=lifecycle,
            perturbations=perturbations,
            ticks_per_day=ticks_per_day,
        )
        self._world = world
        self._tick = 0
        self._last_snapshot = {}

    def tick(self) -> None:
        """Advance the world by one tick."""

        if self._runtime is None:
            raise RuntimeError("World runtime not initialised")
        self._tick += 1
        self._runtime.tick(tick=self._tick)
        self._last_snapshot = self.snapshot()

    def agents(self) -> Iterable[str]:
        world = self._require_world()
        return list(world.agents.keys())

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        world = self._require_world()
        snapshot = world.snapshot()
        if agent_ids is None:
            agent_ids = snapshot.keys()
        observations: dict[str, Any] = {}
        for agent_id in agent_ids:
            if agent_id in snapshot:
                observations[agent_id] = snapshot[agent_id]
        observations["__meta__"] = {"tick": self._tick}
        return observations

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        if self._runtime is None:
            raise RuntimeError("World runtime not initialised")
        self._runtime.apply_actions(actions)

    def snapshot(self) -> Mapping[str, Any]:
        world = self._require_world()
        data = world.snapshot()
        meta = {"tick": self._tick}
        return {"agents": data, "meta": meta}

    @property
    def raw_world(self) -> WorldState:
        """Expose the underlying world state for adapters that need it."""

        return self._require_world()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _require_world(self) -> WorldState:
        if self._world is None:
            raise RuntimeError("World runtime not initialised")
        return self._world


def _resolve_ticks_per_day(cfg: Any) -> int:
    observations_cfg = getattr(cfg, "observations_config", None)
    hybrid = getattr(observations_cfg, "hybrid", None)
    ticks = getattr(hybrid, "time_ticks_per_day", 1440) if hybrid is not None else 1440
    return max(1, int(ticks))


@register("world", "default")
def _build_default_world(*, cfg: Any, **options: Any) -> DefaultWorldAdapter:
    seed = options.get("seed") if isinstance(options, Mapping) else None
    return DefaultWorldAdapter(cfg, seed=seed)
