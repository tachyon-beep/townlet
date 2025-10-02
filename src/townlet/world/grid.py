"""Grid world representation and affordance integration."""

from __future__ import annotations

import random
import logging
import os
import copy
from collections import OrderedDict, deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from townlet.agents.models import Personality
from townlet.agents.relationship_modifiers import (
    RelationshipDelta,
    RelationshipEvent,
    apply_personality_modifiers,
)
from townlet.config import EmploymentConfig, SimulationConfig
from townlet.config.affordance_manifest import (
    AffordanceManifestError,
    load_affordance_manifest,
)
from townlet.console.command import (
    ConsoleCommandEnvelope,
    ConsoleCommandError,
    ConsoleCommandResult,
)
from townlet.observations.embedding import EmbeddingAllocator
from townlet.telemetry.relationship_metrics import RelationshipChurnAccumulator
from townlet.world.queue_manager import QueueManager
from townlet.world.relationships import RelationshipLedger, RelationshipParameters
from townlet.world.rivalry import RivalryLedger, RivalryParameters
from townlet.world.hooks import load_modules as load_hook_modules
from townlet.world.preconditions import (
    CompiledPrecondition,
    PreconditionSyntaxError,
    compile_preconditions,
    evaluate_preconditions,
)


logger = logging.getLogger(__name__)

_CONSOLE_HISTORY_LIMIT = 512
_CONSOLE_RESULT_BUFFER_LIMIT = 256


