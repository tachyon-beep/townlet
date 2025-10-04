"""Grid world representation and affordance integration."""

from __future__ import annotations

import random
import logging
import os
import copy
import time
from collections import OrderedDict, deque
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Optional

from townlet.agents.models import (
    Personality,
    PersonalityProfile,
    PersonalityProfiles,
    personality_from_profile,
)
from townlet.agents.relationship_modifiers import (
    RelationshipDelta,
    RelationshipEvent,
    apply_personality_modifiers,
)
from townlet.config import AffordanceRuntimeConfig, EmploymentConfig, SimulationConfig
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
from townlet.world.console_bridge import ConsoleBridge
from townlet.world.queue_conflict import QueueConflictTracker
from townlet.world.affordances import (
    AffordanceOutcome,
    AffordanceRuntimeContext,
    DefaultAffordanceRuntime,
    HookPayload,
    RunningAffordanceState,
    apply_affordance_outcome,
    build_hook_payload,
)
from townlet.world.queue_manager import QueueManager
from townlet.world.employment import EmploymentEngine
from townlet.world.relationships import RelationshipLedger, RelationshipParameters
from townlet.world.rivalry import RivalryLedger, RivalryParameters
from townlet.world.hooks import load_modules as load_hook_modules
from townlet.world.preconditions import (
    CompiledPrecondition,
    PreconditionSyntaxError,
    compile_preconditions,
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


_DEFAULT_PROFILE_NAME = "balanced"


def _default_personality() -> Personality:
    """Provide a neutral personality for agents lacking explicit traits."""

    return personality_from_profile(_DEFAULT_PROFILE_NAME)[1]


def _resolve_personality_profile(name: str | None) -> tuple[str, Personality]:
    try:
        return personality_from_profile(name)
    except KeyError:
        logger.warning(
            "unknown_personality_profile name=%s fallback=%s",
            name,
            _DEFAULT_PROFILE_NAME,
        )
        return personality_from_profile(_DEFAULT_PROFILE_NAME)


def _normalize_profile_name(name: str | None) -> str | None:
    if name is None:
        return None
    trimmed = str(name).strip()
    return trimmed.lower() if trimmed else None


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
    personality_profile: str = _DEFAULT_PROFILE_NAME
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
        profile_name = (self.personality_profile or "").strip().lower()
        if profile_name:
            resolved_name, resolved = _resolve_personality_profile(profile_name)
            self.personality_profile = resolved_name
            current_personality = getattr(self, "personality", None)
            if current_personality is None or current_personality == resolved:
                self.personality = resolved


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
    _personality_reward_enabled: bool = field(init=False, default=False, repr=False)
    _personality_profile_cache: dict[str, PersonalityProfile] = field(
        init=False,
        default_factory=dict,
        repr=False,
    )
    _active_reservations: dict[str, str] = field(init=False, default_factory=dict)
    objects: dict[str, InteractiveObject] = field(init=False, default_factory=dict)
    affordances: dict[str, AffordanceSpec] = field(init=False, default_factory=dict)
    _running_affordances: dict[str, RunningAffordance] = field(init=False, default_factory=dict)
    _pending_events: dict[int, list[dict[str, Any]]] = field(init=False, default_factory=dict)
    store_stock: dict[str, dict[str, int]] = field(init=False, default_factory=dict)
    _job_keys: list[str] = field(init=False, default_factory=list)
    employment: EmploymentEngine = field(init=False, repr=False)

    _rivalry_ledgers: dict[str, RivalryLedger] = field(init=False, default_factory=dict)
    _relationship_ledgers: dict[str, RelationshipLedger] = field(init=False, default_factory=dict)
    _relationship_churn: RelationshipChurnAccumulator = field(init=False)
    _relationship_window_ticks: int = 600
    _recent_meal_participants: dict[str, dict[str, Any]] = field(init=False, default_factory=dict)
    _rng_seed: Optional[int] = field(init=False, default=None)
    _rng_state: Optional[tuple[Any, ...]] = field(init=False, default=None)
    _rng: Optional[random.Random] = field(init=False, default=None, repr=False)
    affordance_runtime_factory: Callable[["WorldState", AffordanceRuntimeContext], "DefaultAffordanceRuntime"] | None = None
    affordance_runtime_config: AffordanceRuntimeConfig | None = None
    _affordance_manifest_info: dict[str, object] = field(init=False, default_factory=dict)
    _objects_by_position: dict[tuple[int, int], list[str]] = field(init=False, default_factory=dict)
    _console: ConsoleBridge = field(init=False)
    _queue_conflicts: QueueConflictTracker = field(init=False)
    _hook_registry: HookRegistry = field(init=False, repr=False)
    _ctx_reset_requests: set[str] = field(init=False, default_factory=set)
    _respawn_counters: dict[str, int] = field(init=False, default_factory=dict)

    @classmethod
    def from_config(
        cls,
        config: SimulationConfig,
        *,
        rng: Optional[random.Random] = None,
        affordance_runtime_factory: Callable[["WorldState", AffordanceRuntimeContext], "DefaultAffordanceRuntime"] | None = None,
        affordance_runtime_config: AffordanceRuntimeConfig | None = None,
    ) -> "WorldState":
        """Bootstrap the initial world from config."""

        instance = cls(
            config=config,
            affordance_runtime_factory=affordance_runtime_factory,
            affordance_runtime_config=affordance_runtime_config,
        )
        instance.attach_rng(rng or random.Random())
        return instance

    def __post_init__(self) -> None:
        self._personality_reward_enabled = self.config.reward_personality_scaling_enabled()
        self._personality_profile_cache.clear()
        self.queue_manager = QueueManager(config=self.config)
        self.embedding_allocator = EmbeddingAllocator(config=self.config)
        self._active_reservations = {}
        self.objects = {}
        self.affordances = {}
        self._running_affordances = {}
        self._pending_events = {}
        self.store_stock = {}
        self._job_keys = list(self.config.jobs.keys())
        self.employment = EmploymentEngine(self.config, self._emit_event)
        # Backwards-compatible views for existing helpers (to be removed in later phases).
        self._employment_state = self.employment._state
        self._employment_exit_queue = self.employment._exit_queue
        self._employment_exit_queue_timestamps = self.employment._exit_timestamps
        self._employment_manual_exits = self.employment._manual_exits
        self._employment_exits_today = 0
        self.employment.reset_exits_today()
        self._rivalry_ledgers = {}
        self._relationship_ledgers = {}
        self._relationship_window_ticks = 600
        self._relationship_churn = RelationshipChurnAccumulator(
            window_ticks=self._relationship_window_ticks,
            max_samples=8,
        )
        self._recent_meal_participants = {}
        runtime_cfg = self.affordance_runtime_config
        self._runtime_instrumentation_level = (
            runtime_cfg.instrumentation if runtime_cfg is not None else "off"
        )
        self._runtime_options = (
            dict(runtime_cfg.options) if runtime_cfg is not None else {}
        )
        self._load_affordance_definitions()
        self._rng_seed = None
        if self._rng is None:
            self._rng = random.Random()
        self._rng_state = self._rng.getstate()
        self._console = ConsoleBridge(
            world=self,
            history_limit=_CONSOLE_HISTORY_LIMIT,
            buffer_limit=_CONSOLE_RESULT_BUFFER_LIMIT,
        )
        self._register_default_console_handlers()
        from townlet.world.queue_conflict import QueueConflictTracker

        self._queue_conflicts = QueueConflictTracker(
            world=self,
            record_rivalry_conflict=self._apply_rivalry_conflict,
        )
        self._hook_registry = HookRegistry()
        modules = list(self.config.affordances.runtime.hook_allowlist)
        if not modules:
            modules.append("townlet.world.hooks.default")
        extra = os.environ.get("TOWNLET_AFFORDANCE_HOOK_MODULES")
        self.loaded_hook_modules: list[str] = []
        self.rejected_hook_modules: list[tuple[str, str]] = []  # (module, reason)

        if extra and self.config.affordances.runtime.allow_env_hooks:
            for module in extra.split(","):
                mod = module.strip()
                if mod:
                    modules.append(mod)
        elif extra and not self.config.affordances.runtime.allow_env_hooks:
            self.rejected_hook_modules.append(
                ("env@TOWNLET_AFFORDANCE_HOOK_MODULES", "environment overrides disabled")
            )
            logger.warning(
                "affordance_hook_rejected module=%s reason=%s",
                "env@TOWNLET_AFFORDANCE_HOOK_MODULES",
                "environment overrides disabled",
            )

        allowed = set(self.config.affordances.runtime.hook_allowlist)
        filtered: list[str] = []
        for module in modules:
            if module in filtered:
                continue
            if module.startswith("townlet.world.hooks") or module in allowed:
                filtered.append(module)
            else:
                self.rejected_hook_modules.append((module, "not in hook_allowlist"))
                logger.warning(
                    "affordance_hook_rejected module=%s reason=%s",
                    module,
                    "not in hook_allowlist",
                )

        accepted, loader_rejected = load_hook_modules(self, filtered)
        self.loaded_hook_modules.extend(accepted)
        for module, reason in loader_rejected:
            self.rejected_hook_modules.append((module, reason))
            logger.warning(
                "affordance_hook_rejected module=%s reason=%s",
                module,
                reason,
            )
        if accepted:
            logger.info(
                "affordance_hooks_loaded modules=%s",
                ",".join(accepted),
            )
        context = AffordanceRuntimeContext(
            world=self,
            queue_manager=self.queue_manager,
            objects=self.objects,
            affordances=self.affordances,
            running_affordances=self._running_affordances,
            active_reservations=self._active_reservations,
            emit_event=self._emit_event,
            sync_reservation=self._sync_reservation,
            apply_affordance_effects=self._apply_affordance_effects,
            dispatch_hooks=self._dispatch_affordance_hooks,
            record_queue_conflict=self._record_queue_conflict,
            apply_need_decay=self._apply_need_decay,
            build_precondition_context=self._build_precondition_context,
            snapshot_precondition_context=self._snapshot_precondition_context,
        )
        if self.affordance_runtime_factory is not None:
            self._affordance_runtime = self.affordance_runtime_factory(self, context)
        else:
            self._affordance_runtime = DefaultAffordanceRuntime(
                context,
                running_cls=RunningAffordance,
                instrumentation=self._runtime_instrumentation_level,
                options=self._runtime_options,
            )
        self._economy_baseline: dict[str, float] = {
            key: float(value) for key, value in self.config.economy.items()
        }
        self._price_spike_events: dict[str, dict[str, float]] = {}
        self._utility_status: dict[str, bool] = {"power": True, "water": True}
        self._utility_events: dict[str, set[str]] = {
            "power": set(),
            "water": set(),
        }
        self._object_utility_baselines: dict[str, dict[str, float]] = {}

    @property
    def affordance_runtime(self) -> DefaultAffordanceRuntime:
        return self._affordance_runtime

    @property
    def runtime_instrumentation_level(self) -> str:
        return getattr(self, "_runtime_instrumentation_level", "off")

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
        self._console.apply(operations)

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

        self._console.register_handler(
            name,
            handler,
            mode=mode,
            require_cmd_id=require_cmd_id,
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

        return self._console.consume_results()

    def _record_console_result(self, result: ConsoleCommandResult) -> None:
        self._console.record_result(result)

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
        debug_enabled = (
            self._runtime_instrumentation_level == "timings"
            or logger.isEnabledFor(logging.DEBUG)
        )
        for hook_name in hook_names:
            handlers = self._hook_registry.handlers_for(hook_name)
            if not handlers:
                continue
            hook_timer = time.perf_counter() if debug_enabled else None
            base_payload: HookPayload = build_hook_payload(
                stage=stage,
                hook=hook_name,
                tick=self.tick,
                agent_id=agent_id,
                object_id=object_id,
                affordance_id=spec.affordance_id,
                world=self,
                spec=spec,
                extra=extra,
            )
            for handler in handlers:
                context: dict[str, object] = dict(base_payload)
                handler_timer = time.perf_counter() if debug_enabled else None
                try:
                    handler(context)
                except Exception:  # pragma: no cover - defensive
                    logger.exception("Affordance hook '%s' failed", hook_name)
                    continue_execution = False
                    continue
                if debug_enabled and handler_timer is not None:
                    handler_duration_ms = (time.perf_counter() - handler_timer) * 1000.0
                    handler_name = getattr(
                        handler,
                        "__qualname__",
                        getattr(handler, "__name__", handler.__class__.__name__),
                    )
                    logger.debug(
                        "world.resolve_affordances.hook_handler stage=%s hook=%s handler=%s duration_ms=%.2f",
                        stage,
                        hook_name,
                        handler_name,
                        handler_duration_ms,
                    )
                if context.get("cancel"):
                    continue_execution = False
            if debug_enabled and hook_timer is not None:
                hook_duration_ms = (time.perf_counter() - hook_timer) * 1000.0
                logger.debug(
                    "world.resolve_affordances.hook stage=%s hook=%s handlers=%s duration_ms=%.2f",
                    stage,
                    hook_name,
                    len(handlers),
                    hook_duration_ms,
                )
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
            "water_on": bool(stock.get("water_on", 0)) if stock else None,
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
            "affordance_status",
            self._console_affordance_status,
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

    def _console_affordance_status(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        runtime = self.running_affordances_snapshot()
        payload = {
            "running": {
                object_id: asdict(state)
                for object_id, state in runtime.items()
            },
            "running_count": len(runtime),
            "active_reservations": self.active_reservations,
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
        self._affordance_runtime.remove_agent(agent_id)
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
        self._queue_conflicts.remove_agent(agent_id)
        blueprint = {
            "agent_id": snapshot.agent_id,
            "origin_agent_id": snapshot.origin_agent_id or snapshot.agent_id,
            "personality": snapshot.personality,
            "personality_profile": snapshot.personality_profile,
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
        profile_field = blueprint.get("personality_profile")
        resolved_profile, resolved_personality = self._choose_personality_profile(
            agent_id,
            profile_field if isinstance(profile_field, str) else None,
        )
        personality_override = blueprint.get("personality")
        if isinstance(personality_override, Personality):
            resolved_personality = personality_override
        snapshot = AgentSnapshot(
            agent_id=agent_id,
            position=position_tuple,
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=0.0,
            home_position=home_tuple,
            origin_agent_id=origin_agent_id,
            personality=resolved_personality,
            personality_profile=resolved_profile,
        )
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
        profile_field = payload.get("personality_profile")
        profile_name, resolved_personality = self._choose_personality_profile(
            agent_id,
            profile_field if isinstance(profile_field, str) else None,
        )
        snapshot = AgentSnapshot(
            agent_id=agent_id,
            position=(x, y),
            needs={"hunger": hunger, "hygiene": hygiene, "energy": energy},
            wallet=wallet,
            home_position=home_tuple,
            personality=resolved_personality,
            personality_profile=profile_name,
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
            "personality_profile": profile_name,
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
        self._economy_baseline[key] = numeric_value
        if self._price_spike_events:
            self._recompute_price_spikes()
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
            obj.stock.setdefault("power_on", 1)
        if object_type == "bed":
            obj.stock["sleep_slots"] = obj.stock.get("sleep_slots", 1)
            obj.stock.setdefault("sleep_capacity", obj.stock["sleep_slots"])
        if object_type == "shower":
            obj.stock.setdefault("power_on", 1)
            obj.stock.setdefault("water_on", 1)
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
        runtime = self._affordance_runtime
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
            outcome_affordance_id: str | None = None
            outcome_metadata: dict[str, object] = {}

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
            elif kind == "chat":
                target_id = action.get("target") or action.get("listener")
                if not isinstance(target_id, str):
                    continue
                listener = self.agents.get(target_id)
                if listener is None:
                    continue
                if self.rivalry_should_avoid(agent_id, target_id):
                    self.record_chat_failure(agent_id, target_id)
                    continue
                if listener.position != snapshot.position:
                    self.record_chat_failure(agent_id, target_id)
                    continue
                quality_value = action.get("quality", 0.5)
                try:
                    quality = float(quality_value)
                except (TypeError, ValueError):
                    quality = 0.5
                self.record_chat_success(agent_id, target_id, quality)
                action_success = True
            elif kind == "start" and object_id:
                affordance_id = action.get("affordance")
                if affordance_id:
                    affordance_id_str = str(affordance_id)
                    action_success, start_metadata = runtime.start(
                        agent_id,
                        object_id,
                        affordance_id_str,
                        tick=current_tick,
                    )
                    outcome_affordance_id = affordance_id_str
                    if start_metadata:
                        outcome_metadata.update(start_metadata)
            elif kind == "release" and object_id:
                success = bool(action.get("success", True))
                affordance_hint = action.get("affordance")
                reason_value = action.get("reason")
                outcome_affordance_id, release_metadata = runtime.release(
                    agent_id,
                    object_id,
                    success=success,
                    reason=str(reason_value) if reason_value is not None else None,
                    requested_affordance_id=str(affordance_hint)
                    if affordance_hint is not None
                    else None,
                    tick=current_tick,
                )
                action_success = success
                if release_metadata:
                    outcome_metadata.update(release_metadata)
            elif kind == "blocked" and object_id:
                runtime.handle_blocked(object_id, current_tick)
                action_success = False

            if kind:
                outcome = AffordanceOutcome(
                    agent_id=agent_id,
                    kind=str(kind),
                    success=action_success,
                    duration=action_duration,
                    object_id=str(object_id) if isinstance(object_id, str) else None,
                    affordance_id=str(outcome_affordance_id) if outcome_affordance_id else None,
                    tick=current_tick,
                    metadata=dict(outcome_metadata) if outcome_metadata else {},
                )
                apply_affordance_outcome(snapshot, outcome)

    def resolve_affordances(self, current_tick: int) -> None:
        """Resolve queued affordances and hooks."""
        self._affordance_runtime.resolve(tick=current_tick)

    def running_affordances_snapshot(self) -> dict[str, RunningAffordanceState]:
        """Return a serializable view of running affordances (for tests/telemetry)."""

        return self._affordance_runtime.running_snapshot()

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
        self._queue_conflicts.record_queue_conflict(
            object_id=object_id,
            actor=actor,
            rival=rival,
            reason=reason,
            queue_length=queue_length,
            intensity=intensity,
        )

    def register_rivalry_conflict(
        self,
        agent_a: str,
        agent_b: str,
        *,
        intensity: float = 1.0,
        reason: str = "conflict",
    ) -> None:
        self._apply_rivalry_conflict(
            agent_a,
            agent_b,
            intensity=intensity,
            reason=reason,
        )

    def _apply_rivalry_conflict(
        self,
        agent_a: str,
        agent_b: str,
        *,
        intensity: float = 1.0,
        reason: str = "conflict",
    ) -> None:
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
        self._queue_conflicts.record_rivalry_event(
            tick=self.tick,
            agent_a=agent_a,
            agent_b=agent_b,
            intensity=intensity,
            reason=reason,
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

        return self._queue_conflicts.consume_chat_events()

    def consume_relationship_avoidance_events(self) -> list[dict[str, Any]]:
        """Return relationship avoidance events recorded since the last call."""

        return self._queue_conflicts.consume_avoidance_events()

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

        return self._queue_conflicts.consume_rivalry_events()

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

    def _choose_personality_profile(
        self, agent_id: str, profile_name: str | None = None
    ) -> tuple[str, Personality]:
        candidate = _normalize_profile_name(profile_name)
        config = getattr(self, "config", None)
        if config is not None and hasattr(config, "resolve_personality_profile"):
            try:
                chosen = config.resolve_personality_profile(agent_id, candidate)
            except Exception:  # pragma: no cover - defensive fallback
                chosen = candidate
        else:
            chosen = candidate
        return _resolve_personality_profile(chosen)

    def select_personality_profile(
        self, agent_id: str, profile_name: str | None = None
    ) -> tuple[str, Personality]:
        """Public helper for modules assigning agent personalities."""

        return self._choose_personality_profile(agent_id, profile_name)

    def _personality_for(self, agent_id: str) -> Personality:
        snapshot = self.agents.get(agent_id)
        if snapshot is None or snapshot.personality is None:
            return _default_personality()
        return snapshot.personality

    def _profile_for_snapshot(
        self, snapshot: AgentSnapshot
    ) -> PersonalityProfile | None:
        if not self._personality_reward_enabled:
            return None
        name = getattr(snapshot, "personality_profile", None)
        if not name:
            return None
        key = str(name).strip().lower()
        if not key:
            return None
        profile = self._personality_profile_cache.get(key)
        if profile is None:
            try:
                profile = PersonalityProfiles.get(key)
            except KeyError:
                return None
            self._personality_profile_cache[key] = profile
        return profile

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

    def load_relationship_metrics(self, payload: Mapping[str, object] | None) -> None:
        if not payload:
            self._relationship_churn = RelationshipChurnAccumulator(
                window_ticks=self._relationship_window_ticks,
                max_samples=8,
            )
            return
        self._relationship_churn.ingest_payload(dict(payload))

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
        self._queue_conflicts.record_chat_event(
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
        self._queue_conflicts.record_chat_event(
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

    def record_relationship_guard_block(
        self,
        *,
        agent_id: str,
        reason: str,
        target_agent: str | None = None,
        object_id: str | None = None,
    ) -> None:
        payload = {
            "agent": agent_id,
            "reason": reason,
            "target": target_agent,
            "object_id": object_id,
            "tick": int(self.tick),
        }
        self._queue_conflicts.record_avoidance_event(payload)

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
        self._affordance_runtime.handle_blocked(object_id, tick)

    def _start_affordance(self, agent_id: str, object_id: str, affordance_id: str) -> bool:
        success, _ = self._affordance_runtime.start(
            agent_id,
            object_id,
            affordance_id,
            tick=self.tick,
        )
        return success

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
                    multiplier = 1.0
                    profile = self._profile_for_snapshot(snapshot)
                    if profile is not None:
                        raw = profile.need_multipliers.get(need, 1.0)
                        try:
                            multiplier = float(raw)
                        except (TypeError, ValueError):
                            multiplier = 1.0
                        if multiplier <= 0.0:
                            multiplier = 1.0
                    adjusted_decay = decay * multiplier
                    snapshot.needs[need] = max(0.0, snapshot.needs[need] - adjusted_decay)
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
        self.employment.assign_jobs_to_agents(self)

    def _apply_job_state(self) -> None:
        self.employment.apply_job_state(self)

    def _apply_job_state_legacy(self) -> None:
        self.employment._apply_job_state_legacy(self)

    def _apply_job_state_enforced(self) -> None:
        self.employment._apply_job_state_enforced(self)

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
        self.employment.enqueue_exit(self, agent_id, tick)

    def _employment_remove_from_queue(self, agent_id: str) -> None:
        self.employment.remove_from_queue(self, agent_id)

    def employment_queue_snapshot(self) -> dict[str, Any]:
        return self.employment.queue_snapshot()

    def employment_request_manual_exit(self, agent_id: str, tick: int) -> bool:
        return self.employment.request_manual_exit(self, agent_id, tick)

    def employment_defer_exit(self, agent_id: str) -> bool:
        return self.employment.defer_exit(self, agent_id)

    def employment_exits_today(self) -> int:
        return self._employment_exits_today

    def set_employment_exits_today(self, value: int) -> None:
        self._employment_exits_today = max(0, int(value))
        self.employment.set_exits_today(self._employment_exits_today)

    def reset_employment_exits_today(self) -> None:
        self.set_employment_exits_today(0)

    def increment_employment_exits_today(self) -> None:
        self.set_employment_exits_today(self._employment_exits_today + 1)

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

    # ------------------------------------------------------------------
    # Perturbation helpers: price spikes, utilities, arranged meets
    # ------------------------------------------------------------------
    def apply_price_spike(
        self,
        event_id: str,
        *,
        magnitude: float,
        targets: Iterable[str] | None = None,
    ) -> None:
        resolved = tuple(self._resolve_price_targets(targets))
        if not resolved:
            return
        self._price_spike_events[event_id] = {
            "magnitude": max(float(magnitude), 0.0),
            "targets": resolved,
        }
        self._recompute_price_spikes()

    def clear_price_spike(self, event_id: str) -> None:
        if event_id not in self._price_spike_events:
            return
        self._price_spike_events.pop(event_id, None)
        self._recompute_price_spikes()

    def apply_utility_outage(self, event_id: str, utility: str) -> None:
        util = utility.lower()
        events = self._utility_events.setdefault(util, set())
        if event_id in events:
            return
        events.add(event_id)
        if len(events) == 1:
            self._set_utility_state(util, online=False)

    def clear_utility_outage(self, event_id: str, utility: str) -> None:
        util = utility.lower()
        events = self._utility_events.setdefault(util, set())
        if event_id not in events:
            return
        events.discard(event_id)
        if not events:
            self._set_utility_state(util, online=True)

    def apply_arranged_meet(
        self,
        *,
        location: str | None,
        targets: Iterable[str] | None = None,
    ) -> None:
        if not targets:
            return
        obj = None
        if location:
            obj = self.objects.get(location)
            if obj is None:
                for candidate in self.objects.values():
                    if candidate.object_type == location:
                        obj = candidate
                        break
        position = None
        if obj is not None and obj.position is not None:
            position = (int(obj.position[0]), int(obj.position[1]))
        if position is None:
            return
        for agent_id in targets:
            snapshot = self.agents.get(str(agent_id))
            if snapshot is None:
                continue
            snapshot.position = position
            self.request_ctx_reset(snapshot.agent_id)
            self._emit_event(
                "arranged_meet_relocated",
                {
                    "agent_id": snapshot.agent_id,
                    "location": obj.object_id if obj is not None else location,
                    "tick": self.tick,
                },
            )

    def utility_online(self, utility: str) -> bool:
        return self._utility_status.get(utility.lower(), True)

    def _resolve_price_targets(self, targets: Iterable[str] | None) -> list[str]:
        resolved: list[str] = []
        if not targets:
            return list(self._economy_baseline.keys())
        groups = {
            "global": list(self.config.economy.keys()),
            "market": [
                "meal_cost",
                "cook_energy_cost",
                "cook_hygiene_cost",
                "ingredients_cost",
            ],
        }
        for target in targets:
            key = str(target).lower()
            if key in groups:
                for entry in groups[key]:
                    if entry in self.config.economy and entry not in resolved:
                        resolved.append(entry)
                continue
            if key in self.config.economy and key not in resolved:
                resolved.append(key)
        return resolved

    def _recompute_price_spikes(self) -> None:
        for key, value in self._economy_baseline.items():
            self.config.economy[key] = value
        for event in self._price_spike_events.values():
            magnitude = max(event.get("magnitude", 1.0), 0.0)
            for key in event.get("targets", ()):  # type: ignore[arg-type]
                if key in self.config.economy:
                    self.config.economy[key] = self.config.economy[key] * magnitude
        self._update_basket_metrics()

    def _set_utility_state(self, utility: str, *, online: bool) -> None:
        utility_key = utility.lower()
        self._utility_status[utility_key] = online
        affected_types = {
            "power": {"stove"},
            "water": {"shower", "sink"},
        }.get(utility_key, set())
        flag = f"{utility_key}_on"
        for obj in self.objects.values():
            if affected_types and obj.object_type not in affected_types:
                continue
            baseline_flags = self._object_utility_baselines.setdefault(obj.object_id, {})
            if not online:
                baseline_flags.setdefault(flag, float(obj.stock.get(flag, 1.0)))
                obj.stock[flag] = 0.0
                active_agent = self.queue_manager.active_agent(obj.object_id)
                if active_agent is not None:
                    self.queue_manager.release(
                        obj.object_id, active_agent, self.tick, success=False
                    )
                    self._sync_reservation(obj.object_id)
            else:
                baseline = baseline_flags.get(flag, 1.0)
                obj.stock[flag] = baseline

    def economy_settings(self) -> dict[str, float]:
        """Return the current economy configuration values."""

        return {str(key): float(value) for key, value in self.config.economy.items()}

    def active_price_spikes(self) -> dict[str, dict[str, object]]:
        """Return a summary of currently active price spike events."""

        snapshot: dict[str, dict[str, object]] = {}
        for event_id, info in self._price_spike_events.items():
            snapshot[event_id] = {
                "magnitude": float(info.get("magnitude", 0.0)),
                "targets": [str(target) for target in info.get("targets", ())],
            }
        return snapshot

    def utility_snapshot(self) -> dict[str, bool]:
        """Return on/off status for tracked utilities."""

        return {str(key): bool(value) for key, value in self._utility_status.items()}
