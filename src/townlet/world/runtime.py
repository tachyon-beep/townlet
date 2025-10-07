"""Runtime façade coordinating world tick sequencing.

The runtime acts as the glue between the simulation loop and the sprawling
`WorldState` helpers. It is responsible for staging policy actions, applying
console commands, advancing perturbations, and yielding the artefacts other
subsystems consume (policy, telemetry, rewards, etc.).
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from townlet.console.command import ConsoleCommandEnvelope, ConsoleCommandResult
from townlet.scheduler.perturbations import PerturbationScheduler

if TYPE_CHECKING:  # pragma: no cover
    from townlet.lifecycle.manager import LifecycleManager
    from townlet.world.grid import WorldState
    from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


ActionMapping = Mapping[str, object]
ActionProvider = Callable[["WorldState", int], ActionMapping]


@dataclass(slots=True)
class RuntimeStepResult:
    """Outcome of a world runtime tick.

    The runtime reports the console responses, emitted events and the action
    payload applied during the tick so downstream systems (telemetry, rewards,
    policy training) can consume a consistent view of what happened.
    """

    console_results: list[ConsoleCommandResult] = field(default_factory=list)
    events: list[dict[str, object]] = field(default_factory=list)
    actions: dict[str, object] = field(default_factory=dict)
    terminated: dict[str, bool] = field(default_factory=dict)
    termination_reasons: dict[str, str] = field(default_factory=dict)


class WorldRuntime:
    """Facade that sequences world-side operations each tick.

    The object is intentionally stateful: it buffers console operations and
    actions staged by the simulation loop so they are consumed exactly once per
    tick. `SimulationLoop` injects dependencies during construction and calls
    :meth:`tick` on every iteration.
    """

    def __init__(
        self,
        *,
        world: WorldState,
        lifecycle: LifecycleManager,
        perturbations: PerturbationScheduler,
        ticks_per_day: int,
    ) -> None:
        self._world = world
        self._lifecycle = lifecycle
        self._perturbations = perturbations
        self._ticks_per_day = max(0, int(ticks_per_day))
        self._queued_console: list[ConsoleCommandEnvelope] = []
        self._pending_actions: dict[str, object] = {}
        self._world_adapter: WorldRuntimeAdapterProtocol | None = None

    @property
    def world(self) -> WorldState:
        return self._world

    def bind_world(self, world: WorldState) -> None:
        """Rebind the runtime to a freshly constructed ``WorldState``."""

        self._world = world

    def bind_world_adapter(
        self, adapter: WorldRuntimeAdapterProtocol
    ) -> None:  # pragma: no cover - thin setter
        self._world_adapter = adapter

    @property
    def world_adapter(self) -> WorldRuntimeAdapterProtocol | None:
        return self._world_adapter

    def queue_console(self, operations: Iterable[ConsoleCommandEnvelope]) -> None:
        """Buffer console operations for the next tick.

        The buffered operations are drained the next time :meth:`tick` executes.
        Callers typically pass in commands drained from the telemetry layer.
        """

        self._queued_console.extend(list(operations))

    def apply_actions(self, actions: ActionMapping) -> None:
        """Stage policy actions for the next tick.

        Actions staged here are consumed unless :meth:`tick` is provided with a
        dedicated ``policy_actions`` mapping or an ``action_provider`` callable.
        """

        self._pending_actions = dict(actions)

    def snapshot(self) -> dict[str, object]:  # pragma: no cover - thin pass-through
        """Expose the underlying world snapshot for diagnostics/tests."""

        snapshot_getter = getattr(self._world, "snapshot", None)
        if callable(snapshot_getter):
            return snapshot_getter()
        raise AttributeError("WorldState does not expose a snapshot() method")

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable[ConsoleCommandEnvelope] | None = None,
        action_provider: ActionProvider | None = None,
        policy_actions: ActionMapping | None = None,
    ) -> RuntimeStepResult:
        """Advance the world by one tick and return observable artefacts.

        Args:
            tick: Simulation tick to stamp on the world state and output.
            console_operations: Optional override for the buffered console queue.
            action_provider: Callback used to fetch staged policy actions when
                ``policy_actions`` is not supplied.
            policy_actions: Explicit mapping of actions to apply this tick.

        Returns:
            RuntimeStepResult containing console outputs, emitted events and
            termination state for each agent.
        """

        world = self._world
        lifecycle = self._lifecycle
        perturbations = self._perturbations

        queued_ops = (
            list(console_operations)
            if console_operations is not None
            else list(self._queued_console)
        )
        self._queued_console.clear()

        prepared_actions: MutableMapping[str, object]
        if policy_actions is not None:
            prepared_actions = dict(policy_actions)
        elif action_provider is not None:
            prepared_actions = dict(action_provider(world, tick))
        else:
            prepared_actions = dict(self._pending_actions)
        self._pending_actions.clear()

        world.tick = tick
        lifecycle.process_respawns(world, tick=tick)
        world.apply_console(queued_ops)
        console_results = list(world.consume_console_results())
        perturbations.tick(world, current_tick=tick)
        world.apply_actions(prepared_actions)
        world.resolve_affordances(current_tick=tick)
        if self._ticks_per_day and tick % self._ticks_per_day == 0:
            world.apply_nightly_reset()
        terminated = dict(lifecycle.evaluate(world, tick=tick))
        termination_reasons = dict(lifecycle.termination_reasons())
        events = list(world.drain_events())

        return RuntimeStepResult(
            console_results=console_results,
            events=events,
            actions=dict(prepared_actions),
            terminated=terminated,
            termination_reasons=termination_reasons,
        )
