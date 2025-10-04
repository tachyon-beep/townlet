"""Affordance runtime coordinator extracted from WorldState."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping

from townlet.world.affordances import DefaultAffordanceRuntime, RunningAffordanceState


class AffordanceCoordinator:
    """Wrapper around the DefaultAffordanceRuntime exposing a minimal API."""

    def __init__(self, runtime: DefaultAffordanceRuntime) -> None:
        self._runtime = runtime

    def start(
        self,
        agent_id: str,
        object_id: str,
        affordance_id: str,
        *,
        tick: int,
    ) -> tuple[bool, dict[str, object]]:
        return self._runtime.start(agent_id, object_id, affordance_id, tick=tick)

    def release(
        self,
        agent_id: str,
        object_id: str,
        *,
        success: bool,
        reason: str | None,
        requested_affordance_id: str | None,
        tick: int,
    ) -> tuple[str | None, dict[str, object]]:
        return self._runtime.release(
            agent_id,
            object_id,
            success=success,
            reason=reason,
            requested_affordance_id=requested_affordance_id,
            tick=tick,
        )

    def handle_blocked(self, object_id: str, tick: int) -> None:
        self._runtime.handle_blocked(object_id, tick)

    def resolve(self, *, tick: int) -> None:
        self._runtime.resolve(tick=tick)

    def running_snapshot(self) -> dict[str, RunningAffordanceState]:
        snapshot = self._runtime.running_snapshot()
        return {str(object_id): deepcopy(state) for object_id, state in snapshot.items()}

    def clear(self) -> None:
        self._runtime.clear()

    def remove_agent(self, agent_id: str) -> None:
        self._runtime.remove_agent(agent_id)

    @property
    def runtime(self) -> DefaultAffordanceRuntime:
        return self._runtime
