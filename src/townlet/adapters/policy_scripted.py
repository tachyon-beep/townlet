"""Adapter wiring the scripted policy backend to the policy port."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any, Callable

from townlet.ports.policy import PolicyBackend
from townlet.policy.runner import PolicyRuntime


class ScriptedPolicyAdapter(PolicyBackend):
    """Adapter that delegates to the legacy scripted policy runtime."""

    def __init__(
        self,
        backend: PolicyRuntime,
    ) -> None:
        self._backend = backend
        self._tick: int = 0
        self._world_provider: Callable[[], Any] | None = None

    def on_episode_start(self, agent_ids: Iterable[str]) -> None:  # pragma: no cover - thin bridge
        _ = agent_ids
        self._backend.reset_state()

    def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]:
        del observations  # Observations currently unused; backend operates on world state.
        if self._world_provider is None:
            raise RuntimeError("Policy adapter world provider not configured")
        world = self._world_provider()
        actions = self._backend.decide(world, self._tick)
        self._tick += 1
        return actions

    def on_episode_end(self) -> None:  # pragma: no cover - thin bridge
        self._backend.flush_transitions({})

    def attach_world(self, provider: Callable[[], Any]) -> None:
        """Transitional hook for legacy paths that still expect world access."""

        self._world_provider = provider

    @property
    def backend(self) -> PolicyRuntime:
        """Expose the wrapped legacy backend for transitional call sites."""

        return self._backend


__all__ = ["ScriptedPolicyAdapter"]
