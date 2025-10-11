from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any, Callable, cast

from townlet.console.command import ConsoleCommandEnvelope
from townlet.snapshots.state import SnapshotState
from townlet.world.dto.observation import (
    AgentObservationDTO,
    GlobalObservationDTO,
    ObservationEnvelope,
)
from townlet.world.grid import WorldState
from townlet.world.runtime import RuntimeStepResult


@dataclass(slots=True)
class DummyWorldRuntime:
    """Minimal world runtime satisfying the `WorldRuntime` port."""

    agents_list: tuple[str, ...] = field(default_factory=tuple)
    config_id: str = "dummy-config"
    _tick: int = field(default=0, init=False, repr=False)
    _last_actions: dict[str, Any] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        self._tick = 0
        self._last_actions.clear()

    def reset(self, seed: int | None = None) -> None:  # pragma: no cover - simple state reset
        self._tick = 0
        self._last_actions.clear()

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable[ConsoleCommandEnvelope] | None = None,
        action_provider: Callable[[WorldState, int], Mapping[str, Any]] | None = None,
        policy_actions: Mapping[str, Any] | None = None,
    ) -> RuntimeStepResult:
        commands = list(console_operations or ())

        actions: dict[str, Any] = {}
        if action_provider is not None:
            actions.update(action_provider(_DUMMY_WORLD_STATE, tick))
        if policy_actions:
            actions.update(policy_actions)
        self._last_actions = actions
        self._tick = tick
        return RuntimeStepResult(
            console_results=[],
            events=[{"tick": tick, "commands": len(commands)}],
            actions=dict(actions),
            terminated={},
            termination_reasons={},
        )

    def agents(self) -> Iterable[str]:
        return self.agents_list

    def observe(self, agent_ids: Iterable[str] | None = None) -> ObservationEnvelope:
        selected = tuple(agent_ids) if agent_ids is not None else tuple(self.agents_list)
        agents = [
            AgentObservationDTO(
                agent_id=agent,
                metadata={"agent_id": agent},
                needs={},
                wallet=None,
                inventory={},
                job={},
                personality=None,
                queue_state=None,
                pending_intent=None,
                map=None,
                features=None,
                terminated=False,
            )
            for agent in selected
        ]
        return ObservationEnvelope(
            tick=self._tick,
            agents=agents,
            global_context=GlobalObservationDTO(),
            actions=dict(self._last_actions),
            terminated={agent: False for agent in selected},
            termination_reasons={agent: "" for agent in selected},
        )

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        self._last_actions = dict(actions)

    def snapshot(
        self,
        *,
        config: Any | None = None,
        telemetry: Any | None = None,
        stability: Any | None = None,
        promotion: Any | None = None,
        rng_streams: Mapping[str, Any] | None = None,
        identity: Mapping[str, Any] | None = None,
    ) -> SnapshotState:
        return SnapshotState(config_id=self.config_id, tick=self._tick)



@dataclass(slots=True)
class _StubWorldState:
    config_id: str = "dummy-config"


_DUMMY_WORLD_STATE = cast("WorldState", _StubWorldState())


# Late imports to avoid circular dependencies during stub construction.
from typing import Callable  # noqa: E402  # isort:skip