class HookRegistry:
    """Registers named affordance hooks and returns handlers on demand."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}

    def register(self, name: str, handler: Callable[[dict[str, Any]], None]) -> None:
        if not isinstance(name, str) or not name:
            raise ValueError("Hook name must be a non-empty string")
        if not callable(handler):
            raise TypeError("Hook handler must be callable")
        self._handlers.setdefault(name, []).append(handler)

    def handlers_for(self, name: str) -> tuple[Callable[[dict[str, Any]], None], ...]:
        return tuple(self._handlers.get(name, ()))

    def clear(self, name: str | None = None) -> None:
        if name is None:
            self._handlers.clear()
            return
        self._handlers.pop(name, None)


class _ConsoleHandlerEntry:
    """Metadata for registered console handlers."""

    __slots__ = ("handler", "mode", "require_cmd_id")

    def __init__(
        self,
        handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult],
        *,
        mode: str = "viewer",
        require_cmd_id: bool = False,
    ) -> None:
        self.handler = handler
        self.mode = mode
        self.require_cmd_id = require_cmd_id


def _default_personality() -> Personality:
    """Provide a neutral personality for agents lacking explicit traits."""

    return Personality(extroversion=0.0, forgiveness=0.0, ambition=0.0)


_BASE_NEEDS: tuple[str, ...] = ("hunger", "hygiene", "energy")


@dataclass
class AgentSnapshot:
    """Minimal agent view used for scaffolding."""

    agent_id: str
    position: tuple[int, int]
    needs: dict[str, float]
    wallet: float = 0.0
    home_position: tuple[int, int] | None = None
    origin_agent_id: str | None = None
    personality: Personality = field(default_factory=_default_personality)
    inventory: dict[str, int] = field(default_factory=dict)
    job_id: str | None = None
    on_shift: bool = False
    lateness_counter: int = 0
    last_late_tick: int = -1
    shift_state: str = "pre_shift"
    late_ticks_today: int = 0
    attendance_ratio: float = 0.0
    absent_shifts_7d: int = 0
    wages_withheld: float = 0.0
    exit_pending: bool = False
    last_action_id: str = ""
    last_action_success: bool = False
    last_action_duration: int = 0
    episode_tick: int = 0

    def __post_init__(self) -> None:
        clamped: dict[str, float] = {}
        for key, value in self.needs.items():
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                numeric = 0.0
            clamped[key] = max(0.0, min(1.0, numeric))
        for key in _BASE_NEEDS:
            clamped.setdefault(key, 0.5)
        self.needs = clamped
        if self.home_position is not None:
            x, y = int(self.home_position[0]), int(self.home_position[1])
            self.home_position = (x, y)
        if self.origin_agent_id is None:
            self.origin_agent_id = self.agent_id


@dataclass
class InteractiveObject:
    """Represents an interactive world object with optional occupancy."""

    object_id: str
    object_type: str
    occupied_by: str | None = None
    stock: dict[str, int] = field(default_factory=dict)
    position: tuple[int, int] | None = None


@dataclass
class RunningAffordance:
    """Tracks an affordance currently executing on an object."""

    agent_id: str
    affordance_id: str
    duration_remaining: int
    effects: dict[str, float]


@dataclass
class AffordanceSpec:
    """Static affordance definition loaded from configuration."""

    affordance_id: str
    object_type: str
    duration: int
    effects: dict[str, float]
    preconditions: list[str] = field(default_factory=list)
    hooks: dict[str, list[str]] = field(default_factory=dict)
    compiled_preconditions: tuple[CompiledPrecondition, ...] = field(
        default_factory=tuple,
        repr=False,
    )


@dataclass
class WorldState:
    """Holds mutable world state for the simulation tick."""

    config: SimulationConfig
    agents: dict[str, AgentSnapshot] = field(default_factory=dict)
    tick: int = 0
    queue_manager: QueueManager = field(init=False)
    embedding_allocator: EmbeddingAllocator = field(init=False)
    _active_reservations: dict[str, str] = field(init=False, default_factory=dict)
    objects: dict[str, InteractiveObject] = field(init=False, default_factory=dict)
    affordances: dict[str, AffordanceSpec] = field(init=False, default_factory=dict)
    _running_affordances: dict[str, RunningAffordance] = field(init=False, default_factory=dict)
    _pending_events: dict[int, list[dict[str, Any]]] = field(init=False, default_factory=dict)
    store_stock: dict[str, dict[str, int]] = field(init=False, default_factory=dict)
    _job_keys: list[str] = field(init=False, default_factory=list)
    _employment_state: dict[str, dict[str, Any]] = field(init=False, default_factory=dict)
    _employment_exit_queue: list[str] = field(init=False, default_factory=list)
    _employment_exits_today: int = field(init=False, default=0)
    _employment_exit_queue_timestamps: dict[str, int] = field(init=False, default_factory=dict)
    _employment_manual_exits: set[str] = field(init=False, default_factory=set)

    _rivalry_ledgers: dict[str, RivalryLedger] = field(init=False, default_factory=dict)
    _relationship_ledgers: dict[str, RelationshipLedger] = field(init=False, default_factory=dict)
    _relationship_churn: RelationshipChurnAccumulator = field(init=False)
    _rivalry_events: deque[dict[str, Any]] = field(init=False, default_factory=deque)
    _relationship_window_ticks: int = 600
    _recent_meal_participants: dict[str, dict[str, Any]] = field(init=False, default_factory=dict)
    _chat_events: list[dict[str, Any]] = field(init=False, default_factory=list)
    _rng_seed: Optional[int] = field(init=False, default=None)
    _rng_state: Optional[tuple[Any, ...]] = field(init=False, default=None)
    _rng: Optional[random.Random] = field(init=False, default=None, repr=False)
    _affordance_manifest_info: dict[str, object] = field(init=False, default_factory=dict)
    _objects_by_position: dict[tuple[int, int], list[str]] = field(init=False, default_factory=dict)
    _console_handlers: dict[str, _ConsoleHandlerEntry] = field(init=False, default_factory=dict)
    _console_cmd_history: OrderedDict[str, ConsoleCommandResult] = field(
        init=False, default_factory=OrderedDict
    )
    _console_result_buffer: deque[ConsoleCommandResult] = field(init=False, default_factory=deque)
    _hook_registry: HookRegistry = field(init=False, repr=False)
    _ctx_reset_requests: set[str] = field(init=False, default_factory=set)
    _respawn_counters: dict[str, int] = field(init=False, default_factory=dict)

    @classmethod
    def from_config(
        cls,
        config: SimulationConfig,
        *,
        rng: Optional[random.Random] = None,
    ) -> "WorldState":
        """Bootstrap the initial world from config."""

        instance = cls(config=config)
        instance.attach_rng(rng or random.Random())
        return instance

    def __post_init__(self) -> None:
        self.queue_manager = QueueManager(config=self.config)
        self.embedding_allocator = EmbeddingAllocator(config=self.config)
        self._active_reservations = {}
        self.objects = {}
        self.affordances = {}
        self._running_affordances = {}
        self._pending_events = {}
        self.store_stock = {}
        self._job_keys = list(self.config.jobs.keys())
        self._employment_state = {}
        self._employment_exit_queue = []
        self._employment_exits_today = 0
        self._employment_exit_queue_timestamps = {}
        self._employment_manual_exits = set()
        self._rivalry_ledgers = {}
        self._relationship_ledgers = {}
        self._relationship_window_ticks = 600
        self._relationship_churn = RelationshipChurnAccumulator(
            window_ticks=self._relationship_window_ticks,
            max_samples=8,
        )
        self._rivalry_events = deque(maxlen=256)
        self._recent_meal_participants = {}
        self._chat_events = []
        self._load_affordance_definitions()
        self._rng_seed = None
        if self._rng is None:
            self._rng = random.Random()
        self._rng_state = self._rng.getstate()
        self._console_handlers = {}
        self._console_cmd_history = OrderedDict()
        self._console_result_buffer = deque(maxlen=_CONSOLE_RESULT_BUFFER_LIMIT)
        self._register_default_console_handlers()
        self._hook_registry = HookRegistry()
        modules = ["townlet.world.hooks.default"]
        extra = os.environ.get("TOWNLET_AFFORDANCE_HOOK_MODULES")
        if extra:
            modules.extend(module.strip() for module in extra.split(",") if module.strip())
        load_hook_modules(self, modules)

    def generate_agent_id(self, base_id: str) -> str:
        base = base_id or "agent"
        counter = self._respawn_counters.get(base, 0)
        while True:
            counter += 1
            candidate = f"{base}#{counter}"
            if candidate not in self.agents:
                self._respawn_counters[base] = counter
                return candidate

    def apply_console(self, operations: Iterable[Any]) -> None:
        """Apply console operations before the tick sequence runs."""
        for operation in operations:
            try:
                envelope = ConsoleCommandEnvelope.from_payload(operation)
            except ConsoleCommandError as exc:
                fallback_envelope = ConsoleCommandEnvelope(
                    name=str(getattr(operation, "name", "unknown") or "unknown"),
                    args=[],
                    kwargs={},
                    cmd_id=getattr(operation, "cmd_id", None)
                    if isinstance(getattr(operation, "cmd_id", None), str)
                    else None,
                    issuer=None,
                )
                result = ConsoleCommandResult.from_error(
                    fallback_envelope,
                    exc.code,
                    exc.message,
                    details=exc.details or {},
                    tick=self.tick,
                )
                logger.warning("Rejected console command: %s", exc)
                self._record_console_result(result)
                continue
            except Exception:  # pragma: no cover - defensive
                logger.exception("Failed to normalise console command payload: %r", operation)
                continue

            handler_entry = self._console_handlers.get(envelope.name)
            if handler_entry is None:
                self._record_console_result(
                    ConsoleCommandResult.from_error(
                        envelope,
                        "unsupported",
                        f"Unknown console command '{envelope.name}'",
                        tick=self.tick,
                    )
                )
                continue

            if handler_entry.mode == "admin" and envelope.mode != "admin":
                self._record_console_result(
                    ConsoleCommandResult.from_error(
                        envelope,
                        "forbidden",
                        "Command requires admin mode",
                        tick=self.tick,
                    )
                )
                continue

            if handler_entry.require_cmd_id and not envelope.cmd_id:
                self._record_console_result(
                    ConsoleCommandResult.from_error(
                        envelope,
                        "usage",
                        "Command requires cmd_id for idempotency",
                        tick=self.tick,
                    )
                )
                continue

            if envelope.cmd_id and envelope.cmd_id in self._console_cmd_history:
                cached = self._console_cmd_history[envelope.cmd_id].clone()
                cached.tick = self.tick
                self._record_console_result(cached)
                continue

            try:
                result = handler_entry.handler(envelope)
            except ConsoleCommandError as exc:
                result = ConsoleCommandResult.from_error(
                    envelope,
                    exc.code,
                    exc.message,
                    details=exc.details or {},
                    tick=self.tick,
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Console command '%s' failed", envelope.name)
                result = ConsoleCommandResult.from_error(
                    envelope,
                    "internal",
                    "Internal error while executing command",
                    details={"exception": str(exc)},
                    tick=self.tick,
                )

            if result.tick is None:
                result.tick = self.tick
            self._record_console_result(result)

    def attach_rng(self, rng: random.Random) -> None:
        """Attach a deterministic RNG used for world-level randomness."""

        self._rng = rng
        self._rng_state = rng.getstate()

    @property
    def rng(self) -> random.Random:
        if self._rng is None:
            self._rng = random.Random()
        return self._rng

    def get_rng_state(self) -> tuple[Any, ...]:
        return self.rng.getstate()

    def set_rng_state(self, state: tuple[Any, ...]) -> None:
        self.rng.setstate(state)
        self._rng_state = state

    # ------------------------------------------------------------------
    # Console dispatcher helpers
    # ------------------------------------------------------------------

    def register_console_handler(
        self,
        name: str,
        handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult],
        *,
        mode: str = "viewer",
        require_cmd_id: bool = False,
    ) -> None:
        """Register a console handler for queued commands."""

        self._console_handlers[name] = _ConsoleHandlerEntry(
            handler, mode=mode, require_cmd_id=require_cmd_id
        )

    def register_affordance_hook(
        self, name: str, handler: Callable[[dict[str, Any]], None]
    ) -> None:
        """Register a callable invoked when a manifest hook fires."""

        self._hook_registry.register(name, handler)

    def clear_affordance_hooks(self, name: str | None = None) -> None:
        """Clear registered affordance hooks (used primarily for tests)."""

        self._hook_registry.clear(name)

    def consume_console_results(self) -> list[ConsoleCommandResult]:
        """Return and clear buffered console results."""

        results = list(self._console_result_buffer)
        self._console_result_buffer.clear()
        return results

    def _record_console_result(self, result: ConsoleCommandResult) -> None:
        if result.cmd_id:
            self._console_cmd_history[result.cmd_id] = result.clone()
            while len(self._console_cmd_history) > _CONSOLE_HISTORY_LIMIT:
                self._console_cmd_history.popitem(last=False)
        self._console_result_buffer.append(result)

    def _dispatch_affordance_hooks(
        self,
        stage: str,
        hook_names: Iterable[str],
        *,
        agent_id: str,
        object_id: str,
        spec: AffordanceSpec | None,
        extra: Mapping[str, Any] | None = None,
    ) -> bool:
        if not hook_names or spec is None:
            return True
        continue_execution = True
        for hook_name in hook_names:
            handlers = self._hook_registry.handlers_for(hook_name)
            if not handlers:
                continue
            base_context = {
                "stage": stage,
                "hook": hook_name,
                "tick": self.tick,
                "agent_id": agent_id,
                "object_id": object_id,
                "affordance_id": spec.affordance_id,
                "world": self,
                "spec": spec,
            }
            if extra:
                base_context.update(extra)
            for handler in handlers:
                context = dict(base_context)
                try:
                    handler(context)
                except Exception:  # pragma: no cover - defensive
                    logger.exception("Affordance hook '%s' failed", hook_name)
                    continue_execution = False
                    continue
                if context.get("cancel"):
                    continue_execution = False
        return continue_execution

    def _build_precondition_context(
        self,
        *,
        agent_id: str,
        object_id: str,
        spec: AffordanceSpec,
    ) -> dict[str, Any]:
        agent = self.agents.get(agent_id)
        obj = self.objects.get(object_id)
        queue_snapshot = self.queue_manager.queue_snapshot(object_id)
        active_reservation = self.queue_manager.active_agent(object_id)
        observations_cfg = getattr(self.config, "observations_config", None)
        if observations_cfg is not None:
            hybrid_cfg = getattr(observations_cfg, "hybrid", None)
            ticks_per_day = getattr(hybrid_cfg, "time_ticks_per_day", 1440)
        else:
            ticks_per_day = 1440
        ticks_per_day = max(1, int(ticks_per_day))
        day = self.tick // ticks_per_day

        agent_context: dict[str, Any] = {}
        needs: dict[str, float] = {}
        inventory: dict[str, int] = {}
        if agent is not None:
            needs = {key: float(value) for key, value in agent.needs.items()}
            inventory = {key: int(value) for key, value in agent.inventory.items()}
            agent_context = {
                "agent_id": agent.agent_id,
                "position": list(agent.position),
                "wallet": float(agent.wallet),
                "job_id": agent.job_id,
                "on_shift": bool(agent.on_shift),
                "needs": needs,
                "inventory": inventory,
                "lateness_counter": int(agent.lateness_counter),
                "attendance_ratio": float(agent.attendance_ratio),
                "wages_withheld": float(agent.wages_withheld),
                "shift_state": agent.shift_state,
            }

        stock: dict[str, Any] = {}
        object_context: dict[str, Any] = {}
        if obj is not None:
            stock = {key: value for key, value in obj.stock.items()}
            position = list(obj.position) if obj.position is not None else None
            occupied_by = obj.occupied_by
            object_context = {
                "object_id": obj.object_id,
                "object_type": obj.object_type,
                "position": position,
                "occupied_by": occupied_by,
                "stock": stock,
            }
        else:
            occupied_by = None

        queue_list = list(queue_snapshot) if queue_snapshot else []
        context: dict[str, Any] = {
            "affordance_id": spec.affordance_id,
            "agent": agent_context,
            "object": object_context,
            "world": {
                "tick": int(self.tick),
                "day": int(day),
            },
            "needs": needs,
            "inventory": inventory,
            "wallet": agent_context.get("wallet"),
            "queue": queue_list,
            "queue_length": len(queue_list),
            "reservation_active": active_reservation is not None,
            "reservation_holder": active_reservation,
            "occupied": bool(occupied_by and occupied_by != agent_id),
            "power_on": bool(stock.get("power_on", 0)) if stock else None,
            "meal_available": bool(stock.get("meals", 0)) if stock else None,
            "stock": stock,
        }
        return context

    def _snapshot_precondition_context(self, context: Mapping[str, Any]) -> dict[str, Any]:
        def _clone(value: Any) -> Any:
            if isinstance(value, dict):
                return {str(key): _clone(val) for key, val in value.items()}
            if isinstance(value, list):
                return [_clone(item) for item in value]
            if isinstance(value, tuple):
                return [_clone(item) for item in value]
            return value

        return {str(key): _clone(val) for key, val in context.items()}

    def _register_default_console_handlers(self) -> None:
        self.register_console_handler(
            "noop", self._console_noop_handler, mode="viewer", require_cmd_id=False
        )
        self.register_console_handler(
            "employment_status",
            self._console_employment_status,
            mode="viewer",
            require_cmd_id=False,
        )
        self.register_console_handler(
            "employment_exit",
            self._console_employment_exit,
            mode="admin",
            require_cmd_id=True,
        )
        self.register_console_handler(
            "spawn",
            self._console_spawn_agent,
            mode="admin",
            require_cmd_id=True,
        )
        self.register_console_handler(
            "teleport",
            self._console_teleport_agent,
            mode="admin",
            require_cmd_id=True,
        )
        self.register_console_handler(
            "setneed",
            self._console_set_need,
            mode="admin",
            require_cmd_id=True,
        )
        self.register_console_handler(
            "price",
            self._console_set_price,
            mode="admin",
            require_cmd_id=True,
        )
        self.register_console_handler(
            "force_chat",
            self._console_force_chat,
            mode="admin",
            require_cmd_id=True,
        )
        self.register_console_handler(
            "set_rel",
            self._console_set_relationship,
            mode="admin",
            require_cmd_id=True,
        )

    def _console_noop_handler(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        return ConsoleCommandResult.ok(envelope, {}, tick=self.tick)

    def _console_employment_status(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        metrics = self.employment_queue_snapshot()
        payload = {
            "metrics": metrics,
            "pending_agents": list(metrics.get("pending", [])),
        }
        return ConsoleCommandResult.ok(envelope, payload, tick=self.tick)

    def _console_employment_exit(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        if not envelope.args:
            raise ConsoleCommandError("usage", "employment_exit <review|approve|defer> [agent_id]")
        action = str(envelope.args[0])
        if action == "review":
            return ConsoleCommandResult.ok(
                envelope, self.employment_queue_snapshot(), tick=self.tick
            )
        if len(envelope.args) < 2:
            raise ConsoleCommandError("usage", "employment_exit <approve|defer> <agent_id>")
        agent_id = str(envelope.args[1])
        if action == "approve":
            success = self.employment_request_manual_exit(agent_id, tick=self.tick)
            return ConsoleCommandResult.ok(
                envelope,
                {"approved": bool(success), "agent_id": agent_id},
                tick=self.tick,
            )
        if action == "defer":
            success = self.employment_defer_exit(agent_id)
            return ConsoleCommandResult.ok(
                envelope,
                {"deferred": bool(success), "agent_id": agent_id},
                tick=self.tick,
            )
        raise ConsoleCommandError(
            "usage", "Unknown employment_exit action", details={"action": action}
        )

    def _assign_job_if_missing(self, snapshot: AgentSnapshot) -> None:
        if snapshot.job_id is None and self._job_keys:
            snapshot.job_id = self._job_keys[len(self.agents) % len(self._job_keys)]

    def remove_agent(self, agent_id: str, tick: int) -> dict[str, Any] | None:
        snapshot = self.agents.pop(agent_id, None)
        if snapshot is None:
            return None
        self.queue_manager.remove_agent(agent_id, tick)
        for object_id, running in list(self._running_affordances.items()):
            if running.agent_id == agent_id:
                self._running_affordances.pop(object_id, None)
        for object_id, occupant in list(self._active_reservations.items()):
            if occupant == agent_id:
                self.queue_manager.release(object_id, agent_id, tick, success=False)
                self._active_reservations.pop(object_id, None)
                obj = self.objects.get(object_id)
                if obj is not None:
                    obj.occupied_by = None
        self.embedding_allocator.release(agent_id, tick)
        self._employment_state.pop(agent_id, None)
        self._employment_manual_exits.discard(agent_id)
        self._employment_exit_queue_timestamps.pop(agent_id, None)
        if agent_id in self._employment_exit_queue:
            self._employment_exit_queue.remove(agent_id)
        self._employment_remove_from_queue(agent_id)
        self._relationship_ledgers.pop(agent_id, None)
        for ledger in self._relationship_ledgers.values():
            ledger.remove_tie(agent_id, reason="removed")
        self._rivalry_ledgers.pop(agent_id, None)
        for ledger in self._rivalry_ledgers.values():
            ledger.remove(agent_id, reason="removed")
        for record in self._recent_meal_participants.values():
            participants = record.get("agents")
            if isinstance(participants, set):
                participants.discard(agent_id)
        self._chat_events = [
            entry
            for entry in self._chat_events
            if entry.get("agent") != agent_id
            and entry.get("speaker") != agent_id
            and entry.get("listener") != agent_id
        ]
        blueprint = {
            "agent_id": snapshot.agent_id,
            "origin_agent_id": snapshot.origin_agent_id or snapshot.agent_id,
            "personality": snapshot.personality,
            "job_id": snapshot.job_id,
            "position": snapshot.position,
            "home_position": snapshot.home_position,
        }
        self._emit_event(
            "agent_removed",
            {
                "agent_id": snapshot.agent_id,
                "tick": tick,
            },
        )
        return blueprint

    def respawn_agent(self, blueprint: Mapping[str, Any]) -> None:
        agent_id = str(blueprint.get("agent_id", ""))
        if not agent_id or agent_id in self.agents:
            return
        origin_agent_id = str(
            blueprint.get("origin_agent_id") or blueprint.get("agent_id") or agent_id
        )
        position = blueprint.get("position")
        position_tuple: tuple[int, int]
        if (
            isinstance(position, (list, tuple))
            and len(position) == 2
            and all(isinstance(coord, (int, float)) for coord in position)
        ):
            x, y = int(position[0]), int(position[1])
            candidate = (x, y)
            position_tuple = candidate if self._is_position_walkable(candidate) else (0, 0)
        else:
            position_tuple = (0, 0)

        home_position = blueprint.get("home_position")
        home_tuple: tuple[int, int] | None
        if (
            isinstance(home_position, (list, tuple))
            and len(home_position) == 2
            and all(isinstance(coord, (int, float)) for coord in home_position)
        ):
            home_tuple = (int(home_position[0]), int(home_position[1]))
        elif isinstance(home_position, tuple) and len(home_position) == 2:
            home_tuple = (int(home_position[0]), int(home_position[1]))
        else:
            home_tuple = None
        snapshot = AgentSnapshot(
            agent_id=agent_id,
            position=position_tuple,
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=0.0,
            home_position=home_tuple,
            origin_agent_id=origin_agent_id,
        )
        personality = blueprint.get("personality")
        if personality is not None:
            snapshot.personality = personality
        job_id = blueprint.get("job_id")
        if isinstance(job_id, str):
            snapshot.job_id = job_id
        self.agents[agent_id] = snapshot
        self._assign_job_if_missing(snapshot)
        self._sync_agent_spawn(snapshot)
        self._emit_event(
            "agent_respawn",
            {
                "agent_id": agent_id,
                "original_agent_id": origin_agent_id,
                "tick": self.tick,
            },
        )

    def _sync_agent_spawn(self, snapshot: AgentSnapshot) -> None:
        if snapshot.home_position is None:
            snapshot.home_position = snapshot.position
        ctx = self._get_employment_context(snapshot.agent_id)
        ctx.update(self._employment_context_defaults())
        self._employment_state[snapshot.agent_id] = ctx
        self.embedding_allocator.allocate(snapshot.agent_id, self.tick)

    def _console_spawn_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = {key: value for key, value in zip(["agent_id", "position"], envelope.args)}
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "spawn payload must be a mapping")
        agent_id = payload.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            raise ConsoleCommandError("invalid_args", "spawn requires agent_id")
        if agent_id in self.agents:
            raise ConsoleCommandError(
                "conflict", "agent already exists", details={"agent_id": agent_id}
            )
        position = payload.get("position")
        if not isinstance(position, (list, tuple)) or len(position) != 2:
            raise ConsoleCommandError("invalid_args", "position must be [x, y]")
        try:
            x, y = int(position[0]), int(position[1])
        except (TypeError, ValueError):
            raise ConsoleCommandError("invalid_args", "position must be integers")
        if not self._is_position_walkable((x, y)):
            raise ConsoleCommandError(
                "invalid_args",
                "position not walkable",
                details={"position": [x, y]},
            )
        home_payload = payload.get("home_position")
        if home_payload is None:
            home_tuple = (x, y)
        else:
            if not isinstance(home_payload, (list, tuple)) or len(home_payload) != 2:
                raise ConsoleCommandError(
                    "invalid_args", "home_position must be [x, y]"
                )
            try:
                hx, hy = int(home_payload[0]), int(home_payload[1])
            except (TypeError, ValueError):
                raise ConsoleCommandError(
                    "invalid_args", "home_position must be integers"
                )
            home_tuple = (hx, hy)
            if home_tuple != (x, y) and not self._is_position_walkable(home_tuple):
                raise ConsoleCommandError(
                    "invalid_args",
                    "home_position not walkable",
                    details={"home_position": [hx, hy]},
                )
        needs = payload.get("needs") or {}
        if not isinstance(needs, Mapping):
            raise ConsoleCommandError("invalid_args", "needs must be a mapping")
        hunger = float(needs.get("hunger", 0.5))
        hygiene = float(needs.get("hygiene", 0.5))
        energy = float(needs.get("energy", 0.5))
        wallet = float(payload.get("wallet", 0.0))
        snapshot = AgentSnapshot(
            agent_id=agent_id,
            position=(x, y),
            needs={"hunger": hunger, "hygiene": hygiene, "energy": energy},
            wallet=wallet,
            home_position=home_tuple,
        )
        self.agents[agent_id] = snapshot
        job_override = payload.get("job_id")
        if isinstance(job_override, str):
            snapshot.job_id = job_override
        self._assign_job_if_missing(snapshot)
        self._sync_agent_spawn(snapshot)
        result_payload = {
            "agent_id": agent_id,
            "position": [x, y],
            "job_id": snapshot.job_id,
            "home_position": list(home_tuple),
        }
        return ConsoleCommandResult.ok(envelope, result_payload, tick=self.tick)

    def _console_teleport_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = {key: value for key, value in zip(["agent_id", "position"], envelope.args)}
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "teleport payload must be a mapping")
        agent_id = payload.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            raise ConsoleCommandError("invalid_args", "teleport requires agent_id")
        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            raise ConsoleCommandError(
                "not_found", "agent not found", details={"agent_id": agent_id}
            )
        position = payload.get("position")
        if not isinstance(position, (list, tuple)) or len(position) != 2:
            raise ConsoleCommandError("invalid_args", "position must be [x, y]")
        try:
            x, y = int(position[0]), int(position[1])
        except (TypeError, ValueError):
            raise ConsoleCommandError("invalid_args", "position must be integers")
        if not self._is_position_walkable((x, y)):
            raise ConsoleCommandError(
                "invalid_args",
                "position not walkable",
                details={"position": [x, y]},
            )
        self._release_queue_membership(snapshot.agent_id)
        snapshot.position = (x, y)
        self._sync_reservation_for_agent(snapshot.agent_id)
        self.request_ctx_reset(agent_id)
        return ConsoleCommandResult.ok(
            envelope, {"agent_id": agent_id, "position": [x, y]}, tick=self.tick
        )

    def _release_queue_membership(self, agent_id: str) -> None:
        self.queue_manager.remove_agent(agent_id, self.tick)
        for object_id, occupant in list(self._active_reservations.items()):
            if occupant == agent_id:
                self._sync_reservation(object_id)

    def _sync_reservation_for_agent(self, agent_id: str) -> None:
        for object_id, occupant in list(self._active_reservations.items()):
            if occupant == agent_id:
                self._sync_reservation(object_id)

    def _is_position_walkable(self, position: tuple[int, int]) -> bool:
        if any(agent.position == position for agent in self.agents.values()):
            return False
        if position in self._objects_by_position:
            return False
        return True

    def kill_agent(self, agent_id: str, *, reason: str | None = None) -> bool:
        snapshot = self.agents.pop(agent_id, None)
        if snapshot is None:
            return False
        self._release_queue_membership(agent_id)
        self.embedding_allocator.release(agent_id, self.tick)
        self._employment_state.pop(agent_id, None)
        self._employment_remove_from_queue(agent_id)
        self._recent_meal_participants = {
            key: value
            for key, value in self._recent_meal_participants.items()
            if agent_id not in value.get("agents", set())
        }
        self._emit_event(
            "agent_killed",
            {
                "agent_id": agent_id,
                "reason": reason,
                "tick": self.tick,
            },
        )
        return True

    def _console_set_need(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = {key: value for key, value in zip(["agent_id", "needs"], envelope.args)}
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "setneed payload must be a mapping")
        agent_id = payload.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            raise ConsoleCommandError("invalid_args", "setneed requires agent_id")
        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            raise ConsoleCommandError(
                "not_found", "agent not found", details={"agent_id": agent_id}
            )
        needs_payload = payload.get("needs")
        if not isinstance(needs_payload, Mapping):
            raise ConsoleCommandError(
                "invalid_args", "needs must be a mapping of need names to values"
            )
        updated: dict[str, float] = {}
        for key, value in needs_payload.items():
            if key not in snapshot.needs:
                raise ConsoleCommandError(
                    "invalid_args",
                    "unknown need",
                    details={"need": key},
                )
            try:
                float_value = float(value)
            except (TypeError, ValueError):
                raise ConsoleCommandError(
                    "invalid_args", "need values must be numeric", details={"need": key}
                )
            clamped = max(0.0, min(1.0, float_value))
            snapshot.needs[key] = clamped
            updated[key] = clamped
        return ConsoleCommandResult.ok(
            envelope,
            {"agent_id": agent_id, "needs": updated},
            tick=self.tick,
        )

    def _console_set_price(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = {key: value for key, value in zip(["key", "value"], envelope.args)}
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "price payload must be a mapping")
        key = payload.get("key")
        if not isinstance(key, str) or not key:
            raise ConsoleCommandError("invalid_args", "price requires key")
        if key not in self.config.economy:
            raise ConsoleCommandError("not_found", "unknown economy key", details={"key": key})
        value = payload.get("value")
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise ConsoleCommandError("invalid_args", "value must be numeric", details={"key": key})
        self.config.economy[key] = numeric_value
        if key in {"meal_cost", "cook_energy_cost", "cook_hygiene_cost", "ingredients_cost"}:
            self._update_basket_metrics()
        result_payload = {"key": key, "value": numeric_value}
        return ConsoleCommandResult.ok(envelope, result_payload, tick=self.tick)

    def _console_force_chat(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = {
                key: value for key, value in zip(["speaker", "listener", "quality"], envelope.args)
            }
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "force_chat payload must be a mapping")
        speaker = payload.get("speaker")
        listener = payload.get("listener")
        if not isinstance(speaker, str) or not isinstance(listener, str):
            raise ConsoleCommandError("invalid_args", "force_chat requires speaker and listener")
        if speaker == listener:
            raise ConsoleCommandError("invalid_args", "speaker and listener must differ")
        if speaker not in self.agents:
            raise ConsoleCommandError(
                "not_found", "speaker not found", details={"agent_id": speaker}
            )
        if listener not in self.agents:
            raise ConsoleCommandError(
                "not_found", "listener not found", details={"agent_id": listener}
            )
        quality = payload.get("quality", 1.0)
        try:
            quality_value = float(quality)
        except (TypeError, ValueError):
            raise ConsoleCommandError(
                "invalid_args", "quality must be numeric", details={"quality": quality}
            )
        clipped = max(0.0, min(1.0, quality_value))
        self.record_chat_success(speaker, listener, clipped)
        tie_forward = self.relationship_tie(speaker, listener)
        tie_reverse = self.relationship_tie(listener, speaker)
        result_payload = {
            "speaker": speaker,
            "listener": listener,
            "quality": clipped,
            "speaker_tie": tie_forward.as_dict() if tie_forward else {},
            "listener_tie": tie_reverse.as_dict() if tie_reverse else {},
        }
        return ConsoleCommandResult.ok(envelope, result_payload, tick=self.tick)

    def _console_set_relationship(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = {
                key: value
                for key, value in zip(
                    ["agent_a", "agent_b", "trust", "familiarity", "rivalry"],
                    envelope.args,
                )
            }
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "set_rel payload must be a mapping")
        agent_a = payload.get("agent_a")
        agent_b = payload.get("agent_b")
        if not isinstance(agent_a, str) or not isinstance(agent_b, str):
            raise ConsoleCommandError("invalid_args", "set_rel requires agent_a and agent_b")
        if agent_a == agent_b:
            raise ConsoleCommandError("invalid_args", "agent_a and agent_b must differ")
        if agent_a not in self.agents:
            raise ConsoleCommandError(
                "not_found", "agent_a not found", details={"agent_id": agent_a}
            )
        if agent_b not in self.agents:
            raise ConsoleCommandError(
                "not_found", "agent_b not found", details={"agent_id": agent_b}
            )
        target_trust = payload.get("trust")
        target_fam = payload.get("familiarity")
        target_rivalry = payload.get("rivalry")
        if target_trust is None and target_fam is None and target_rivalry is None:
            raise ConsoleCommandError(
                "invalid_args", "set_rel requires at least one of trust/familiarity/rivalry"
            )
        forward = self._get_relationship_ledger(agent_a).tie_for(agent_b)
        reverse = self._get_relationship_ledger(agent_b).tie_for(agent_a)
        current_forward = (
            forward.as_dict() if forward else {"trust": 0.0, "familiarity": 0.0, "rivalry": 0.0}
        )
        current_reverse = (
            reverse.as_dict() if reverse else {"trust": 0.0, "familiarity": 0.0, "rivalry": 0.0}
        )

        def _compute_delta(
            target: object, current: float, *, clamp_low: float, clamp_high: float
        ) -> float:
            if target is None:
                return 0.0
            try:
                coerced = float(target)
            except (TypeError, ValueError):
                raise ConsoleCommandError(
                    "invalid_args",
                    "relationship values must be numeric",
                )
            coerced = max(clamp_low, min(clamp_high, coerced))
            return coerced - current

        delta_trust = _compute_delta(
            target_trust, current_forward["trust"], clamp_low=-1.0, clamp_high=1.0
        )
        delta_fam = _compute_delta(
            target_fam, current_forward["familiarity"], clamp_low=-1.0, clamp_high=1.0
        )
        delta_rivalry = _compute_delta(
            target_rivalry, current_forward["rivalry"], clamp_low=0.0, clamp_high=1.0
        )

        self.update_relationship(
            agent_a,
            agent_b,
            trust=delta_trust,
            familiarity=delta_fam,
            rivalry=delta_rivalry,
            event="console_override",
        )
        # ensure symmetry (update_relationship already symmetric)
        forward_tie = self.relationship_tie(agent_a, agent_b)
        reverse_tie = self.relationship_tie(agent_b, agent_a)
        result_payload = {
            "agent_a": agent_a,
            "agent_b": agent_b,
            "agent_a_tie": forward_tie.as_dict() if forward_tie else {},
            "agent_b_tie": reverse_tie.as_dict() if reverse_tie else {},
        }
        return ConsoleCommandResult.ok(envelope, result_payload, tick=self.tick)

    def register_object(
        self,
        *,
        object_id: str,
        object_type: str,
        position: tuple[int, int] | None = None,
    ) -> None:
        """Register or update an interactive object in the world."""

        existing = self.objects.get(object_id)
        if existing is not None and existing.position is not None:
            self._unindex_object_position(object_id, existing.position)

        obj = InteractiveObject(
            object_id=object_id,
            object_type=object_type,
            position=position,
        )
        if object_type == "fridge":
            obj.stock["meals"] = 5
        if object_type == "stove":
            obj.stock["raw_ingredients"] = 3
        if object_type == "bed":
            obj.stock["sleep_slots"] = obj.stock.get("sleep_slots", 1)
            obj.stock.setdefault("sleep_capacity", obj.stock["sleep_slots"])
        if object_type == "shower":
            obj.stock.setdefault("power_on", 1)
        self.objects[object_id] = obj
        self.store_stock[object_id] = obj.stock
        if obj.position is not None:
            self._index_object_position(object_id, obj.position)

    def _index_object_position(self, object_id: str, position: tuple[int, int]) -> None:
        bucket = self._objects_by_position.setdefault(position, [])
        if object_id not in bucket:
            bucket.append(object_id)

    def _unindex_object_position(self, object_id: str, position: tuple[int, int]) -> None:
        bucket = self._objects_by_position.get(position)
        if not bucket:
            return
        try:
            bucket.remove(object_id)
        except ValueError:
            return
        if not bucket:
            self._objects_by_position.pop(position, None)

    def register_affordance(
        self,
        *,
        affordance_id: str,
        object_type: str,
        duration: int,
        effects: dict[str, float],
        preconditions: Iterable[str] | None = None,
        hooks: Mapping[str, Iterable[str]] | None = None,
    ) -> None:
        """Register an affordance available in the world."""
        raw_preconditions = list(preconditions or [])
        try:
            compiled = compile_preconditions(raw_preconditions)
        except PreconditionSyntaxError as exc:  # pragma: no cover - defensive
            raise RuntimeError(
                f"Failed to compile preconditions for affordance '{affordance_id}': {exc}"
            ) from exc

        self.affordances[affordance_id] = AffordanceSpec(
            affordance_id=affordance_id,
            object_type=object_type,
            duration=duration,
            effects=dict(effects),
            preconditions=raw_preconditions,
            hooks={key: list(values) for key, values in (hooks or {}).items()},
            compiled_preconditions=compiled,
        )

    def apply_actions(self, actions: dict[str, Any]) -> None:
        """Apply agent actions for the current tick."""
        current_tick = self.tick
        for agent_id, action in actions.items():
            snapshot = self.agents.get(agent_id)
            if snapshot is None:
                continue
            if not isinstance(action, dict):
                continue

            kind = action.get("kind")
            object_id = action.get("object")
            action_success = False
            action_duration = int(action.get("duration", 1))

            if kind == "request" and object_id:
                granted = self.queue_manager.request_access(object_id, agent_id, current_tick)
                self._sync_reservation(object_id)
                if not granted and action.get("blocked"):
                    self._handle_blocked(object_id, current_tick)
                action_success = bool(granted)
            elif kind == "move" and action.get("position"):
                target_pos = tuple(action["position"])
                snapshot.position = target_pos
                action_success = True
            elif kind == "start" and object_id:
                affordance_id = action.get("affordance")
                if affordance_id:
                    action_success = self._start_affordance(agent_id, object_id, affordance_id)
            elif kind == "release" and object_id:
                success = bool(action.get("success", True))
                running = self._running_affordances.pop(object_id, None)
                if running is not None and success:
                    self._apply_affordance_effects(running.agent_id, running.effects)
                    spec = self.affordances.get(running.affordance_id)
                    self._dispatch_affordance_hooks(
                        "after",
                        spec.hooks.get("after", ()) if spec else (),
                        agent_id=running.agent_id,
                        object_id=object_id,
                        spec=spec,
                        extra={"effects": dict(running.effects)},
                    )
                    self._emit_event(
                        "affordance_finish",
                        {
                            "agent_id": running.agent_id,
                            "object_id": object_id,
                            "affordance_id": running.affordance_id,
                        },
                    )
                    obj = self.objects.get(object_id)
                    if obj is not None:
                        obj.occupied_by = None
                self.queue_manager.release(object_id, agent_id, current_tick, success=success)
                self._sync_reservation(object_id)
                if not success:
                    spec: AffordanceSpec | None = None
                    if running is not None:
                        spec = self.affordances.get(running.affordance_id)
                        self._dispatch_affordance_hooks(
                            "fail",
                            spec.hooks.get("fail", ()) if spec else (),
                            agent_id=agent_id,
                            object_id=object_id,
                            spec=spec,
                            extra={"reason": action.get("reason")},
                        )
                        self._emit_event(
                            "affordance_fail",
                            {
                                "agent_id": agent_id,
                                "object_id": object_id,
                                "affordance_id": running.affordance_id,
                            },
                        )
                    self._running_affordances.pop(object_id, None)
                action_success = success
            elif kind == "blocked" and object_id:
                self._handle_blocked(object_id, current_tick)
                action_success = False
            # TODO(@townlet): Update agent snapshot based on outcomes.

            if kind:
                snapshot.last_action_id = str(kind)
                snapshot.last_action_success = action_success
                snapshot.last_action_duration = action_duration

    def resolve_affordances(self, current_tick: int) -> None:
        """Resolve queued affordances and hooks."""
        # Tick the queue manager so cooldowns expire and fairness checks apply.
        self.queue_manager.on_tick(current_tick)
        # Automatically monitor stalled queues and trigger ghost steps when required.
        for object_id, occupant in list(self._active_reservations.items()):
            queue = self.queue_manager.queue_snapshot(object_id)
            if not queue:
                continue
            if self.queue_manager.record_blocked_attempt(object_id):
                waiting = self.queue_manager.queue_snapshot(object_id)
                rival = waiting[0] if waiting else None
                self.queue_manager.release(object_id, occupant, current_tick, success=False)
                self.queue_manager.requeue_to_tail(object_id, occupant, current_tick)
                if rival is not None:
                    self._record_queue_conflict(
                        object_id=object_id,
                        actor=occupant,
                        rival=rival,
                        reason="ghost_step",
                        queue_length=len(waiting),
                        intensity=None,
                    )
                self._running_affordances.pop(object_id, None)
                self._sync_reservation(object_id)
        # TODO(@townlet): Integrate with affordance registry and hook dispatch.

        for object_id, running in list(self._running_affordances.items()):
            running.duration_remaining -= 1
            if running.duration_remaining <= 0:
                self._apply_affordance_effects(running.agent_id, running.effects)
                self._running_affordances.pop(object_id, None)
                waiting = self.queue_manager.queue_snapshot(object_id)
                spec = self.affordances.get(running.affordance_id)
                self._dispatch_affordance_hooks(
                    "after",
                    spec.hooks.get("after", ()) if spec else (),
                    agent_id=running.agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={"effects": dict(running.effects)},
                )
                self.queue_manager.release(object_id, running.agent_id, current_tick, success=True)
                self._sync_reservation(object_id)
                if waiting:
                    next_agent = waiting[0]
                    self._record_queue_conflict(
                        object_id=object_id,
                        actor=running.agent_id,
                        rival=next_agent,
                        reason="handover",
                        queue_length=len(waiting),
                        intensity=0.5,
                    )
                self._emit_event(
                    "affordance_finish",
                    {
                        "agent_id": running.agent_id,
                        "object_id": object_id,
                        "affordance_id": running.affordance_id,
                    },
                )

        self._apply_need_decay()

    def request_ctx_reset(self, agent_id: str) -> None:
        """Mark an agent so the next observation toggles ctx_reset_flag."""
        if agent_id in self.agents:
            self._ctx_reset_requests.add(agent_id)

    def consume_ctx_reset_requests(self) -> set[str]:
        """Return and clear pending ctx-reset requests."""
        pending = set(self._ctx_reset_requests)
        self._ctx_reset_requests.clear()
        return pending

    def snapshot(self) -> dict[str, AgentSnapshot]:
        """Return a shallow copy of the agent dictionary for observers."""
        return {agent_id: copy.deepcopy(snapshot) for agent_id, snapshot in self.agents.items()}

    def local_view(
        self,
        agent_id: str,
        radius: int,
        *,
        include_agents: bool = True,
        include_objects: bool = True,
    ) -> dict[str, Any]:
        """Return local neighborhood information for observation builders."""

        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            return {
                "center": None,
                "radius": radius,
                "tiles": [],
                "agents": [],
                "objects": [],
            }

        cx, cy = snapshot.position
        agent_lookup: dict[tuple[int, int], list[str]] = {}
        if include_agents:
            for other in self.agents.values():
                position = other.position
                agent_lookup.setdefault(position, []).append(other.agent_id)

        object_lookup: dict[tuple[int, int], list[str]] = {}
        if include_objects:
            for position, object_ids in self._objects_by_position.items():
                filtered = [obj_id for obj_id in object_ids if obj_id in self.objects]
                if filtered:
                    object_lookup[position] = filtered

        tiles: list[list[dict[str, Any]]] = []
        seen_agents: dict[str, dict[str, Any]] = {}
        seen_objects: dict[str, dict[str, Any]] = {}

        for dy in range(-radius, radius + 1):
            row: list[dict[str, Any]] = []
            for dx in range(-radius, radius + 1):
                x = cx + dx
                y = cy + dy
                position = (x, y)
                agent_ids = agent_lookup.get(position, [])
                object_ids = object_lookup.get(position, [])
                if include_agents:
                    for agent_id_at_tile in agent_ids:
                        if agent_id_at_tile == agent_id:
                            continue
                        other = self.agents.get(agent_id_at_tile)
                        if other is not None:
                            seen_agents.setdefault(
                                agent_id_at_tile,
                                {
                                    "agent_id": agent_id_at_tile,
                                    "position": other.position,
                                    "on_shift": other.on_shift,
                                },
                            )
                if include_objects:
                    for object_id in object_ids:
                        obj = self.objects.get(object_id)
                        if obj is None:
                            continue
                        seen_objects.setdefault(
                            object_id,
                            {
                                "object_id": object_id,
                                "object_type": obj.object_type,
                                "position": obj.position,
                                "occupied_by": obj.occupied_by,
                            },
                        )
                reservation_active = False
                if object_ids:
                    reservation_active = any(
                        self._active_reservations.get(object_id) is not None
                        for object_id in object_ids
                    )
                row.append(
                    {
                        "position": position,
                        "self": position == (cx, cy),
                        "agent_ids": list(agent_ids),
                        "object_ids": list(object_ids),
                        "reservation_active": reservation_active,
                    }
                )
            tiles.append(row)

        return {
            "center": (cx, cy),
            "radius": radius,
            "tiles": tiles,
            "agents": list(seen_agents.values()),
            "objects": list(seen_objects.values()),
        }

    def agent_context(self, agent_id: str) -> dict[str, object]:
        """Return scalar context fields for the requested agent."""

        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            return {}
        return {
            "needs": dict(snapshot.needs),
            "wallet": snapshot.wallet,
            "lateness_counter": snapshot.lateness_counter,
            "on_shift": snapshot.on_shift,
            "attendance_ratio": snapshot.attendance_ratio,
            "wages_withheld": snapshot.wages_withheld,
            "shift_state": snapshot.shift_state,
            "last_action_id": snapshot.last_action_id,
            "last_action_success": snapshot.last_action_success,
            "last_action_duration": snapshot.last_action_duration,
            "wages_paid": self._employment_context_wages(snapshot.agent_id),
            "punctuality_bonus": self._employment_context_punctuality(snapshot.agent_id),
        }

    @property
    def active_reservations(self) -> dict[str, str]:
        """Expose a copy of active reservations for diagnostics/tests."""
        return dict(self._active_reservations)

    def drain_events(self) -> list[dict[str, Any]]:
        """Return all pending events accumulated up to the current tick."""
        events: list[dict[str, Any]] = []
        for _, batch in sorted(self._pending_events.items()):
            events.extend(batch)
        self._pending_events.clear()
        return events

    def _record_queue_conflict(
        self,
        *,
        object_id: str,
        actor: str,
        rival: str,
        reason: str,
        queue_length: int,
        intensity: float | None = None,
    ) -> None:
        if actor == rival:
            return
        payload = {
            "object_id": object_id,
            "actor": actor,
            "rival": rival,
            "reason": reason,
            "queue_length": queue_length,
        }
        if reason == "handover":
            self.update_relationship(
                actor,
                rival,
                trust=0.05,
                familiarity=0.05,
                rivalry=-0.05,
                event="queue_polite",
            )
            self._emit_event("queue_interaction", {**payload, "variant": "handover"})
            return

        params = self.config.conflict.rivalry
        base_intensity = intensity
        if base_intensity is None:
            boost = params.ghost_step_boost if reason == "ghost_step" else params.handover_boost
            base_intensity = boost + params.queue_length_boost * max(queue_length - 1, 0)
        clamped_intensity = min(5.0, max(0.1, base_intensity))
        self.register_rivalry_conflict(actor, rival, intensity=clamped_intensity, reason=reason)
        self.update_relationship(
            actor,
            rival,
            rivalry=0.05 * clamped_intensity,
            event="conflict",
        )
        self._emit_event(
            "queue_conflict",
            {
                **payload,
                "intensity": clamped_intensity,
            },
        )

    def register_rivalry_conflict(
        self,
        agent_a: str,
        agent_b: str,
        *,
        intensity: float = 1.0,
        reason: str = "conflict",
    ) -> None:
        """Record a rivalry-inducing conflict between two agents.

        Both ledgers are updated symmetrically so downstream consumers can
        inspect rivalry magnitudes without having to normalise directionality.
        """
        if agent_a == agent_b:
            return
        ledger_a = self._get_rivalry_ledger(agent_a)
        ledger_b = self._get_rivalry_ledger(agent_b)
        ledger_a.apply_conflict(agent_b, intensity=intensity)
        ledger_b.apply_conflict(agent_a, intensity=intensity)
        self.update_relationship(
            agent_a,
            agent_b,
            rivalry=0.1 * intensity,
            event="conflict",
        )
        self._record_rivalry_event(
            agent_a=agent_a, agent_b=agent_b, intensity=intensity, reason=reason
        )

    def rivalry_snapshot(self) -> dict[str, dict[str, float]]:
        """Expose rivalry ledgers for telemetry/diagnostics."""
        snapshot: dict[str, dict[str, float]] = {}
        for agent_id, ledger in self._rivalry_ledgers.items():
            data = ledger.snapshot()
            if data:
                snapshot[agent_id] = data
        return snapshot

    def relationships_snapshot(self) -> dict[str, dict[str, dict[str, float]]]:
        snapshot: dict[str, dict[str, dict[str, float]]] = {}
        for agent_id, ledger in self._relationship_ledgers.items():
            data = ledger.snapshot()
            if data:
                snapshot[agent_id] = data
        return snapshot

    def relationship_tie(self, agent_id: str, other_id: str) -> RelationshipTie | None:
        """Return the current relationship tie between two agents, if any."""

        ledger = self._relationship_ledgers.get(agent_id)
        if ledger is None:
            return None
        return ledger.tie_for(other_id)

    def consume_chat_events(self) -> list[dict[str, Any]]:
        """Return chat events staged for reward calculations and clear the buffer."""

        events = list(self._chat_events)
        self._chat_events.clear()
        return events

    def rivalry_value(self, agent_id: str, other_id: str) -> float:
        """Return the rivalry score between two agents, if present."""
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return 0.0
        return ledger.score_for(other_id)

    def rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return False
        return ledger.should_avoid(other_id)

    def rivalry_top(self, agent_id: str, limit: int) -> list[tuple[str, float]]:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return []
        return ledger.top_rivals(limit)

    def consume_rivalry_events(self) -> list[dict[str, Any]]:
        """Return rivalry events recorded since the last call."""

        if not self._rivalry_events:
            return []
        events = list(self._rivalry_events)
        self._rivalry_events.clear()
        return events

    def _record_rivalry_event(
        self, *, agent_a: str, agent_b: str, intensity: float, reason: str
    ) -> None:
        self._rivalry_events.append(
            {
                "tick": int(self.tick),
                "agent_a": agent_a,
                "agent_b": agent_b,
                "intensity": float(intensity),
                "reason": reason,
            }
        )

    def _get_rivalry_ledger(self, agent_id: str) -> RivalryLedger:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            ledger = RivalryLedger(
                owner_id=agent_id,
                params=self._rivalry_parameters(),
                eviction_hook=self._record_relationship_eviction,
            )
            self._rivalry_ledgers[agent_id] = ledger
        else:
            ledger.eviction_hook = self._record_relationship_eviction
        return ledger

    def _get_relationship_ledger(self, agent_id: str) -> RelationshipLedger:
        ledger = self._relationship_ledgers.get(agent_id)
        if ledger is None:
            ledger = RelationshipLedger(
                owner_id=agent_id,
                params=self._relationship_parameters(),
                eviction_hook=self._record_relationship_eviction,
            )
            self._relationship_ledgers[agent_id] = ledger
        else:
            ledger.set_eviction_hook(
                owner_id=agent_id,
                hook=self._record_relationship_eviction,
            )
        return ledger

    def _relationship_parameters(self) -> RelationshipParameters:
        return RelationshipParameters(max_edges=self.config.conflict.rivalry.max_edges)

    def _personality_for(self, agent_id: str) -> Personality:
        snapshot = self.agents.get(agent_id)
        if snapshot is None or snapshot.personality is None:
            return _default_personality()
        return snapshot.personality

    def _apply_relationship_delta(
        self,
        owner_id: str,
        other_id: str,
        *,
        delta: RelationshipDelta,
        event: RelationshipEvent,
    ) -> None:
        ledger = self._get_relationship_ledger(owner_id)
        adjusted = apply_personality_modifiers(
            delta=delta,
            personality=self._personality_for(owner_id),
            event=event,
            enabled=bool(self.config.features.relationship_modifiers),
        )
        ledger.apply_delta(
            other_id,
            trust=adjusted.trust,
            familiarity=adjusted.familiarity,
            rivalry=adjusted.rivalry,
        )

    def _rivalry_parameters(self) -> RivalryParameters:
        cfg = self.config.conflict.rivalry
        return RivalryParameters(
            increment_per_conflict=cfg.increment_per_conflict,
            decay_per_tick=cfg.decay_per_tick,
            min_value=cfg.min_value,
            max_value=cfg.max_value,
            avoid_threshold=cfg.avoid_threshold,
            eviction_threshold=cfg.eviction_threshold,
            max_edges=cfg.max_edges,
        )

    def _decay_rivalry_ledgers(self) -> None:
        if not self._rivalry_ledgers:
            return
        empty_agents: list[str] = []
        for agent_id, ledger in self._rivalry_ledgers.items():
            ledger.decay(ticks=1)
            if not ledger.snapshot():
                empty_agents.append(agent_id)
        for agent_id in empty_agents:
            self._rivalry_ledgers.pop(agent_id, None)
        self._decay_relationship_ledgers()

    def _decay_relationship_ledgers(self) -> None:
        if not self._relationship_ledgers:
            return
        empty_agents: list[str] = []
        for agent_id, ledger in self._relationship_ledgers.items():
            ledger.decay()
            if not ledger.snapshot():
                empty_agents.append(agent_id)
        for agent_id in empty_agents:
            self._relationship_ledgers.pop(agent_id, None)

    def _record_relationship_eviction(self, owner_id: str, other_id: str, reason: str) -> None:
        self._relationship_churn.record_eviction(
            tick=self.tick,
            owner_id=owner_id,
            evicted_id=other_id,
            reason=reason,
        )

    def relationship_metrics_snapshot(self) -> dict[str, object]:
        return self._relationship_churn.latest_payload()

    def load_relationship_snapshot(
        self,
        snapshot: dict[str, dict[str, dict[str, float]]],
    ) -> None:
        """Restore relationship ledgers from persisted snapshot data."""

        self._relationship_ledgers.clear()
        for owner_id, edges in snapshot.items():
            ledger = RelationshipLedger(
                owner_id=owner_id,
                params=self._relationship_parameters(),
            )
            ledger.inject(edges)
            ledger.set_eviction_hook(
                owner_id=owner_id,
                hook=self._record_relationship_eviction,
            )
            self._relationship_ledgers[owner_id] = ledger

    def update_relationship(
        self,
        agent_a: str,
        agent_b: str,
        *,
        trust: float = 0.0,
        familiarity: float = 0.0,
        rivalry: float = 0.0,
        event: RelationshipEvent = "generic",
    ) -> None:
        if agent_a == agent_b:
            return
        delta = RelationshipDelta(trust=trust, familiarity=familiarity, rivalry=rivalry)
        self._apply_relationship_delta(agent_a, agent_b, delta=delta, event=event)
        self._apply_relationship_delta(agent_b, agent_a, delta=delta, event=event)

    def record_chat_success(self, speaker: str, listener: str, quality: float) -> None:
        clipped_quality = max(0.0, min(1.0, quality))
        self.update_relationship(
            speaker,
            listener,
            trust=0.05 * clipped_quality,
            familiarity=0.10 * clipped_quality,
            event="chat_success",
        )
        self._chat_events.append(
            {
                "event": "chat_success",
                "speaker": speaker,
                "listener": listener,
                "quality": clipped_quality,
                "tick": self.tick,
            }
        )
        self._emit_event(
            "chat_success",
            {
                "speaker": speaker,
                "listener": listener,
                "quality": clipped_quality,
            },
        )

    def record_chat_failure(self, speaker: str, listener: str) -> None:
        self.update_relationship(
            speaker,
            listener,
            trust=0.0,
            familiarity=-0.05,
            rivalry=0.05,
            event="chat_failure",
        )
        self._chat_events.append(
            {
                "event": "chat_failure",
                "speaker": speaker,
                "listener": listener,
                "tick": self.tick,
            }
        )
        self._emit_event(
            "chat_failure",
            {
                "speaker": speaker,
                "listener": listener,
            },
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _sync_reservation(self, object_id: str) -> None:
        active = self.queue_manager.active_agent(object_id)
        obj = self.objects.get(object_id)
        if active is None:
            self._active_reservations.pop(object_id, None)
            if obj is not None:
                obj.occupied_by = None
        else:
            self._active_reservations[object_id] = active
            if obj is not None:
                obj.occupied_by = active

    def _handle_blocked(self, object_id: str, tick: int) -> None:
        if self.queue_manager.record_blocked_attempt(object_id):
            occupant = self.queue_manager.active_agent(object_id)
            running = self._running_affordances.pop(object_id, None)
            spec: AffordanceSpec | None = None
            if running is not None:
                spec = self.affordances.get(running.affordance_id)
                self._dispatch_affordance_hooks(
                    "fail",
                    spec.hooks.get("fail", ()) if spec else (),
                    agent_id=running.agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={"reason": "ghost_step"},
                )
            if occupant is not None:
                self.queue_manager.release(object_id, occupant, tick, success=False)
            self._sync_reservation(object_id)

    def _start_affordance(self, agent_id: str, object_id: str, affordance_id: str) -> bool:
        if self.queue_manager.active_agent(object_id) != agent_id:
            return False
        if object_id in self._running_affordances:
            return False
        obj = self.objects.get(object_id)
        spec = self.affordances.get(affordance_id)
        if obj is None or spec is None:
            return False
        if spec.object_type != obj.object_type:
            return False

        if spec.compiled_preconditions:
            context = self._build_precondition_context(
                agent_id=agent_id,
                object_id=object_id,
                spec=spec,
            )
            ok, failed = evaluate_preconditions(
                spec.compiled_preconditions,
                context,
            )
            if not ok:
                context_snapshot = self._snapshot_precondition_context(context)
                payload = {
                    "agent_id": agent_id,
                    "object_id": object_id,
                    "affordance_id": affordance_id,
                    "condition": failed.source if failed else None,
                    "context": context_snapshot,
                }
                logger.debug(
                    "Precondition failed for affordance '%s' (agent=%s, object=%s, condition=%s)",
                    affordance_id,
                    agent_id,
                    object_id,
                    payload["condition"],
                )
                self._dispatch_affordance_hooks(
                    "fail",
                    spec.hooks.get("fail", ()),
                    agent_id=agent_id,
                    object_id=object_id,
                    spec=spec,
                    extra={
                        "reason": "precondition_failed",
                        "condition": payload["condition"],
                        "context": context_snapshot,
                    },
                )
                self._emit_event("affordance_precondition_fail", payload)
                self._emit_event(
                    "affordance_fail",
                    {
                        **payload,
                        "reason": "precondition_failed",
                    },
                )
                if self.queue_manager.active_agent(object_id) == agent_id:
                    self.queue_manager.release(object_id, agent_id, self.tick, success=False)
                    self._sync_reservation(object_id)
                return False

        self._running_affordances[object_id] = RunningAffordance(
            agent_id=agent_id,
            affordance_id=affordance_id,
            duration_remaining=max(spec.duration, 1),
            effects=spec.effects,
        )
        obj.occupied_by = agent_id
        continue_start = self._dispatch_affordance_hooks(
            "before",
            spec.hooks.get("before", ()),
            agent_id=agent_id,
            object_id=object_id,
            spec=spec,
        )
        if not continue_start:
            self._running_affordances.pop(object_id, None)
            if obj.occupied_by == agent_id:
                obj.occupied_by = None
            if self.queue_manager.active_agent(object_id) == agent_id:
                self.queue_manager.release(object_id, agent_id, self.tick, success=False)
                self._sync_reservation(object_id)
            return False
        self._emit_event(
            "affordance_start",
            {
                "agent_id": agent_id,
                "object_id": object_id,
                "affordance_id": affordance_id,
                "duration": spec.duration,
            },
        )
        return True

    def _apply_affordance_effects(self, agent_id: str, effects: dict[str, float]) -> None:
        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            return
        for key, delta in effects.items():
            if key in snapshot.needs:
                new_value = snapshot.needs[key] + delta
                snapshot.needs[key] = max(0.0, min(1.0, new_value))
            elif key == "money":
                snapshot.wallet += delta

    def _emit_event(self, event: str, payload: dict[str, Any]) -> None:
        events = self._pending_events.setdefault(self.tick, [])
        events.append({"event": event, "tick": self.tick, **payload})

    def _load_affordance_definitions(self) -> None:
        manifest_path = Path(self.config.affordances.affordances_file).expanduser()
        try:
            manifest = load_affordance_manifest(manifest_path)
        except FileNotFoundError as error:
            raise RuntimeError(f"Affordance manifest not found at {manifest_path}.") from error
        except AffordanceManifestError as error:
            raise RuntimeError(
                f"Failed to load affordance manifest {manifest_path}: {error}"
            ) from error

        self.objects.clear()
        self.affordances.clear()
        self.store_stock.clear()

        for entry in manifest.objects:
            self.register_object(
                object_id=entry.object_id,
                object_type=entry.object_type,
                position=getattr(entry, "position", None),
            )
            if entry.stock:
                obj = self.objects.get(entry.object_id)
                if obj is not None:
                    obj.stock.update(entry.stock)
                    self.store_stock[entry.object_id] = obj.stock

        for entry in manifest.affordances:
            self.register_affordance(
                affordance_id=entry.affordance_id,
                object_type=entry.object_type,
                duration=entry.duration,
                effects=entry.effects,
                preconditions=entry.preconditions,
                hooks=entry.hooks,
            )

        self._affordance_manifest_info = {
            "path": str(manifest.path),
            "checksum": manifest.checksum,
            "object_count": manifest.object_count,
            "affordance_count": manifest.affordance_count,
        }
        self._assign_jobs_to_agents()

    def affordance_manifest_metadata(self) -> dict[str, object]:
        """Expose manifest metadata (path, checksum, counts) for telemetry."""

        return dict(self._affordance_manifest_info)

    def find_nearest_object_of_type(
        self, object_type: str, origin: tuple[int, int]
    ) -> tuple[int, int] | None:
        targets = [
            obj.position
            for obj in self.objects.values()
            if obj.object_type == object_type and obj.position is not None
        ]
        if not targets:
            return None
        ox, oy = origin
        closest = min(targets, key=lambda pos: (pos[0] - ox) ** 2 + (pos[1] - oy) ** 2)
        return closest

    def _apply_need_decay(self) -> None:
        decay_rates = self.config.rewards.decay_rates
        for snapshot in self.agents.values():
            for need, decay in decay_rates.items():
                if need in snapshot.needs:
                    snapshot.needs[need] = max(0.0, snapshot.needs[need] - decay)
        self._decay_rivalry_ledgers()
        self._apply_job_state()
        self._update_basket_metrics()

    def apply_nightly_reset(self) -> list[str]:
        """Return agents home, refresh needs, and reset employment flags."""

        if not self.agents:
            return []
        reset_agents: list[str] = []
        for snapshot in self.agents.values():
            previous_position = snapshot.position
            home = snapshot.home_position or snapshot.position
            if home is None:
                home = snapshot.position
                snapshot.home_position = home

            target = home
            if target is not None and target != snapshot.position:
                occupied = any(
                    other.agent_id != snapshot.agent_id and other.position == target
                    for other in self.agents.values()
                )
                blocked = target in self._objects_by_position
                if not occupied and not blocked:
                    self._release_queue_membership(snapshot.agent_id)
                    snapshot.position = target
                    self._sync_reservation_for_agent(snapshot.agent_id)

            for need_name, value in snapshot.needs.items():
                snapshot.needs[need_name] = max(0.5, min(1.0, float(value)))

            snapshot.exit_pending = False
            snapshot.on_shift = False
            snapshot.shift_state = "pre_shift"
            snapshot.late_ticks_today = 0
            ctx = self._get_employment_context(snapshot.agent_id)
            ctx.update(
                {
                    "state": "pre_shift",
                    "late_penalty_applied": False,
                    "absence_penalty_applied": False,
                    "late_event_emitted": False,
                    "absence_event_emitted": False,
                    "departure_event_emitted": False,
                    "late_help_event_emitted": False,
                    "took_shift_event_emitted": False,
                    "shift_started_tick": None,
                    "shift_end_tick": None,
                    "last_present_tick": None,
                    "late_ticks": 0,
                    "shift_outcome_recorded": False,
                    "ever_on_time": False,
                    "late_counter_recorded": False,
                }
            )

            reset_agents.append(snapshot.agent_id)
            self._emit_event(
                "agent_nightly_reset",
                {
                    "agent_id": snapshot.agent_id,
                    "moved": snapshot.position != previous_position,
                    "home_position": list(snapshot.home_position)
                    if snapshot.home_position
                    else None,
                },
            )

        return reset_agents

    def _assign_jobs_to_agents(self) -> None:
        if not self._job_keys:
            return
        for index, snapshot in enumerate(self.agents.values()):
            if snapshot.job_id is None or snapshot.job_id not in self.config.jobs:
                snapshot.job_id = self._job_keys[index % len(self._job_keys)]
            snapshot.inventory.setdefault("meals_cooked", 0)
            snapshot.inventory.setdefault("meals_consumed", 0)
            snapshot.inventory.setdefault("wages_earned", 0)

    def _apply_job_state(self) -> None:
        if self.config.employment.enforce_job_loop:
            self._apply_job_state_enforced()
        else:
            self._apply_job_state_legacy()

    def _apply_job_state_legacy(self) -> None:
        jobs = self.config.jobs
        default_job_id = self._job_keys[0] if self._job_keys else None
        for snapshot in self.agents.values():
            job_id = snapshot.job_id
            if job_id is None or job_id not in jobs:
                if default_job_id is None:
                    snapshot.on_shift = False
                    continue
                job_id = default_job_id
                snapshot.job_id = job_id
            spec = jobs[job_id]
            start = spec.start_tick
            end = spec.end_tick or spec.start_tick
            wage_rate = spec.wage_rate or self.config.economy.get("wage_income", 0.0)
            lateness_penalty = spec.lateness_penalty
            location = spec.location
            required_position = tuple(location) if location else (0, 0)

            if start <= self.tick <= end:
                snapshot.on_shift = True
                if self.tick == start and snapshot.position != required_position:
                    snapshot.lateness_counter += 1
                    if snapshot.last_late_tick != self.tick:
                        snapshot.wallet = max(0.0, snapshot.wallet - lateness_penalty)
                        snapshot.last_late_tick = self.tick
                        self._emit_event(
                            "job_late",
                            {
                                "agent_id": snapshot.agent_id,
                                "job_id": job_id,
                                "tick": self.tick,
                            },
                        )
                if location and tuple(location) != snapshot.position:
                    snapshot.on_shift = False
                else:
                    snapshot.wallet += wage_rate
                    snapshot.inventory["wages_earned"] = (
                        snapshot.inventory.get("wages_earned", 0) + 1
                    )
            else:
                snapshot.on_shift = False

    def _apply_job_state_enforced(self) -> None:
        jobs = self.config.jobs
        default_job_id = self._job_keys[0] if self._job_keys else None
        employment_cfg = self.config.employment
        arrival_buffer = self.config.behavior.job_arrival_buffer
        ticks_per_day = max(1, employment_cfg.exit_review_window)
        seven_day_window = ticks_per_day * 7

        for snapshot in self.agents.values():
            ctx = self._get_employment_context(snapshot.agent_id)
            # Reset daily counters when day changes.
            current_day = self.tick // ticks_per_day
            if ctx["current_day"] != current_day:
                ctx["current_day"] = current_day
                ctx["late_ticks"] = 0
                ctx["wages_paid"] = 0.0
                snapshot.late_ticks_today = 0

            job_id = snapshot.job_id
            if job_id is None or job_id not in jobs:
                if default_job_id is None:
                    self._employment_idle_state(snapshot, ctx)
                    continue
                job_id = default_job_id
                snapshot.job_id = job_id

            spec = jobs[job_id]
            start = spec.start_tick
            end = spec.end_tick or spec.start_tick
            if end < start:
                end = start
            wage_rate = spec.wage_rate or self.config.economy.get("wage_income", 0.0)
            lateness_penalty = spec.lateness_penalty
            required_position = tuple(spec.location) if spec.location else None
            at_required_location = (
                required_position is None or snapshot.position == required_position
            )

            # Maintenance: drop stale absence events beyond rolling window.
            while ctx["absence_events"] and (
                self.tick - ctx["absence_events"][0] > seven_day_window
            ):
                ctx["absence_events"].popleft()
            snapshot.absent_shifts_7d = len(ctx["absence_events"])

            if self.tick < start - arrival_buffer:
                self._employment_idle_state(snapshot, ctx)
                continue

            if start - arrival_buffer <= self.tick < start:
                self._employment_prepare_state(snapshot, ctx)
                continue

            if start <= self.tick <= end:
                self._employment_begin_shift(ctx, start, end)
                state = self._employment_determine_state(
                    ctx=ctx,
                    tick=self.tick,
                    start=start,
                    at_required_location=at_required_location,
                    employment_cfg=employment_cfg,
                )
                self._employment_apply_state_effects(
                    snapshot=snapshot,
                    ctx=ctx,
                    state=state,
                    at_required_location=at_required_location,
                    wage_rate=wage_rate,
                    lateness_penalty=lateness_penalty,
                    employment_cfg=employment_cfg,
                )
                continue

            # Post-shift window.
            self._employment_finalize_shift(
                snapshot=snapshot,
                ctx=ctx,
                employment_cfg=employment_cfg,
                job_id=job_id,
            )

    # ------------------------------------------------------------------
    # Employment helpers
    # ------------------------------------------------------------------
    def _employment_context_defaults(self) -> dict[str, Any]:
        window = max(1, self.config.employment.attendance_window)
        return {
            "state": "pre_shift",
            "late_penalty_applied": False,
            "absence_penalty_applied": False,
            "late_event_emitted": False,
            "absence_event_emitted": False,
            "departure_event_emitted": False,
            "late_help_event_emitted": False,
            "took_shift_event_emitted": False,
            "shift_started_tick": None,
            "shift_end_tick": None,
            "last_present_tick": None,
            "ever_on_time": False,
            "scheduled_ticks": 0,
            "on_time_ticks": 0,
            "late_ticks": 0,
            "wages_paid": 0.0,
            "attendance_samples": deque(maxlen=window),
            "absence_events": deque(),
            "shift_outcome_recorded": False,
            "current_day": -1,
            "late_counter_recorded": False,
        }

    def _get_employment_context(self, agent_id: str) -> dict[str, Any]:
        ctx = self._employment_state.get(agent_id)
        if ctx is None or ctx.get("attendance_samples") is None:
            ctx = self._employment_context_defaults()
            self._employment_state[agent_id] = ctx
        # Resize deque if window changed via config reload.
        window = max(1, self.config.employment.attendance_window)
        samples: deque[float] = ctx["attendance_samples"]
        if samples.maxlen != window:
            new_samples: deque[float] = deque(samples, maxlen=window)
            ctx["attendance_samples"] = new_samples
        return ctx

    def _employment_context_wages(self, agent_id: str) -> float:
        ctx = self._employment_state.get(agent_id)
        if not ctx:
            return 0.0
        return float(ctx.get("wages_paid", 0.0))

    def _employment_context_punctuality(self, agent_id: str) -> float:
        ctx = self._employment_state.get(agent_id)
        if not ctx:
            return 0.0
        scheduled = max(1, int(ctx.get("scheduled_ticks", 0)))
        on_time = float(ctx.get("on_time_ticks", 0))
        value = on_time / scheduled
        return max(0.0, min(1.0, value))

    def _employment_idle_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None:
        if ctx["state"] != "pre_shift":
            ctx["state"] = "pre_shift"
            ctx["late_penalty_applied"] = False
            ctx["absence_penalty_applied"] = False
            ctx["late_event_emitted"] = False
            ctx["absence_event_emitted"] = False
            ctx["departure_event_emitted"] = False
            ctx["late_help_event_emitted"] = False
            ctx["took_shift_event_emitted"] = False
            ctx["shift_started_tick"] = None
            ctx["shift_end_tick"] = None
            ctx["last_present_tick"] = None
            ctx["ever_on_time"] = False
            ctx["scheduled_ticks"] = 0
            ctx["on_time_ticks"] = 0
            ctx["shift_outcome_recorded"] = False
        snapshot.shift_state = "pre_shift"
        snapshot.on_shift = False

    def _employment_prepare_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None:
        ctx["state"] = "await_start"
        snapshot.shift_state = "await_start"
        snapshot.on_shift = False

    def _employment_begin_shift(self, ctx: dict[str, Any], start: int, end: int) -> None:
        if ctx["shift_started_tick"] != start:
            ctx["shift_started_tick"] = start
            ctx["shift_end_tick"] = end
            ctx["scheduled_ticks"] = max(1, end - start + 1)
            ctx["on_time_ticks"] = 0
            ctx["late_ticks"] = 0
            ctx["wages_paid"] = 0.0
            ctx["late_penalty_applied"] = False
            ctx["absence_penalty_applied"] = False
            ctx["late_event_emitted"] = False
            ctx["absence_event_emitted"] = False
            ctx["departure_event_emitted"] = False
            ctx["late_help_event_emitted"] = False
            ctx["took_shift_event_emitted"] = False
            ctx["shift_outcome_recorded"] = False
            ctx["ever_on_time"] = False
            ctx["last_present_tick"] = None
            ctx["late_counter_recorded"] = False

    def _employment_determine_state(
        self,
        *,
        ctx: dict[str, Any],
        tick: int,
        start: int,
        at_required_location: bool,
        employment_cfg: EmploymentConfig,
    ) -> str:
        ticks_since_start = tick - start
        state = ctx["state"]

        if at_required_location:
            ctx["last_present_tick"] = tick
            if ctx["ever_on_time"] or ticks_since_start <= employment_cfg.grace_ticks:
                state = "on_time"
                ctx["ever_on_time"] = True
            else:
                state = "late"
        else:
            if ticks_since_start <= employment_cfg.grace_ticks:
                state = "late"
            elif ticks_since_start > employment_cfg.absent_cutoff:
                state = "absent"
            elif (
                ctx["last_present_tick"] is not None
                and tick - ctx["last_present_tick"] > employment_cfg.absence_slack
            ):
                state = "absent"
            else:
                state = "late"

        return state

    def _employment_apply_state_effects(
        self,
        *,
        snapshot: AgentSnapshot,
        ctx: dict[str, Any],
        state: str,
        at_required_location: bool,
        wage_rate: float,
        lateness_penalty: float,
        employment_cfg: EmploymentConfig,
    ) -> None:
        previous_state = ctx["state"]
        ctx["state"] = state
        snapshot.shift_state = state
        eligible_for_wage = state in {"on_time", "late"} and at_required_location
        coworkers = self._employment_coworkers_on_shift(snapshot)

        if state == "on_time":
            ctx["on_time_ticks"] += 1
        if state == "late":
            ctx["late_ticks"] += 1
            snapshot.late_ticks_today += 1
            if not ctx["late_penalty_applied"] and previous_state not in {
                "on_time",
                "late",
            }:
                snapshot.wallet = max(0.0, snapshot.wallet - lateness_penalty)
                ctx["late_penalty_applied"] = True
                if not ctx["late_counter_recorded"]:
                    snapshot.lateness_counter += 1
                    ctx["late_counter_recorded"] = True
            if not ctx["late_event_emitted"]:
                self._emit_event(
                    "shift_late_start",
                    {
                        "agent_id": snapshot.agent_id,
                        "job_id": snapshot.job_id,
                        "ticks_late": ctx["late_ticks"],
                    },
                )
                ctx["late_event_emitted"] = True
            if not at_required_location:
                penalty = employment_cfg.late_tick_penalty
                if penalty:
                    snapshot.wallet = max(0.0, snapshot.wallet - penalty)
                snapshot.wages_withheld += wage_rate
            if coworkers and not ctx["late_help_event_emitted"]:
                for other_id in coworkers:
                    self.update_relationship(
                        snapshot.agent_id,
                        other_id,
                        trust=0.2,
                        familiarity=0.1,
                        rivalry=-0.1,
                        event="employment_help",
                    )
                self._emit_event(
                    "employment_helped_when_late",
                    {
                        "agent_id": snapshot.agent_id,
                        "coworkers": coworkers,
                    },
                )
                ctx["late_help_event_emitted"] = True

        if state == "absent":
            if not ctx["absence_penalty_applied"]:
                snapshot.wallet = max(0.0, snapshot.wallet - employment_cfg.absence_penalty)
                ctx["absence_penalty_applied"] = True
            snapshot.wages_withheld += wage_rate
            if not ctx["absence_event_emitted"]:
                self._emit_event(
                    "shift_absent",
                    {
                        "agent_id": snapshot.agent_id,
                        "job_id": snapshot.job_id,
                    },
                )
                ctx["absence_event_emitted"] = True
                ctx["absence_events"].append(self.tick)
                snapshot.absent_shifts_7d = len(ctx["absence_events"])
            if coworkers and not ctx["took_shift_event_emitted"]:
                for other_id in coworkers:
                    self.update_relationship(
                        snapshot.agent_id,
                        other_id,
                        trust=-0.1,
                        familiarity=0.0,
                        rivalry=0.3,
                        event="employment_shift_taken",
                    )
                self._emit_event(
                    "employment_took_my_shift",
                    {
                        "agent_id": snapshot.agent_id,
                        "coworkers": coworkers,
                    },
                )
                ctx["took_shift_event_emitted"] = True
        else:
            # Reset absence penalty if they return during the same shift.
            if state in {"on_time", "late"}:
                ctx["absence_penalty_applied"] = False

        if eligible_for_wage and state != "absent":
            snapshot.on_shift = True
            snapshot.wallet += wage_rate
            snapshot.inventory["wages_earned"] = snapshot.inventory.get("wages_earned", 0) + 1
            ctx["wages_paid"] += wage_rate
        else:
            snapshot.on_shift = False
            if previous_state in {"on_time", "late"} and state not in {
                "on_time",
                "late",
            }:
                if not ctx["departure_event_emitted"] and previous_state != "absent":
                    self._emit_event(
                        "shift_departed_early",
                        {
                            "agent_id": snapshot.agent_id,
                            "job_id": snapshot.job_id,
                        },
                    )
                    ctx["departure_event_emitted"] = True

    def _employment_finalize_shift(
        self,
        *,
        snapshot: AgentSnapshot,
        ctx: dict[str, Any],
        employment_cfg: EmploymentConfig,
        job_id: str | None,
    ) -> None:
        if ctx["shift_started_tick"] is None or ctx["shift_outcome_recorded"]:
            snapshot.shift_state = "post_shift"
            snapshot.on_shift = False
            return

        scheduled = max(1, ctx["scheduled_ticks"])
        attendance_value = ctx["on_time_ticks"] / scheduled
        ctx["attendance_samples"].append(attendance_value)
        if ctx["absence_event_emitted"] or ctx["state"] == "absent":
            # absence already recorded when event emitted.
            pass
        snapshot.attendance_ratio = sum(ctx["attendance_samples"]) / len(ctx["attendance_samples"])
        ctx["shift_outcome_recorded"] = True
        ctx["state"] = "post_shift"
        snapshot.shift_state = "post_shift"
        snapshot.on_shift = False
        # Reset per-shift counters ready for next cycle.
        ctx["shift_started_tick"] = None
        ctx["shift_end_tick"] = None
        ctx["last_present_tick"] = None
        ctx["late_penalty_applied"] = False
        ctx["absence_penalty_applied"] = False
        ctx["late_event_emitted"] = False
        ctx["absence_event_emitted"] = False
        ctx["departure_event_emitted"] = False
        ctx["late_counter_recorded"] = False
        snapshot.late_ticks_today = ctx["late_ticks"]
        ctx["late_ticks"] = 0

    def _employment_coworkers_on_shift(self, snapshot: AgentSnapshot) -> list[str]:
        job_id = snapshot.job_id
        if job_id is None:
            return []
        coworkers: list[str] = []
        for other in self.agents.values():
            if other.agent_id == snapshot.agent_id or other.job_id != job_id:
                continue
            other_ctx = self._get_employment_context(other.agent_id)
            if other_ctx["state"] in {"on_time", "late"}:
                coworkers.append(other.agent_id)
        return coworkers

    def _employment_enqueue_exit(self, agent_id: str, tick: int) -> None:
        if agent_id in self._employment_exit_queue:
            return
        self._employment_exit_queue.append(agent_id)
        self._employment_exit_queue_timestamps[agent_id] = tick
        snapshot = self.agents.get(agent_id)
        if snapshot is not None:
            snapshot.exit_pending = True
        limit = self.config.employment.exit_queue_limit
        if limit and len(self._employment_exit_queue) > limit:
            self._emit_event(
                "employment_exit_queue_overflow",
                {
                    "pending_count": len(self._employment_exit_queue),
                    "limit": limit,
                },
            )
        else:
            self._emit_event(
                "employment_exit_pending",
                {
                    "agent_id": agent_id,
                    "pending_count": len(self._employment_exit_queue),
                },
            )

    def _employment_remove_from_queue(self, agent_id: str) -> None:
        if agent_id in self._employment_exit_queue:
            self._employment_exit_queue.remove(agent_id)
        self._employment_exit_queue_timestamps.pop(agent_id, None)
        snapshot = self.agents.get(agent_id)
        if snapshot is not None:
            snapshot.exit_pending = False

    def employment_queue_snapshot(self) -> dict[str, Any]:
        return {
            "pending": list(self._employment_exit_queue),
            "pending_count": len(self._employment_exit_queue),
            "exits_today": self._employment_exits_today,
            "daily_exit_cap": self.config.employment.daily_exit_cap,
            "queue_limit": self.config.employment.exit_queue_limit,
            "review_window": self.config.employment.exit_review_window,
        }

    def employment_request_manual_exit(self, agent_id: str, tick: int) -> bool:
        if agent_id not in self.agents:
            return False
        self._employment_manual_exits.add(agent_id)
        self._emit_event(
            "employment_exit_manual_request",
            {
                "agent_id": agent_id,
                "tick": tick,
            },
        )
        return True

    def employment_defer_exit(self, agent_id: str) -> bool:
        if agent_id not in self.agents:
            return False
        self._employment_manual_exits.discard(agent_id)
        self._employment_remove_from_queue(agent_id)
        self._emit_event(
            "employment_exit_deferred",
            {
                "agent_id": agent_id,
                "pending_count": len(self._employment_exit_queue),
            },
        )
        return True

    def _update_basket_metrics(self) -> None:
        basket_cost = (
            self.config.economy.get("meal_cost", 0.0)
            + self.config.economy.get("cook_energy_cost", 0.0)
            + self.config.economy.get("cook_hygiene_cost", 0.0)
            + self.config.economy.get("ingredients_cost", 0.0)
        )
        for snapshot in self.agents.values():
            snapshot.inventory["basket_cost"] = basket_cost
        self._restock_economy()

    def _restock_economy(self) -> None:
        restock_amount = int(self.config.economy.get("stove_stock_replenish", 0))
        if restock_amount <= 0:
            return
        if self.tick % 200 != 0:
            return
        for obj in self.objects.values():
            if obj.object_type == "stove":
                before = obj.stock.get("raw_ingredients", 0)
                obj.stock["raw_ingredients"] = before + restock_amount
                self._emit_event(
                    "stock_replenish",
                    {
                        "object_id": obj.object_id,
                        "type": "stove",
                        "amount": restock_amount,
                    },
                )
