"""Grid world representation and affordance integration."""

from __future__ import annotations

import copy
import hashlib
import logging
import os
import pickle
import random
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any

from townlet.agents.models import Personality, PersonalityProfile, PersonalityProfiles
from townlet.agents.relationship_modifiers import RelationshipEvent
from townlet.config import AffordanceRuntimeConfig, SimulationConfig
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
from townlet.world.affordance_runtime import AffordanceCoordinator
from townlet.world.affordance_runtime_service import AffordanceRuntimeService
from townlet.world.affordances import (
    AffordanceEnvironment,
    AffordanceRuntimeContext,
    DefaultAffordanceRuntime,
    RunningAffordanceState,
)
from townlet.world.agents.employment import EmploymentService
from townlet.world.agents.lifecycle import LifecycleService
from townlet.world.agents.nightly_reset import NightlyResetService
from townlet.world.agents.personality import (
    default_personality,
    normalize_profile_name,
    resolve_personality_profile,
)
from townlet.world.agents.registry import AgentRecord, AgentRegistry
from townlet.world.agents.relationships_service import RelationshipService
from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.console import (
    WorldConsoleController,
    install_world_console_handlers,
)
from townlet.world.core.context import WorldContext
from townlet.world.economy import EconomyService
from townlet.world.employment_runtime import EmploymentRuntime
from townlet.world.employment_service import EmploymentCoordinator, create_employment_coordinator
from townlet.world.events import Event, EventDispatcher
from townlet.world.hooks import load_modules as load_hook_modules
from townlet.world.observations.context import snapshot_precondition_context
from townlet.world.observations.interfaces import ObservationServiceProtocol
from townlet.world.observations.service import WorldObservationService
from townlet.world.observations.views import (
    find_nearest_object_of_type as observation_find_nearest_object_of_type,
)
from townlet.world.perturbations import PerturbationService
from townlet.world.preconditions import (
    CompiledPrecondition,
    PreconditionSyntaxError,
    compile_preconditions,
)
from townlet.world.queue import QueueConflictTracker, QueueManager
from townlet.world.relationships import RelationshipTie
from townlet.world.rng import RngStreamManager
from townlet.world.spatial import WorldSpatialIndex
from townlet.world.systems import affordances as affordance_system
from townlet.world.systems import economy as economy_system
from townlet.world.systems import employment as employment_system
from townlet.world.systems import perturbations as perturbation_system
from townlet.world.systems import queues as queue_system
from townlet.world.systems import relationships as relationship_system
from townlet.world.systems.base import SystemContext

logger = logging.getLogger(__name__)

