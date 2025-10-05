"""Grid world representation and affordance integration."""

from __future__ import annotations

import copy
import logging
import os
import random
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any

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
    ConsoleCommandResult,
)
from townlet.console.service import ConsoleService
from townlet.observations.embedding import EmbeddingAllocator
from townlet.telemetry.relationship_metrics import RelationshipChurnAccumulator
from townlet.world.affordance_runtime import AffordanceCoordinator
from townlet.world.affordance_runtime_service import AffordanceRuntimeService
from townlet.world.affordances import (
    AffordanceOutcome,
    AffordanceRuntimeContext,
    DefaultAffordanceRuntime,
    RunningAffordanceState,
    apply_affordance_outcome,
)
from townlet.world.console_handlers import (
    WorldConsoleController,
    install_world_console_handlers,
)
from townlet.world.employment_runtime import EmploymentRuntime
from townlet.world.employment_service import EmploymentCoordinator, create_employment_coordinator
from townlet.world.hooks import load_modules as load_hook_modules
from townlet.world.observation import (
    find_nearest_object_of_type as observation_find_nearest_object_of_type,
)
from townlet.world.observation import (
    snapshot_precondition_context,
)
from townlet.world.preconditions import (
    CompiledPrecondition,
    PreconditionSyntaxError,
    compile_preconditions,
)
from townlet.world.queue_conflict import QueueConflictTracker
from townlet.world.queue_manager import QueueManager
from townlet.world.relationships import (
    RelationshipLedger,
    RelationshipParameters,
    RelationshipTie,
)
from townlet.world.rivalry import RivalryLedger, RivalryParameters

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


