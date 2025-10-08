"""Adapter that exposes scripted policies via the new port."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from townlet.factories.registry import register
from townlet.policy.scripted import (
    ScriptedPolicyAdapter as LegacyScriptedPolicyAdapter,
)
from townlet.policy.scripted import (
    get_scripted_policy,
)
from townlet.ports.policy import PolicyBackend
from townlet.ports.world import WorldRuntime
from townlet.world.grid import WorldState


class ScriptedPolicyAdapter(PolicyBackend):
    """Adapter for the legacy scripted policy backend."""

    def __init__(self, cfg: Any, *, policy: str = "idle") -> None:
        self._cfg = cfg
        self._policy_name = policy
        self._backend = LegacyScriptedPolicyAdapter(get_scripted_policy(policy))
        self._active_agents: list[str] = []
        self._world: WorldRuntime | None = None

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:
        self._active_agents = list(agent_ids)

    def bind_world(self, world: WorldRuntime) -> None:
        """Bind the world runtime so decisions can access the world state."""

        self._world = world

    def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]:
        meta = observations.get("__meta__", {}) if isinstance(observations, Mapping) else {}
        tick = int(meta.get("tick", 0))
        world = self._require_world_state()
        actions = self._backend.decide(world, tick)
        return actions

    def on_episode_end(self) -> None:
        self._backend.post_step({}, {})
        self._active_agents = []

    def _require_world_state(self) -> WorldState:
        if self._world is None:
            raise RuntimeError("ScriptedPolicyAdapter requires bind_world() before decide()")
        raw_world = getattr(self._world, "raw_world", None)
        if raw_world is None:
            raise RuntimeError("Bound world runtime does not expose raw_world")
        if not isinstance(raw_world, WorldState):
            raise RuntimeError("raw_world attribute must be a WorldState")
        return raw_world


@register("policy", "scripted")
def _build_scripted_policy(*, cfg: Any, **options: Any) -> ScriptedPolicyAdapter:
    policy_name = options.get("policy") if isinstance(options, Mapping) else None
    return ScriptedPolicyAdapter(cfg, policy=policy_name or "idle")