def _derive_seed_from_state(state: tuple[Any, ...]) -> int:
    payload = pickle.dumps(state)
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big", signed=False)

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
    tick: int = 0
    _agents: AgentRegistry = field(init=False, repr=False)
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
    employment: EmploymentCoordinator = field(init=False, repr=False)
    _employment_runtime: EmploymentRuntime = field(init=False, repr=False)
    _employment_service: EmploymentService = field(init=False, repr=False)
    _lifecycle_service: LifecycleService = field(init=False, repr=False)
    _nightly_reset_service: NightlyResetService = field(init=False, repr=False)
    _economy_service: EconomyService = field(init=False, repr=False)
    _perturbation_service: PerturbationService = field(init=False, repr=False)

    _relationships: RelationshipService = field(init=False, repr=False)
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
    _console: ConsoleService | None = field(init=False, default=None, repr=False)
    _console_controller: WorldConsoleController | None = field(init=False, default=None, repr=False)
    _spatial_index: WorldSpatialIndex = field(init=False, repr=False)
    _queue_conflicts: QueueConflictTracker = field(init=False)
    _observation_service: ObservationServiceProtocol | None = field(
        init=False, default=None, repr=False
    )
    _hook_registry: HookRegistry = field(init=False, repr=False)
    _ctx_reset_requests: set[str] = field(init=False, default_factory=set)
    _respawn_counters: dict[str, int] = field(init=False, default_factory=dict)
    _event_dispatcher: EventDispatcher = field(init=False, repr=False)
    _system_rng_manager: RngStreamManager | None = field(init=False, default=None, repr=False)

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
        attach_console: bool = True,
        console_service_factory: (
            Callable[[WorldState], ConsoleService] | None
        ) = None,
    ) -> WorldState:
        """Bootstrap the initial world from config."""

        instance = cls(
            config=config,
            affordance_runtime_factory=affordance_runtime_factory,
            affordance_runtime_config=affordance_runtime_config,
        )
        instance.attach_rng(rng or random.Random())
        if attach_console:
            factory = console_service_factory or build_console_service
            console_service = factory(instance)
            instance.attach_console_service(console_service)
        return instance

    def __post_init__(self) -> None:
        self._personality_reward_enabled = self.config.reward_personality_scaling_enabled()
        self._personality_profile_cache.clear()
        self._agents = AgentRegistry()
        self.queue_manager = QueueManager(config=self.config)
        self._spatial_index = WorldSpatialIndex()
        self.embedding_allocator = EmbeddingAllocator(config=self.config)
        self._active_reservations = {}
        self.objects = {}
        self.affordances = {}
        self._running_affordances = {}
        self._pending_events = {}
        self._event_dispatcher = EventDispatcher()
        self._event_dispatcher.register(self._handle_guardrail_request)
        self.store_stock = {}
        self.employment = create_employment_coordinator(self.config, self._emit_event)
        self.employment.reset_exits_today()
        self._employment_runtime = EmploymentRuntime(self, self.employment, self._emit_event)
        self._employment_service = EmploymentService(
            coordinator=self.employment,
            runtime=self._employment_runtime,
        )
        self._economy_service = EconomyService(
            config=self.config,
            agents=self.agents,
            objects=self.objects,
            queue_manager=self.queue_manager,
            sync_reservation=self._sync_reservation,
            emit_event=self._emit_event,
            tick_supplier=lambda: self.tick,
        )
        self._perturbation_service = PerturbationService(
            economy_service=self._economy_service,
            agents=self.agents,
            objects=self.objects,
            emit_event=self._emit_event,
            request_ctx_reset=self.request_ctx_reset,
            tick_supplier=lambda: self.tick,
        )
        self._relationship_window_ticks = 600
        self._relationships = RelationshipService(
            self.config,
            tick_supplier=lambda: self.tick,
            personality_resolver=self._personality_for,
            churn_window=self._relationship_window_ticks,
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
        if self._rng is None:
            self._rng = random.Random()
        self._rng_state = self._rng.getstate()
        if self._rng_seed is None:
            self._rng_seed = _derive_seed_from_state(self._rng_state)
        self._system_rng_manager = RngStreamManager.from_seed(self._rng_seed)
        self._queue_conflicts = QueueConflictTracker(
            world=self,
            record_rivalry_conflict=self._apply_rivalry_conflict,
        )
        self._hook_registry = HookRegistry()
        self._observation_service = WorldObservationService(config=self.config)
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
        affordance_env = AffordanceEnvironment(
            queue_manager=self.queue_manager,
            agents=self.agents,
            relationships=self.relationships_service,
            objects=self.objects,
            affordances=self.affordances,
            running_affordances=self._running_affordances,
            active_reservations=self._active_reservations,
            emit_event=self._emit_event,
            sync_reservation=self._sync_reservation,
            apply_affordance_effects=self._apply_affordance_effects,
            dispatch_hooks=lambda *args, **kwargs: True,
            record_queue_conflict=self._record_queue_conflict,
            apply_need_decay=self._apply_need_decay,
            build_precondition_context=self._build_precondition_context,
            snapshot_precondition_context=snapshot_precondition_context,
            tick_supplier=lambda: self.tick,
            store_stock=self.store_stock,
            recent_meal_participants=self._recent_meal_participants,
            config=self.config,
            world_ref=self,
        )
        context = AffordanceRuntimeContext(environment=affordance_env)
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
            environment=affordance_env,
            context=context,
            coordinator=self._affordance_runtime,
            hook_registry=self._hook_registry,
        )
        affordance_env.dispatch_hooks = self._affordance_service.dispatch_hooks
        self._lifecycle_service = LifecycleService(
            agents=self.agents,
            objects=self.objects,
            queue_manager=self.queue_manager,
            spatial_index=self._spatial_index,
            employment_service=self._employment_service,
            relationship_service=self._relationships,
            affordance_service=self._affordance_service,
            embedding_allocator=self.embedding_allocator,
            queue_conflicts=self._queue_conflicts,
            recent_meal_participants=self._recent_meal_participants,
            respawn_counters=self._respawn_counters,
            emit_event=self._emit_event,
            request_ctx_reset=self.request_ctx_reset,
            sync_reservation=self._sync_reservation,
            tick_supplier=lambda: self.tick,
            update_basket_metrics=self._economy_service.update_basket_metrics,
            choose_personality_profile=self._choose_personality_profile,
            objects_by_position=self._objects_by_position,
            active_reservations=self._active_reservations,
        )
        self._nightly_reset_service = NightlyResetService(
            agents=self.agents,
            queue_manager=self.queue_manager,
            active_reservations=self._active_reservations,
            employment_service=self._employment_service,
            emit_event=self._emit_event,
            sync_reservation=self._sync_reservation,
            sync_reservation_for_agent=self._lifecycle_service.sync_reservation_for_agent,
            is_tile_blocked=lambda position: position in self._objects_by_position,
        )
        self.rebuild_spatial_index()
        self.context: WorldContext | None = None

    @property
    def affordance_runtime(self) -> DefaultAffordanceRuntime:
        return self._affordance_service.runtime()

    @property
    def agents(self) -> AgentRegistry:
        return self._agents

    @property
    def runtime_instrumentation_level(self) -> str:
        return getattr(self, "_runtime_instrumentation_level", "off")

    @property
    def employment_service(self) -> EmploymentService:
        return self._employment_service

    @property
    def lifecycle_service(self) -> LifecycleService:
        return self._lifecycle_service

    @property
    def nightly_reset_service(self) -> NightlyResetService:
        return self._nightly_reset_service

    @property
    def economy_service(self) -> EconomyService:
        return self._economy_service

    @property
    def perturbation_service(self) -> PerturbationService:
        return self._perturbation_service

    @property
    def _relationship_ledgers(self):
        return self._relationships._relationship_ledgers

    @property
    def _rivalry_ledgers(self):
        return self._relationships._rivalry_ledgers

    @property
    def relationships_service(self) -> RelationshipService:
        """Expose the relationship service for integrations/tests."""

        return self._relationships

    def generate_agent_id(self, base_id: str) -> str:
        return self._lifecycle_service.generate_agent_id(base_id)

    def apply_console(self, operations: Iterable[Any]) -> list[ConsoleCommandResult]:
        """Apply console operations before the tick sequence runs."""
        if self._console is None:
            raise RuntimeError("Console service not attached to world")
        return self._console.apply(operations)

    def attach_rng(self, rng: random.Random) -> None:
        """Attach a deterministic RNG used for world-level randomness."""

        self._rng = rng
        self._rng_state = rng.getstate()
        if self._rng_seed is None:
            self._rng_seed = _derive_seed_from_state(self._rng_state)
        self._system_rng_manager = RngStreamManager.from_seed(self._rng_seed)

    def attach_console_service(self, console: ConsoleService) -> None:
        """Attach a console service and rebuild the world context."""

        self._console = console
        self._console_controller = install_world_console_handlers(self, console)
        self.context = self._build_context(console)

    def _build_context(self, console: ConsoleService) -> WorldContext:
        return WorldContext(
            state=self,
            queue_manager=self.queue_manager,
            queue_conflicts=self._queue_conflicts,
            affordance_service=self._affordance_service,
            console=console,
            employment=self.employment,
            employment_runtime=self._employment_runtime,
            employment_service=self._employment_service,
            lifecycle_service=self._lifecycle_service,
            nightly_reset_service=self._nightly_reset_service,
            relationships=self._relationships,
            economy_service=self._economy_service,
            perturbation_service=self._perturbation_service,
            config=self.config,
            emit_event_callback=self._emit_event,
            sync_reservation_callback=self._sync_reservation,
            observation_service=self._observation_service,
        )

    @property
    def rng(self) -> random.Random:
        if self._rng is None:
            self._rng = random.Random()
        return self._rng

    @property
    def rng_seed(self) -> int | None:
        return getattr(self, "_rng_seed", None)

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

        if self._console is None:
            raise RuntimeError("Console service not attached to world")
        self._console.register_handler(
            name,
            handler,
            mode=mode,
            require_cmd_id=require_cmd_id,
        )

    @property
    def console_controller(self) -> WorldConsoleController:
        """Access the bound console controller (primarily for tests)."""

        if self._console_controller is None:
            raise RuntimeError("Console controller not attached to world")
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

    def spawn_agent(
        self,
        agent_id: str,
        position: tuple[int, int],
        *,
        needs: Mapping[str, float] | None = None,
        home_position: tuple[int, int] | None = None,
        wallet: float | None = None,
        personality_profile: str | None = None,
    ) -> AgentSnapshot:
        """Create a new agent at ``position`` and register supporting state."""

        return self._lifecycle_service.spawn_agent(
            agent_id,
            position,
            needs=needs,
            home_position=home_position,
            wallet=wallet,
            personality_profile=personality_profile,
        )

    def teleport_agent(self, agent_id: str, position: tuple[int, int]) -> tuple[int, int]:
        """Teleport ``agent_id`` to ``position`` if the tile is available."""
        return self._lifecycle_service.teleport_agent(agent_id, position)

    def set_price_target(self, key: str, value: float) -> float:
        """Update the economy price target for ``key`` and refresh metrics."""
        return self._economy_service.set_price_target(key, value)

    def _record_console_result(self, result: ConsoleCommandResult) -> None:
        if self._console is None:
            raise RuntimeError("Console service not attached to world")
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

    def remove_agent(self, agent_id: str, tick: int) -> dict[str, Any] | None:
        return self._lifecycle_service.remove_agent(agent_id, tick)

    def kill_agent(self, agent_id: str, *, reason: str | None = None) -> bool:
        """Remove an agent from the world and emit a kill notification."""
        return self._lifecycle_service.kill_agent(agent_id, reason=reason)

    def respawn_agent(self, blueprint: Mapping[str, Any]) -> None:
        self._lifecycle_service.respawn_agent(blueprint)

    def _assign_job_if_missing(self, snapshot: AgentSnapshot) -> None:
        self._lifecycle_service.assign_job_if_missing(snapshot)

    def _sync_agent_spawn(self, snapshot: AgentSnapshot) -> None:
        self._lifecycle_service.sync_agent_spawn(snapshot)

    def _sync_reservation_for_agent(self, agent_id: str) -> None:
        self._lifecycle_service.sync_reservation_for_agent(agent_id)

    def _is_position_walkable(self, position: tuple[int, int]) -> bool:
        return self._lifecycle_service.is_position_walkable(position)

    def register_object(
        self,
        *,
        object_id: str,
        object_type: str,
        position: tuple[int, int] | None = None,
        stock: Mapping[str, Any] | None = None,
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
        if stock:
            obj.stock.update(dict(stock))
        self.objects[object_id] = obj
        self.store_stock[object_id] = obj.stock
        if obj.position is not None:
            self._index_object_position(object_id, obj.position)
            if self._active_reservations.get(object_id):
                self._spatial_index.set_reservation(obj.position, True)

    def _reset_object_registry(self) -> None:
        self.objects.clear()
        self.store_stock.clear()
        self._objects_by_position.clear()
        self._active_reservations.clear()
        self._spatial_index.rebuild(self.agents, self.objects, self._active_reservations)

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
        affordance_system.process_actions(self, actions, tick=self.tick)

    def resolve_affordances(self, current_tick: int) -> None:
        """Resolve queued affordances and hooks via modular systems."""

        self.tick = current_tick
        ctx = self._system_context()
        queue_system.step(ctx)
        affordance_system.step(ctx)
        employment_system.step(ctx)
        relationship_system.step(ctx)
        economy_system.step(ctx)
        perturbation_system.step(ctx)

    def running_affordances_snapshot(self) -> dict[str, RunningAffordanceState]:
        """Return a serializable view of running affordances (for tests/telemetry)."""

        return self._affordance_service.running_snapshot()

    def _system_context(self) -> SystemContext:
        if self._system_rng_manager is None:
            seed = getattr(self, "_rng_seed", None)
            self._system_rng_manager = RngStreamManager.from_seed(seed)
        return SystemContext(
            state=self,
            rng=self._system_rng_manager,
            events=self._event_dispatcher,
        )

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

        queue_system.refresh_reservations(
            manager=self.queue_manager,
            objects=self.objects,
            active_reservations=self._active_reservations,
            spatial_index=self._spatial_index,
        )

    def agent_snapshots_view(self) -> Mapping[str, AgentSnapshot]:
        """Expose current agent snapshots without allowing dict mutation."""

        return MappingProxyType(self.agents)

    def agent_records_view(self) -> Mapping[str, AgentRecord]:
        """Expose bookkeeping metadata for agent snapshots."""

        return self.agents.records_map()

    def objects_by_position_view(self) -> Mapping[tuple[int, int], tuple[str, ...]]:
        """Return immutable positions mapped to tuples of object IDs."""

        snapshot: dict[tuple[int, int], tuple[str, ...]] = {
            position: tuple(object_ids)
            for position, object_ids in self._objects_by_position.items()
        }
        return MappingProxyType(snapshot)

    def drain_events(self) -> list[dict[str, Any]]:
        """Return all pending events accumulated up to the current tick."""
        events: list[dict[str, Any]] = [
            {
                "event": dispatched.type,
                "tick": dispatched.tick if dispatched.tick is not None else self.tick,
                **dict(dispatched.payload),
            }
            for dispatched in self._event_dispatcher.drain()
        ]
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
        relationship_system.apply_rivalry_conflict(
            self._relationships,
            agent_a,
            agent_b,
            intensity=intensity,
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
        return relationship_system.rivalry_snapshot(self._relationships)

    def relationships_snapshot(self) -> dict[str, dict[str, dict[str, float]]]:
        return relationship_system.relationships_snapshot(self._relationships)

    def relationship_tie(self, agent_id: str, other_id: str) -> RelationshipTie | None:
        """Return the current relationship tie between two agents, if any."""
        return relationship_system.relationship_tie(self._relationships, agent_id, other_id)

    def get_rivalry_ledger(self, agent_id: str):
        """Return the rivalry ledger for ``agent_id``."""

        return relationship_system.get_rivalry_ledger(self._relationships, agent_id)

    def _get_rivalry_ledger(self, agent_id: str):
        return self.get_rivalry_ledger(agent_id)

    def consume_chat_events(self) -> list[dict[str, Any]]:
        """Return chat events staged for reward calculations and clear the buffer."""

        return self._queue_conflicts.consume_chat_events()

    def consume_relationship_avoidance_events(self) -> list[dict[str, Any]]:
        """Return relationship avoidance events recorded since the last call."""

        return self._queue_conflicts.consume_avoidance_events()

    def rivalry_value(self, agent_id: str, other_id: str) -> float:
        """Return the rivalry score between two agents, if present."""
        return relationship_system.rivalry_value(self._relationships, agent_id, other_id)

    def rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool:
        return relationship_system.rivalry_should_avoid(self._relationships, agent_id, other_id)

    def rivalry_top(self, agent_id: str, limit: int) -> list[tuple[str, float]]:
        return relationship_system.rivalry_top(self._relationships, agent_id, limit)

    def consume_rivalry_events(self) -> list[dict[str, Any]]:
        """Return rivalry events recorded since the last call."""

        return self._queue_conflicts.consume_rivalry_events()

    def _choose_personality_profile(
        self, agent_id: str, profile_name: str | None = None
    ) -> tuple[str, Personality]:
        candidate = normalize_profile_name(profile_name)
        config = getattr(self, "config", None)
        if config is not None and hasattr(config, "resolve_personality_profile"):
            try:
                chosen = config.resolve_personality_profile(agent_id, candidate)
            except Exception:  # pragma: no cover - defensive fallback
                chosen = candidate
        else:
            chosen = candidate
        return resolve_personality_profile(chosen)

    def select_personality_profile(
        self, agent_id: str, profile_name: str | None = None
    ) -> tuple[str, Personality]:
        """Public helper for modules assigning agent personalities."""

        return self._choose_personality_profile(agent_id, profile_name)

    def _personality_for(self, agent_id: str) -> Personality:
        snapshot = self.agents.get(agent_id)
        if snapshot is None or snapshot.personality is None:
            return default_personality()
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

    def relationship_metrics_snapshot(self) -> dict[str, object]:
        return relationship_system.relationship_metrics_snapshot(self._relationships)

    def load_relationship_metrics(self, payload: Mapping[str, object] | None) -> None:
        relationship_system.load_relationship_metrics(self._relationships, payload)

    def load_relationship_snapshot(
        self,
        snapshot: dict[str, dict[str, dict[str, float]]],
    ) -> None:
        """Restore relationship ledgers from persisted snapshot data."""
        relationship_system.load_relationship_snapshot(self._relationships, snapshot)

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
        relationship_system.update_relationship(
            self._relationships,
            agent_a,
            agent_b,
            trust=trust,
            familiarity=familiarity,
            rivalry=rivalry,
            event=event,
        )

    def set_relationship(
        self,
        agent_a: str,
        agent_b: str,
        *,
        trust: float,
        familiarity: float,
        rivalry: float,
    ) -> None:
        relationship_system.set_relationship(
            self._relationships,
            agent_a,
            agent_b,
            trust=trust,
            familiarity=familiarity,
            rivalry=rivalry,
        )

    def record_chat_success(self, speaker: str, listener: str, quality: float) -> None:
        clipped_quality = max(0.0, min(1.0, quality))
        relationship_system.update_relationship(
            self._relationships,
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
        self._process_chat_failure(speaker, listener, emit=True)

    def record_relationship_guard_block(
        self,
        *,
        agent_id: str,
        reason: str,
        target_agent: str | None = None,
        object_id: str | None = None,
    ) -> None:
        self._process_relationship_guard_block(
            agent_id,
            reason,
            target_agent=target_agent,
            object_id=object_id,
            emit=True,
        )

    def _process_chat_failure(
        self,
        speaker: str,
        listener: str,
        *,
        emit: bool,
    ) -> None:
        if not speaker or not listener:
            return
        relationship_system.update_relationship(
            self._relationships,
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
        if emit:
            self._emit_event(
                "chat_failure",
                {
                    "speaker": speaker,
                    "listener": listener,
                },
            )

    def _process_relationship_guard_block(
        self,
        agent_id: str,
        reason: str,
        *,
        target_agent: str | None,
        object_id: str | None,
        emit: bool,
    ) -> None:
        queue_payload = {
            "agent": agent_id,
            "reason": reason,
            "target": target_agent,
            "object_id": object_id,
            "tick": int(self.tick),
        }
        self._queue_conflicts.record_avoidance_event(queue_payload)
        if emit:
            event_payload = {
                "agent_id": agent_id,
                "reason": reason,
                "target_agent": target_agent,
                "object_id": object_id,
                "tick": int(self.tick),
            }
            self._emit_event("policy.guardrail.block", event_payload)

    def _handle_guardrail_request(self, event: Event) -> None:
        if event.type != "policy.guardrail.request":
            return
        payload = dict(event.payload)
        variant = str(payload.get("variant") or "")
        if variant == "chat_failure":
            speaker = str(payload.get("speaker") or payload.get("agent") or "")
            listener_value = (
                payload.get("listener")
                or payload.get("target_agent")
                or payload.get("target")
                or ""
            )
            listener = str(listener_value)
            if speaker and listener:
                self._process_chat_failure(speaker, listener, emit=True)
        elif variant == "relationship_block":
            agent = str(payload.get("agent_id") or payload.get("agent") or "")
            reason = str(payload.get("reason") or "")
            if not agent or not reason:
                return
            target_agent = payload.get("target_agent") or payload.get("target")
            object_id = payload.get("object_id")
            self._process_relationship_guard_block(
                agent,
                reason,
                target_agent=target_agent,
                object_id=object_id,
                emit=True,
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _sync_reservation(self, object_id: str) -> None:
        queue_system.sync_reservation(
            manager=self.queue_manager,
            objects=self.objects,
            active_reservations=self._active_reservations,
            spatial_index=self._spatial_index,
            object_id=object_id,
        )

    def _handle_blocked(self, object_id: str, tick: int) -> None:
        affordance_system.handle_blocked(self._affordance_service, object_id, tick)

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

    def emit_event(self, event: str, payload: Mapping[str, Any]) -> Event:
        """Emit an event into both legacy and modular pipelines."""

        event_obj = self._event_dispatcher.emit(event_type=event, payload=payload, tick=self.tick)
        events = self._pending_events.setdefault(self.tick, [])
        events.append({"event": event, "tick": self.tick, **dict(payload)})
        return event_obj

    def _emit_event(self, event: str, payload: dict[str, Any]) -> None:
        self.emit_event(event, payload)

    def event_dispatcher(self) -> EventDispatcher:
        """Return the dispatcher used by modular world systems."""

        return self._event_dispatcher

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

        self._reset_object_registry()
        self.affordances.clear()

        for entry in manifest.objects:
            self.register_object(
                object_id=entry.object_id,
                object_type=entry.object_type,
                position=getattr(entry, "position", None),
                stock=getattr(entry, "stock", None),
            )

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
        if getattr(self, "_relationships", None) is None:
            relationship_system.decay(self._relationships)
        employment_service = getattr(self, "_employment_service", None)
        if employment_service is None:
            coordinator = getattr(self, "employment", None)
            if coordinator is not None and hasattr(coordinator, "apply_job_state"):
                coordinator.apply_job_state(self)  # type: ignore[call-arg]
        if getattr(self, "_economy_service", None) is None:
            self._update_basket_metrics()

    def apply_nightly_reset(self) -> list[str]:
        return employment_system.nightly_reset(self._nightly_reset_service, self.tick)

    def assign_jobs_to_agents(self) -> None:
        """Assign jobs to agents lacking a valid role."""

        employment_system.assign_jobs(self._employment_service)

    def employment_queue_snapshot(self) -> dict[str, Any]:
        return dict(employment_system.queue_snapshot(self._employment_service))

    def employment_request_manual_exit(self, agent_id: str, tick: int) -> bool:
        return employment_system.request_manual_exit(self._employment_service, agent_id, tick)

    def employment_defer_exit(self, agent_id: str) -> bool:
        return employment_system.defer_exit(self._employment_service, agent_id)

    def employment_exits_today(self) -> int:
        return employment_system.exits_today(self._employment_service)

    def set_employment_exits_today(self, value: int) -> None:
        employment_system.set_exits_today(self._employment_service, value)

    def reset_employment_exits_today(self) -> None:
        employment_system.reset_exits_today(self._employment_service)

    def increment_employment_exits_today(self) -> None:
        employment_system.increment_exits_today(self._employment_service)

    def _update_basket_metrics(self) -> None:
        economy_system.update_basket_metrics(self._economy_service)

    def _restock_economy(self) -> None:
        economy_system.restock(self._economy_service)

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
        perturbation_system.apply_price_spike(
            self._perturbation_service,
            event_id,
            magnitude=magnitude,
            targets=targets,
        )

    def clear_price_spike(self, event_id: str) -> None:
        perturbation_system.clear_price_spike(self._perturbation_service, event_id)

    def apply_utility_outage(self, event_id: str, utility: str) -> None:
        perturbation_system.apply_utility_outage(self._perturbation_service, event_id, utility)

    def clear_utility_outage(self, event_id: str, utility: str) -> None:
        perturbation_system.clear_utility_outage(self._perturbation_service, event_id, utility)

    def apply_arranged_meet(
        self,
        *,
        location: str | None,
        targets: Iterable[str] | None = None,
    ) -> None:
        perturbation_system.apply_arranged_meet(
            self._perturbation_service,
            location=location,
            targets=targets,
        )

    def utility_online(self, utility: str) -> bool:
        return economy_system.utility_online(self._economy_service, utility)

    def economy_settings(self) -> dict[str, float]:
        """Return the current economy configuration values."""

        return economy_system.economy_settings(self._economy_service)

    def active_price_spikes(self) -> dict[str, dict[str, object]]:
        """Return a summary of currently active price spike events."""

        return economy_system.active_price_spikes(self._economy_service)

    def utility_snapshot(self) -> dict[str, bool]:
        """Return on/off status for tracked utilities."""

        return economy_system.utility_snapshot(self._economy_service)


def build_console_service(
    world: WorldState,
    *,
    history_limit: int = _CONSOLE_HISTORY_LIMIT,
    buffer_limit: int = _CONSOLE_RESULT_BUFFER_LIMIT,
) -> ConsoleService:
    """Construct a console service bound to the given world."""

    return ConsoleService(
        world=world,
        history_limit=history_limit,
        buffer_limit=buffer_limit,
    )