class WorldSpatialIndex:
    """Maintains spatial lookups to accelerate world queries.

    World code calls into the index whenever agents move, spawn, or despawn so
    other subsystems (observations, telemetry) can run O(radius²) queries rather
    than scanning every agent. Reservation tiles are tracked separately because
    they are derived from objects instead of the agent registry.
    """

    def __init__(self) -> None:
        self._agents_by_position: dict[tuple[int, int], list[str]] = {}
        self._positions_by_agent: dict[str, tuple[int, int]] = {}
        self._reservation_tiles: set[tuple[int, int]] = set()

    # Agent bookkeeping -------------------------------------------------
    def rebuild(
        self,
        agents: Mapping[str, AgentSnapshot],
        objects: Mapping[str, InteractiveObject],
        active_reservations: Mapping[str, str],
    ) -> None:
        """Recalculate cached lookups from authoritative world state."""

        self._agents_by_position.clear()
        self._positions_by_agent.clear()
        for agent_id, snapshot in agents.items():
            position = tuple(snapshot.position)
            self._positions_by_agent[agent_id] = position
            bucket = self._agents_by_position.setdefault(position, [])
            bucket.append(agent_id)
        for bucket in self._agents_by_position.values():
            bucket.sort()
        self._reservation_tiles.clear()
        for object_id, occupant in active_reservations.items():
            if not occupant:
                continue
            obj = objects.get(object_id)
            if obj is None or obj.position is None:
                continue
            self._reservation_tiles.add(obj.position)

    def insert_agent(self, agent_id: str, position: tuple[int, int]) -> None:
        """Register a new agent at ``position`` without rebuilding all indexes."""

        self._positions_by_agent[agent_id] = position
        bucket = self._agents_by_position.setdefault(position, [])
        if agent_id not in bucket:
            bucket.append(agent_id)

    def move_agent(self, agent_id: str, position: tuple[int, int]) -> None:
        """Update cached lookups when an agent moves to ``position``."""

        previous = self._positions_by_agent.get(agent_id)
        if previous is not None:
            bucket = self._agents_by_position.get(previous)
            if bucket is not None:
                try:
                    bucket.remove(agent_id)
                except ValueError:
                    pass
                if not bucket:
                    self._agents_by_position.pop(previous, None)
        self.insert_agent(agent_id, position)

    def remove_agent(self, agent_id: str) -> None:
        """Remove agent entries from cached indices."""

        previous = self._positions_by_agent.pop(agent_id, None)
        if previous is None:
            return
        bucket = self._agents_by_position.get(previous)
        if bucket is None:
            return
        try:
            bucket.remove(agent_id)
        except ValueError:
            return
        if not bucket:
            self._agents_by_position.pop(previous, None)

    def position_of(self, agent_id: str) -> tuple[int, int] | None:
        """Return the cached grid position for ``agent_id`` if known."""

        return self._positions_by_agent.get(agent_id)

    def agents_at(self, position: tuple[int, int]) -> tuple[str, ...]:
        """Return agent identifiers occupying ``position``."""

        return tuple(self._agents_by_position.get(position, ()))

    # Reservation bookkeeping -------------------------------------------
    def set_reservation(self, position: tuple[int, int] | None, active: bool) -> None:
        """Toggle reservation state for the tile at ``position``."""

        if position is None:
            return
        if active:
            self._reservation_tiles.add(position)
        else:
            self._reservation_tiles.discard(position)

    def reservation_tiles(self) -> frozenset[tuple[int, int]]:
        """Return a frozen copy of tiles reserved by active affordances."""

        return frozenset(self._reservation_tiles)


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
    employment: EmploymentCoordinator = field(init=False, repr=False)
    _employment_runtime: EmploymentRuntime = field(init=False, repr=False)

    _rivalry_ledgers: dict[str, RivalryLedger] = field(init=False, default_factory=dict)
    _relationship_ledgers: dict[str, RelationshipLedger] = field(init=False, default_factory=dict)
    _relationship_churn: RelationshipChurnAccumulator = field(init=False)
    _relationship_window_ticks: int = 600
    _recent_meal_participants: dict[str, dict[str, Any]] = field(init=False, default_factory=dict)
    _rng_seed: int | None = field(init=False, default=None)
    _rng_state: tuple[Any, ...] | None = field(init=False, default=None)
    _rng: random.Random | None = field(init=False, default=None, repr=False)
    affordance_runtime_factory: (
        Callable[[WorldState, AffordanceRuntimeContext], DefaultAffordanceRuntime]
        | None
    ) = None
    affordance_runtime_config: AffordanceRuntimeConfig | None = None
    _affordance_manifest_info: dict[str, object] = field(init=False, default_factory=dict)
    _objects_by_position: dict[tuple[int, int], list[str]] = field(init=False, default_factory=dict)
    _console: ConsoleService = field(init=False)
    _console_controller: WorldConsoleController = field(init=False, repr=False)
    _spatial_index: WorldSpatialIndex = field(init=False, repr=False)
    _queue_conflicts: QueueConflictTracker = field(init=False)
    _hook_registry: HookRegistry = field(init=False, repr=False)
    _ctx_reset_requests: set[str] = field(init=False, default_factory=set)
    _respawn_counters: dict[str, int] = field(init=False, default_factory=dict)

    @classmethod
    def from_config(
        cls,
        config: SimulationConfig,
        *,
        rng: random.Random | None = None,
        affordance_runtime_factory: (
            Callable[[WorldState, AffordanceRuntimeContext], DefaultAffordanceRuntime]
            | None
        ) = None,
        affordance_runtime_config: AffordanceRuntimeConfig | None = None,
    ) -> WorldState:
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
        self._spatial_index = WorldSpatialIndex()
        self.embedding_allocator = EmbeddingAllocator(config=self.config)
        self._active_reservations = {}
        self.objects = {}
        self.affordances = {}
        self._running_affordances = {}
        self._pending_events = {}
        self.store_stock = {}
        self._job_keys = list(self.config.jobs.keys())
        self.employment = create_employment_coordinator(self.config, self._emit_event)
        self.employment.reset_exits_today()
        self._employment_runtime = EmploymentRuntime(self, self.employment, self._emit_event)
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
        self._console = ConsoleService(
            world=self,
            history_limit=_CONSOLE_HISTORY_LIMIT,
            buffer_limit=_CONSOLE_RESULT_BUFFER_LIMIT,
        )
        self._console_controller = install_world_console_handlers(self, self._console)
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
            snapshot_precondition_context=snapshot_precondition_context,
        )
        runtime_obj: DefaultAffordanceRuntime | AffordanceCoordinator
        if self.affordance_runtime_factory is not None:
            runtime_obj = self.affordance_runtime_factory(self, context)
        else:
            runtime_obj = DefaultAffordanceRuntime(
                context,
                running_cls=RunningAffordance,
                instrumentation=self._runtime_instrumentation_level,
                options=self._runtime_options,
            )
        if isinstance(runtime_obj, AffordanceCoordinator):
            self._affordance_runtime = runtime_obj
        else:
            self._affordance_runtime = AffordanceCoordinator(runtime_obj)
        self._affordance_service = AffordanceRuntimeService(
            world=self,
            context=context,
            coordinator=self._affordance_runtime,
            hook_registry=self._hook_registry,
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
        self.rebuild_spatial_index()

    @property
    def affordance_runtime(self) -> DefaultAffordanceRuntime:
        return self._affordance_service.runtime()

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

    def rebuild_spatial_index(self) -> None:
        self._spatial_index.rebuild(self.agents, self.objects, self._active_reservations)

    def agents_at_tile(self, position: tuple[int, int]) -> tuple[str, ...]:
        return self._spatial_index.agents_at(position)

    def agent_position(self, agent_id: str) -> tuple[int, int] | None:
        return self._spatial_index.position_of(agent_id)

    def reservation_tiles(self) -> frozenset[tuple[int, int]]:
        return self._spatial_index.reservation_tiles()

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

    @property
    def console_controller(self) -> WorldConsoleController:
        """Access the bound console controller (primarily for tests)."""

        return self._console_controller

    @property
    def employment_runtime(self) -> EmploymentRuntime:
        """Access the employment runtime facade (tests/back-compat)."""

        return self._employment_runtime

    @property
    def affordance_service(self) -> AffordanceRuntimeService:
        """Access affordance runtime service (tests/back-compat)."""

        return self._affordance_service

    def register_affordance_hook(
        self, name: str, handler: Callable[[dict[str, Any]], None]
    ) -> None:
        """Register a callable invoked when a manifest hook fires."""

        if hasattr(self, "_affordance_service"):
            self._affordance_service.register_hook(name, handler)
        else:
            self._hook_registry.register(name, handler)

    def clear_affordance_hooks(self, name: str | None = None) -> None:
        """Clear registered affordance hooks (used primarily for tests)."""

        if hasattr(self, "_affordance_service"):
            self._affordance_service.clear_hooks(name)
        else:
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
        debug_enabled = (
            self._runtime_instrumentation_level == "timings"
            or logger.isEnabledFor(logging.DEBUG)
        )
        return self._affordance_service.dispatch_hooks(
            stage,
            hook_names,
            agent_id=agent_id,
            object_id=object_id,
            spec=spec,
            extra=extra,
            debug_enabled=debug_enabled,
        )


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
            inventory = {}
            for key, value in agent.inventory.items():
                if isinstance(value, (int, float)):
                    inventory[key] = int(value)
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
            stock = dict(obj.stock)
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

    def _assign_job_if_missing(self, snapshot: AgentSnapshot) -> None:
        if snapshot.job_id is None and self._job_keys:
            snapshot.job_id = self._job_keys[len(self.agents) % len(self._job_keys)]

    def remove_agent(self, agent_id: str, tick: int) -> dict[str, Any] | None:
        snapshot = self.agents.pop(agent_id, None)
        if snapshot is None:
            return None
        self._spatial_index.remove_agent(agent_id)
        self.queue_manager.remove_agent(agent_id, tick)
        self._affordance_service.remove_agent(agent_id)
        for object_id, occupant in list(self._active_reservations.items()):
            if occupant == agent_id:
                self.queue_manager.release(object_id, agent_id, tick, success=False)
                self._active_reservations.pop(object_id, None)
                obj = self.objects.get(object_id)
                if obj is not None:
                    obj.occupied_by = None
                    self._spatial_index.set_reservation(obj.position, False)
        self.embedding_allocator.release(agent_id, tick)
        self._employment_runtime.remove_agent(agent_id)
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

    def kill_agent(self, agent_id: str, *, reason: str | None = None) -> bool:
        """Remove an agent from the world and emit a kill notification."""

        blueprint = self.remove_agent(agent_id, self.tick)
        if blueprint is None:
            return False
        self._emit_event(
            "agent_killed",
            {
                "agent_id": agent_id,
                "reason": reason,
                "tick": self.tick,
            },
        )
        return True

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
        self._spatial_index.insert_agent(agent_id, snapshot.position)
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
        self._employment_runtime.reset_context(snapshot.agent_id)
        self.embedding_allocator.allocate(snapshot.agent_id, self.tick)

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
            if self._active_reservations.get(object_id):
                self._spatial_index.set_reservation(existing.position, False)

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
            if self._active_reservations.get(object_id):
                self._spatial_index.set_reservation(obj.position, True)

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
        runtime = self._affordance_service
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
                self._spatial_index.move_agent(snapshot.agent_id, target_pos)
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
        self._affordance_service.resolve(tick=current_tick)

    def running_affordances_snapshot(self) -> dict[str, RunningAffordanceState]:
        """Return a serializable view of running affordances (for tests/telemetry)."""

        return self._affordance_service.running_snapshot()

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

    @property
    def active_reservations(self) -> dict[str, str]:
        """Expose a copy of active reservations for diagnostics/tests."""
        return dict(self._active_reservations)

    def active_reservations_view(self) -> Mapping[str, str]:
        """Return a read-only snapshot of active reservations."""

        return MappingProxyType(self._active_reservations)

    def refresh_reservations(self) -> None:
        """Synchronise reservation state from the queue manager."""

        for object_id in self.objects:
            self._sync_reservation(object_id)

    def agent_snapshots_view(self) -> Mapping[str, AgentSnapshot]:
        """Expose current agent snapshots without allowing dict mutation."""

        return MappingProxyType(self.agents)

    def objects_by_position_view(self) -> Mapping[tuple[int, int], tuple[str, ...]]:
        """Return immutable positions mapped to tuples of object IDs."""

        snapshot: dict[tuple[int, int], tuple[str, ...]] = {
            position: tuple(object_ids)
            for position, object_ids in self._objects_by_position.items()
        }
        return MappingProxyType(snapshot)

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
                self._spatial_index.set_reservation(obj.position, False)
        else:
            self._active_reservations[object_id] = active
            if obj is not None:
                obj.occupied_by = active
                self._spatial_index.set_reservation(obj.position, True)

    def _handle_blocked(self, object_id: str, tick: int) -> None:
        self._affordance_service.handle_blocked(object_id, tick)

    def _start_affordance(self, agent_id: str, object_id: str, affordance_id: str) -> bool:
        success, _ = self._affordance_service.start(
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
        self.assign_jobs_to_agents()

    def affordance_manifest_metadata(self) -> dict[str, object]:
        """Expose manifest metadata (path, checksum, counts) for telemetry."""

        return dict(self._affordance_manifest_info)

    def find_nearest_object_of_type(
        self, object_type: str, origin: tuple[int, int]
    ) -> tuple[int, int] | None:
        return observation_find_nearest_object_of_type(self, object_type, origin)

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

    def assign_jobs_to_agents(self) -> None:
        """Assign jobs to agents lacking a valid role."""

        self._employment_runtime.assign_jobs_to_agents()

    def _apply_job_state(self) -> None:
        self._employment_runtime.apply_job_state()

    def _apply_job_state_legacy(self) -> None:
        self.employment._apply_job_state_legacy(self)

    def _apply_job_state_enforced(self) -> None:
        self.employment._apply_job_state_enforced(self)

    # ------------------------------------------------------------------
    # Employment helpers
    # ------------------------------------------------------------------
    def _employment_context_defaults(self) -> dict[str, Any]:
        return self._employment_runtime.context_defaults()

    def _get_employment_context(self, agent_id: str) -> dict[str, Any]:
        return self._employment_runtime.get_context(agent_id)

    def _employment_context_wages(self, agent_id: str) -> float:
        return self._employment_runtime.context_wages(agent_id)

    def _employment_context_punctuality(self, agent_id: str) -> float:
        return self._employment_runtime.context_punctuality(agent_id)

    def _employment_idle_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None:
        self._employment_runtime.idle_state(snapshot, ctx)

    def _employment_prepare_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None:
        self._employment_runtime.prepare_state(snapshot, ctx)

    def _employment_begin_shift(self, ctx: dict[str, Any], start: int, end: int) -> None:
        self._employment_runtime.begin_shift(ctx, start, end)

    def _employment_determine_state(
        self,
        *,
        ctx: dict[str, Any],
        tick: int,
        start: int,
        at_required_location: bool,
        employment_cfg: EmploymentConfig,
    ) -> str:
        return self._employment_runtime.determine_state(
            ctx=ctx,
            tick=tick,
            start=start,
            at_required_location=at_required_location,
            employment_cfg=employment_cfg,
        )

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
        self._employment_runtime.apply_state_effects(
            snapshot=snapshot,
            ctx=ctx,
            state=state,
            at_required_location=at_required_location,
            wage_rate=wage_rate,
            lateness_penalty=lateness_penalty,
            employment_cfg=employment_cfg,
        )

    def _employment_finalize_shift(
        self,
        *,
        snapshot: AgentSnapshot,
        ctx: dict[str, Any],
        employment_cfg: EmploymentConfig,
        job_id: str | None,
    ) -> None:
        self._employment_runtime.finalize_shift(
            snapshot=snapshot,
            ctx=ctx,
            employment_cfg=employment_cfg,
            job_id=job_id,
        )

    def _employment_coworkers_on_shift(self, snapshot: AgentSnapshot) -> list[str]:
        return self._employment_runtime.coworkers_on_shift(snapshot)

    def employment_queue_snapshot(self) -> dict[str, Any]:
        return self._employment_runtime.queue_snapshot()

    def employment_request_manual_exit(self, agent_id: str, tick: int) -> bool:
        return self._employment_runtime.request_manual_exit(agent_id, tick)

    def employment_defer_exit(self, agent_id: str) -> bool:
        return self._employment_runtime.defer_exit(agent_id)

    def employment_exits_today(self) -> int:
        return self._employment_runtime.exits_today()

    def set_employment_exits_today(self, value: int) -> None:
        self._employment_runtime.set_exits_today(value)

    def reset_employment_exits_today(self) -> None:
        self._employment_runtime.reset_exits_today()

    def increment_employment_exits_today(self) -> None:
        self._employment_runtime.increment_exits_today()

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
