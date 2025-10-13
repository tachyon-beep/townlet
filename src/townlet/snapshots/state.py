"""Snapshot persistence scaffolding."""

from __future__ import annotations

import json
import logging
import random
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from townlet.agents.models import Personality, personality_from_profile
from townlet.config import SimulationConfig
from townlet.core.interfaces import TelemetrySinkProtocol
from townlet.core.utils import is_stub_telemetry
from townlet.dto.telemetry import TelemetryEventDTO, TelemetryMetadata
from townlet.dto.world import (
    AffordanceSnapshot,
    AgentSummary,
    EmbeddingSnapshot,
    EmploymentSnapshot,
    IdentitySnapshot,
    LifecycleSnapshot,
    MigrationSnapshot,
    PerturbationSnapshot,
    PromotionSnapshot,
    QueueSnapshot,
    SimulationSnapshot,
    StabilitySnapshot,
    TelemetrySnapshot,
)
from townlet.lifecycle.manager import LifecycleManager
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.snapshots.migrations import (
    MigrationExecutionError,
    MigrationNotFoundError,
    migration_registry,
)
from townlet.utils import decode_rng_state, encode_rng, encode_rng_state
from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.core.runtime_adapter import ensure_world_adapter
from townlet.world.grid import InteractiveObject, WorldState
from townlet.world.rng import RngStreamManager

if TYPE_CHECKING:
    from townlet.stability.monitor import StabilityMonitor
    from townlet.stability.promotion import PromotionManager


SNAPSHOT_SCHEMA_VERSION = "1.6"


def _parse_version(value: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in value.split("."):
        if not chunk:
            return ()
        try:
            parts.append(int(chunk))
        except ValueError:
            return ()
    return tuple(parts)


logger = logging.getLogger(__name__)


@dataclass
class SnapshotState:
    config_id: str
    tick: int
    agents: dict[str, dict[str, Any]] = field(default_factory=dict)
    objects: dict[str, dict[str, Any]] = field(default_factory=dict)
    queues: dict[str, Any] = field(default_factory=dict)
    embeddings: dict[str, Any] = field(default_factory=dict)
    employment: dict[str, Any] = field(default_factory=dict)
    lifecycle: dict[str, Any] = field(default_factory=dict)
    rng_state: str | None = None
    rng_streams: dict[str, str] = field(default_factory=dict)
    telemetry: dict[str, Any] = field(default_factory=dict)
    console_buffer: list[Any] = field(default_factory=list)
    perturbations: dict[str, Any] = field(default_factory=dict)
    affordances: dict[str, Any] = field(default_factory=dict)
    relationships: dict[str, dict[str, dict[str, float]]] = field(default_factory=dict)
    relationship_metrics: dict[str, Any] = field(default_factory=dict)
    stability: dict[str, Any] = field(default_factory=dict)
    promotion: dict[str, Any] = field(default_factory=dict)
    identity: dict[str, Any] = field(default_factory=dict)
    migrations: dict[str, Any] = field(default_factory=lambda: {"applied": [], "required": []})

    def as_dict(self) -> dict[str, Any]:
        return {
            "config_id": self.config_id,
            "tick": self.tick,
            "agents": {agent_id: dict(payload) for agent_id, payload in self.agents.items()},
            "objects": {object_id: dict(payload) for object_id, payload in self.objects.items()},
            "queues": dict(self.queues),
            "embeddings": dict(self.embeddings),
            "employment": dict(self.employment),
            "lifecycle": dict(self.lifecycle),
            "rng_state": self.rng_state,
            "rng_streams": dict(self.rng_streams),
            "telemetry": dict(self.telemetry),
            "console_buffer": list(self.console_buffer),
            "perturbations": dict(self.perturbations),
            "affordances": dict(self.affordances),
            "relationships": {
                owner: {other: dict(values) for other, values in edges.items()} for owner, edges in self.relationships.items()
            },
            "relationship_metrics": dict(self.relationship_metrics),
            "stability": dict(self.stability),
            "promotion": dict(self.promotion),
            "identity": dict(self.identity),
            "migrations": dict(self.migrations),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> SnapshotState:
        if "config_id" not in payload or "tick" not in payload:
            raise ValueError("Snapshot payload missing required fields")
        config_id = str(payload["config_id"])
        tick_value = payload["tick"]
        if not isinstance(tick_value, (int, float, str)):
            raise TypeError("Snapshot tick must be numeric")
        tick = int(tick_value)
        agents_obj = payload.get("agents", {})
        if not isinstance(agents_obj, Mapping):
            raise ValueError("Snapshot agents field must be a mapping")
        agents: dict[str, dict[str, Any]] = {str(agent_id): dict(data) for agent_id, data in agents_obj.items()}

        objects_obj = payload.get("objects", {})
        if not isinstance(objects_obj, Mapping):
            raise ValueError("Snapshot objects field must be a mapping")
        objects: dict[str, dict[str, Any]] = {str(object_id): dict(data) for object_id, data in objects_obj.items()}

        queues_payload = payload.get("queues", {})
        if isinstance(queues_payload, Mapping):
            queues: dict[str, Any] = dict(queues_payload)
        else:
            queues = {}

        embeddings_payload = payload.get("embeddings", {})
        if isinstance(embeddings_payload, Mapping):
            embeddings: dict[str, Any] = dict(embeddings_payload)
        else:
            embeddings = {}

        employment_payload = payload.get("employment", {})
        if isinstance(employment_payload, Mapping):
            employment: dict[str, Any] = dict(employment_payload)
        else:
            employment = {}

        lifecycle_payload = payload.get("lifecycle", {})
        if isinstance(lifecycle_payload, Mapping):
            lifecycle: dict[str, Any] = dict(lifecycle_payload)
        else:
            lifecycle = {}

        rng_state = payload.get("rng_state")
        rng_state_str: str | None
        if isinstance(rng_state, str):
            rng_state_str = rng_state
        else:
            rng_state_str = None

        rng_streams_payload = payload.get("rng_streams", {})
        if isinstance(rng_streams_payload, Mapping):
            rng_streams: dict[str, str] = {str(name): str(data) for name, data in rng_streams_payload.items() if isinstance(data, str)}
        else:
            rng_streams = {}
        if rng_state_str and "world" not in rng_streams:
            rng_streams["world"] = rng_state_str

        telemetry_payload = payload.get("telemetry", {})
        telemetry: dict[str, Any] = dict(telemetry_payload) if isinstance(telemetry_payload, Mapping) else {}

        console_buffer_payload = payload.get("console_buffer", [])
        if isinstance(console_buffer_payload, list):
            console_buffer = list(console_buffer_payload)
        else:
            console_buffer = []

        perturbations_payload = payload.get("perturbations", {})
        if isinstance(perturbations_payload, Mapping):
            perturbations: dict[str, Any] = dict(perturbations_payload)
        else:
            perturbations = {}

        if "relationships" not in payload:
            raise ValueError("Snapshot payload missing relationships field")
        relationships_obj = payload["relationships"]
        if not isinstance(relationships_obj, Mapping):
            raise ValueError("Snapshot relationships field must be a mapping")
        relationships: dict[str, dict[str, dict[str, float]]] = {}
        for owner, edges in relationships_obj.items():
            if not isinstance(edges, Mapping):
                raise ValueError("Relationship edges must be mappings")
            owner_id = str(owner)
            owner_edges: dict[str, dict[str, float]] = {}
            for other, values in edges.items():
                if isinstance(values, Mapping):
                    owner_edges[str(other)] = {
                        "trust": float(values.get("trust", 0.0)),
                        "familiarity": float(values.get("familiarity", 0.0)),
                        "rivalry": float(values.get("rivalry", 0.0)),
                    }
                else:
                    # Backwards-compatibility for legacy scalar snapshots.
                    scalar = float(values)
                    owner_edges[str(other)] = {
                        "trust": scalar,
                        "familiarity": 0.0,
                        "rivalry": 0.0,
                    }
            relationships[owner_id] = owner_edges

        metrics_payload = payload.get("relationship_metrics", {})
        if isinstance(metrics_payload, Mapping):
            relationship_metrics: dict[str, Any] = dict(metrics_payload)
        elif metrics_payload in (None,):
            relationship_metrics = {}
        else:
            raise ValueError("Snapshot relationship_metrics field must be a mapping if provided")
        affordances_payload = payload.get("affordances", {})
        if isinstance(affordances_payload, Mapping):
            affordances: dict[str, Any] = {
                str(object_id): dict(data) if isinstance(data, Mapping) else {} for object_id, data in affordances_payload.items()
            }
        else:
            affordances = {}
        stability_payload = payload.get("stability", {})
        stability: dict[str, Any] = dict(stability_payload) if isinstance(stability_payload, Mapping) else {}

        promotion_payload = payload.get("promotion", {})
        promotion: dict[str, Any] = dict(promotion_payload) if isinstance(promotion_payload, Mapping) else {}

        identity_payload = payload.get("identity", {})
        if isinstance(identity_payload, Mapping):
            identity: dict[str, Any] = dict(identity_payload)
        else:
            identity = {"config_id": config_id}

        migrations_payload = payload.get("migrations", {})
        if isinstance(migrations_payload, Mapping):
            migrations: dict[str, Any] = dict(migrations_payload)
        else:
            migrations = {"applied": [], "required": []}

        return cls(
            config_id=config_id,
            tick=tick,
            agents=agents,
            objects=objects,
            queues=queues,
            embeddings=embeddings,
            employment=employment,
            lifecycle=lifecycle,
            rng_state=rng_state_str,
            rng_streams=rng_streams,
            telemetry=telemetry,
            console_buffer=console_buffer,
            perturbations=perturbations,
            affordances=affordances,
            relationships=relationships,
            relationship_metrics=relationship_metrics,
            stability=stability,
            promotion=promotion,
            identity=identity,
            migrations=migrations,
        )


def snapshot_from_world(
    config: SimulationConfig,
    world: WorldState,
    *,
    lifecycle: LifecycleManager | None = None,
    telemetry: TelemetrySinkProtocol | None = None,
    perturbations: PerturbationScheduler | None = None,
    stability: StabilityMonitor | None = None,
    promotion: PromotionManager | None = None,
    rng_streams: Mapping[str, random.Random] | None = None,
    identity: Mapping[str, Any] | None = None,
) -> SimulationSnapshot:
    """Capture the current world state into a SimulationSnapshot DTO."""

    adapter = ensure_world_adapter(world)

    # Build AgentSummary DTOs
    agents: dict[str, AgentSummary] = {}
    for agent_id, agent_snapshot in adapter.agent_snapshots_view().items():
        agents[agent_id] = AgentSummary(
            agent_id=agent_id,
            position=agent_snapshot.position,
            needs=dict(agent_snapshot.needs),
            wallet=float(agent_snapshot.wallet),
            personality={
                "extroversion": float(agent_snapshot.personality.extroversion),
                "forgiveness": float(agent_snapshot.personality.forgiveness),
                "ambition": float(agent_snapshot.personality.ambition),
            },
            personality_profile=agent_snapshot.personality_profile,
            inventory=dict(agent_snapshot.inventory),
            job_id=agent_snapshot.job_id,
            on_shift=bool(agent_snapshot.on_shift),
            lateness_counter=int(agent_snapshot.lateness_counter),
            last_late_tick=int(agent_snapshot.last_late_tick),
            shift_state=agent_snapshot.shift_state,
            late_ticks_today=int(agent_snapshot.late_ticks_today),
            attendance_ratio=float(agent_snapshot.attendance_ratio),
            absent_shifts_7d=int(agent_snapshot.absent_shifts_7d),
            wages_withheld=float(agent_snapshot.wages_withheld),
            exit_pending=bool(agent_snapshot.exit_pending),
        )

    # Build objects payload (still dict-based for now)
    objects_payload: dict[str, dict[str, Any]] = {}
    for object_id, obj in adapter.objects_snapshot().items():
        objects_payload[object_id] = {
            "object_type": obj.get("object_type"),
            "occupied_by": obj.get("occupied_by"),
            "stock": dict(obj.get("stock", {})),
        }

    # Build QueueSnapshot DTO
    queue_dict = adapter.queue_manager.export_state()
    active_raw = queue_dict.get("active", {})
    queues_raw = queue_dict.get("queues", {})
    cooldowns_raw = queue_dict.get("cooldowns", [])
    stall_counts_raw = queue_dict.get("stall_counts", {})
    queues_snapshot = QueueSnapshot(
        active=dict(active_raw) if isinstance(active_raw, dict) else {},
        queues=dict(queues_raw) if isinstance(queues_raw, dict) else {},
        cooldowns=list(cooldowns_raw) if isinstance(cooldowns_raw, list) else [],
        stall_counts=dict(stall_counts_raw) if isinstance(stall_counts_raw, dict) else {},
    )

    # Build EmploymentSnapshot DTO
    employment_dict = world.employment.export_state()
    exit_queue_raw = employment_dict.get("exit_queue", [])
    queue_timestamps_raw = employment_dict.get("queue_timestamps", {})
    manual_exits_raw = employment_dict.get("manual_exits", [])
    exits_today_raw = employment_dict.get("exits_today", 0)
    employment_snapshot = EmploymentSnapshot(
        exit_queue=list(exit_queue_raw) if isinstance(exit_queue_raw, list) else [],
        queue_timestamps=dict(queue_timestamps_raw) if isinstance(queue_timestamps_raw, dict) else {},
        manual_exits=list(manual_exits_raw) if isinstance(manual_exits_raw, list) else [],
        exits_today=int(exits_today_raw) if isinstance(exits_today_raw, (int, float)) else 0,
    )

    # Build LifecycleSnapshot DTO
    lifecycle_snapshot = LifecycleSnapshot()
    if lifecycle is not None:
        lifecycle_dict = lifecycle.export_state()
        exits_today_raw = lifecycle_dict.get("exits_today", 0)
        employment_day_raw = lifecycle_dict.get("employment_day", -1)
        lifecycle_snapshot = LifecycleSnapshot(
            exits_today=int(exits_today_raw) if isinstance(exits_today_raw, (int, float)) else 0,
            employment_day=int(employment_day_raw) if isinstance(employment_day_raw, (int, float)) else -1,
        )

    # Encode RNG streams
    encoded_rngs: dict[str, str] = {}
    if rng_streams:
        for name, rng in rng_streams.items():
            encoded_rngs[str(name)] = encode_rng(rng)
    else:
        if hasattr(world, "get_rng_state"):
            try:
                encoded_rngs["world"] = encode_rng_state(world.get_rng_state())
            except Exception:  # pragma: no cover - defensive fallback
                encoded_rngs["world"] = encode_rng_state(random.getstate())
        else:
            encoded_rngs["world"] = encode_rng_state(random.getstate())

    rng_payload = encoded_rngs.get("world")

    # Build TelemetrySnapshot DTO
    console_buffer: list[Any] = []
    telemetry_snapshot = TelemetrySnapshot()
    if telemetry is not None:
        if is_stub_telemetry(telemetry):
            logger.warning("snapshot_capture_stub_telemetry message='Telemetry sink in stub mode; export payload will be empty.'")
        else:
            if hasattr(telemetry, "export_state"):
                telemetry_dict = telemetry.export_state()
                telemetry_snapshot = TelemetrySnapshot(
                    queue_metrics=dict(telemetry_dict.get("queue_metrics", {})),
                    embedding_metrics=dict(telemetry_dict.get("embedding_metrics", {})),
                    conflict_snapshot=dict(telemetry_dict.get("conflict_snapshot", {})),
                    relationship_metrics=dict(telemetry_dict.get("relationship_metrics", {})),
                    job_snapshot=dict(telemetry_dict.get("job_snapshot", {})),
                    economy_snapshot=dict(telemetry_dict.get("economy_snapshot", {})),
                    relationship_snapshot=dict(telemetry_dict.get("relationship_snapshot", {})),
                )
            # Capture the console buffer (pending commands) without draining it
            if hasattr(telemetry, "_latest_console_events"):
                console_buffer = list(telemetry._latest_console_events)

    # Build PerturbationSnapshot DTO
    perturbations_snapshot = PerturbationSnapshot()
    if perturbations is not None:
        pert_dict = perturbations.export_state()
        perturbations_snapshot = PerturbationSnapshot(
            pending=list(pert_dict.get("pending", [])),
            active=dict(pert_dict.get("active", {})),
        )

    # Build AffordanceSnapshot DTO
    affordances_dict = world.affordance_runtime.export_state()
    affordances_snapshot = AffordanceSnapshot(
        running=cast(dict[str, dict[str, Any]], dict(affordances_dict)),
    )

    # Build EmbeddingSnapshot DTO
    embeddings_dict = world.embedding_allocator.export_state()
    assignments_raw = embeddings_dict.get("assignments", {})
    available_raw = embeddings_dict.get("available", [])
    embeddings_snapshot = EmbeddingSnapshot(
        assignments=dict(assignments_raw) if isinstance(assignments_raw, dict) else {},
        available=list(available_raw) if isinstance(available_raw, list) else [],
    )

    # Build StabilitySnapshot DTO
    stability_snapshot = StabilitySnapshot()
    if stability is not None:
        stability_dict = stability.export_state()
        starvation_streaks_raw = stability_dict.get("starvation_streaks", {})
        starvation_active_raw = stability_dict.get("starvation_active", [])
        starvation_incidents_raw = stability_dict.get("starvation_incidents", [])
        latest_metrics_raw = stability_dict.get("latest_metrics", {})
        stability_snapshot = StabilitySnapshot(
            starvation_streaks=dict(starvation_streaks_raw) if isinstance(starvation_streaks_raw, dict) else {},
            starvation_active=list(starvation_active_raw) if isinstance(starvation_active_raw, list) else [],
            starvation_incidents=list(starvation_incidents_raw) if isinstance(starvation_incidents_raw, list) else [],
            latest_metrics=dict(latest_metrics_raw) if isinstance(latest_metrics_raw, dict) else {},
        )

    # Build PromotionSnapshot DTO
    promotion_snapshot = PromotionSnapshot()
    if promotion is not None:
        promotion_dict = promotion.export_state()
        state_raw = promotion_dict.get("state", "monitoring")
        pass_streak_raw = promotion_dict.get("pass_streak", 0)
        required_passes_raw = promotion_dict.get("required_passes", 2)
        candidate_ready_raw = promotion_dict.get("candidate_ready", False)
        promotion_snapshot = PromotionSnapshot(
            state=str(state_raw) if state_raw else "monitoring",
            pass_streak=int(pass_streak_raw) if isinstance(pass_streak_raw, (int, float)) else 0,
            required_passes=int(required_passes_raw) if isinstance(required_passes_raw, (int, float)) else 2,
            candidate_ready=bool(candidate_ready_raw),
        )

    # Build IdentitySnapshot DTO
    identity_dict: dict[str, Any] = {
        "config_id": config.config_id,
        "observation_variant": getattr(config, "observation_variant", None),
    }
    if identity:
        for key, value in identity.items():
            identity_dict[key] = value
    if identity_dict.get("observation_variant") is None:
        try:
            identity_dict["observation_variant"] = config.observation_variant
        except AttributeError:
            identity_dict.pop("observation_variant", None)

    identity_snapshot = IdentitySnapshot(
        config_id=identity_dict["config_id"],
        policy_hash=identity_dict.get("policy_hash"),
        observation_variant=identity_dict.get("observation_variant"),
        anneal_ratio=identity_dict.get("anneal_ratio"),
        policy_artifact=identity_dict.get("policy_artifact"),
    )

    # Build MigrationSnapshot DTO
    migrations_snapshot = MigrationSnapshot(
        applied=[],
        required=[],
    )

    # Add context seed to RNG streams if present
    context_seed = None
    world_context = getattr(world, "context", None)
    if world_context is not None:
        rng_manager = getattr(world_context, "rng_manager", None)
        base_seed = getattr(rng_manager, "base_seed", None)
        if base_seed is not None:
            context_seed = str(int(base_seed))
            encoded_rngs["context_seed"] = context_seed

    # Build SimulationSnapshot DTO
    snapshot = SimulationSnapshot(
        config_id=config.config_id,
        tick=world.tick,
        ticks_per_day=getattr(config, "ticks_per_day", 1440),
        agents=agents,
        objects=objects_payload,
        queues=queues_snapshot,
        employment=employment_snapshot,
        relationships={
            owner: {other: dict(values) for other, values in relations.items()}
            for owner, relations in adapter.relationships_snapshot().items()
        },
        relationship_metrics=dict(adapter.relationship_metrics_snapshot()),
        lifecycle=lifecycle_snapshot,
        perturbations=perturbations_snapshot,
        affordances=affordances_snapshot,
        embeddings=embeddings_snapshot,
        stability=stability_snapshot,
        promotion=promotion_snapshot,
        telemetry=telemetry_snapshot,
        rng_state=rng_payload,
        rng_streams=encoded_rngs,
        console_buffer=console_buffer,
        identity=identity_snapshot,
        migrations=migrations_snapshot,
    )

    return snapshot


def apply_snapshot_to_world(
    world: WorldState,
    snapshot: SimulationSnapshot,
    *,
    lifecycle: LifecycleManager | None = None,
) -> None:
    """Restore world, queue, embeddings, and lifecycle state from SimulationSnapshot."""

    world.tick = snapshot.tick

    # Restore agents from AgentSummary DTOs
    world.agents.clear()
    for agent_id, agent_dto in snapshot.agents.items():
        # Handle personality - either from personality dict or profile
        personality_data = agent_dto.personality if isinstance(agent_dto.personality, dict) else {}
        fallback_personality = Personality(
            extroversion=float(personality_data.get("extroversion", 0.0)),
            forgiveness=float(personality_data.get("forgiveness", 0.0)),
            ambition=float(personality_data.get("ambition", 0.0)),
        )
        try:
            profile_name, resolved_personality = personality_from_profile(agent_dto.personality_profile)
        except KeyError:
            fallback_name = agent_dto.personality_profile if agent_dto.personality_profile else "balanced"
            logger.warning(
                "snapshot.unknown_personality_profile name=%s fallback=%s",
                agent_dto.personality_profile,
                fallback_name,
            )
            profile_name = fallback_name
            resolved_personality = fallback_personality

        agent = AgentSnapshot(
            agent_id=agent_id,
            position=agent_dto.position,
            needs=dict(agent_dto.needs),
            wallet=float(agent_dto.wallet),
            personality=resolved_personality,
            personality_profile=profile_name,
            inventory=dict(agent_dto.inventory),
            job_id=agent_dto.job_id,
            on_shift=bool(agent_dto.on_shift),
            lateness_counter=int(agent_dto.lateness_counter),
            last_late_tick=int(agent_dto.last_late_tick),
            shift_state=str(agent_dto.shift_state),
            late_ticks_today=int(agent_dto.late_ticks_today),
            attendance_ratio=float(agent_dto.attendance_ratio),
            absent_shifts_7d=int(agent_dto.absent_shifts_7d),
            wages_withheld=float(agent_dto.wages_withheld),
            exit_pending=bool(agent_dto.exit_pending),
        )
        world.agents[agent_id] = agent

    # Restore objects (still dict-based)
    world.objects.clear()
    world.store_stock.clear()
    for object_id, payload in snapshot.objects.items():
        obj = InteractiveObject(
            object_id=object_id,
            object_type=str(payload.get("object_type", "")),
            occupied_by=payload.get("occupied_by"),
            stock=dict(payload.get("stock", {})),
        )
        world.objects[object_id] = obj
        world.store_stock[object_id] = obj.stock

    # Clear internal state
    world._active_reservations.clear()
    world._running_affordances.clear()
    world._pending_events.clear()
    world._recent_meal_participants.clear()

    # Restore queue state from QueueSnapshot DTO
    queue_dict = snapshot.queues.model_dump()
    world.queue_manager.import_state(queue_dict)
    active_payload = queue_dict.get("active", {})
    if isinstance(active_payload, dict):
        world._active_reservations.update({str(object_id): str(agent_id) for object_id, agent_id in active_payload.items()})

    world.rebuild_spatial_index()

    # Restore embedding state from EmbeddingSnapshot DTO
    embeddings_dict = snapshot.embeddings.model_dump()
    world.embedding_allocator.import_state(embeddings_dict)

    # Restore affordance state from AffordanceSnapshot DTO
    affordances_dict = snapshot.affordances.model_dump()
    affordance_running = affordances_dict.get("running", {})
    if affordance_running:
        world.affordance_runtime.import_state(affordance_running)
    else:
        world.affordance_runtime.clear()
    if hasattr(world, "_queue_conflicts"):
        world._queue_conflicts.reset()  # pylint: disable=protected-access

    # Restore employment state from EmploymentSnapshot DTO
    employment_dict = snapshot.employment.model_dump()
    world.employment.import_state(employment_dict)
    world.set_employment_exits_today(employment_dict.get("exits_today", 0))

    # Restore lifecycle state from LifecycleSnapshot DTO
    if lifecycle is not None:
        lifecycle_dict = snapshot.lifecycle.model_dump()
        lifecycle.import_state(lifecycle_dict)

    # Restore RNG streams
    context_seed_raw = snapshot.rng_streams.get("context_seed")
    rng_payload = snapshot.rng_streams.get("world") or snapshot.rng_state
    if rng_payload:
        state_tuple = decode_rng_state(rng_payload)
        if hasattr(world, "set_rng_state"):
            world.set_rng_state(state_tuple)
        else:
            random.setstate(state_tuple)
    if context_seed_raw is not None:
        try:
            seed_value = int(context_seed_raw)
        except (TypeError, ValueError):
            seed_value = None
        if seed_value is not None:
            context = getattr(world, "context", None)
            if context is not None:
                context.rng_manager = RngStreamManager.from_seed(seed_value)

    # Restore relationships
    world.load_relationship_snapshot(snapshot.relationships)
    world.load_relationship_metrics(snapshot.relationship_metrics)


def apply_snapshot_to_telemetry(
    telemetry: TelemetrySinkProtocol,
    snapshot: SimulationSnapshot,
) -> None:
    """Restore telemetry state from SimulationSnapshot."""
    if is_stub_telemetry(telemetry):
        logger.warning("snapshot_restore_stub_telemetry message='Telemetry sink in stub mode; snapshot state not fully restored.'")
        return

    # Restore telemetry state from TelemetrySnapshot DTO
    if hasattr(telemetry, "import_state"):
        telemetry_dict = snapshot.telemetry.model_dump()
        telemetry.import_state(telemetry_dict)
    if hasattr(telemetry, "import_console_buffer"):
        telemetry.import_console_buffer(snapshot.console_buffer)
    if snapshot.relationship_metrics and hasattr(telemetry, "update_relationship_metrics"):
        telemetry.update_relationship_metrics(dict(snapshot.relationship_metrics))

    # Emit stability metrics from StabilitySnapshot DTO
    stability_metrics = snapshot.stability.latest_metrics
    if stability_metrics:
        emit = getattr(telemetry, "emit_event", None)
        if callable(emit):
            event = TelemetryEventDTO(
                event_type="stability.metrics",
                tick=snapshot.tick,
                payload=dict(stability_metrics),
                metadata=TelemetryMetadata(),
            )
            emit(event)

    # Update policy identity from IdentitySnapshot DTO
    if hasattr(telemetry, "update_policy_identity"):
        identity_dict = snapshot.identity.model_dump()
        telemetry.update_policy_identity(identity_dict)

    # Emit migration events from MigrationSnapshot DTO
    migrations_applied = snapshot.migrations.applied
    if migrations_applied:
        applied_list = [str(item) for item in migrations_applied]
        if applied_list:
            emit = getattr(telemetry, "emit_event", None)
            if callable(emit):
                event = TelemetryEventDTO(
                    event_type="telemetry.snapshot.migrations",
                    tick=snapshot.tick,
                    payload={"applied": applied_list},
                    metadata=TelemetryMetadata(),
                )
                emit(event)


class SnapshotManager:
    """Handles save/load of simulation state and RNG streams."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).expanduser().resolve()

    def save(self, state: SimulationSnapshot) -> Path:
        """Save SimulationSnapshot to JSON using Pydantic serialization."""
        document = {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "state": state.model_dump(),
        }
        self.root.mkdir(parents=True, exist_ok=True)
        target = (self.root / f"snapshot-{state.tick}.json").resolve()
        try:
            target.relative_to(self.root)
        except ValueError:
            raise ValueError("Snapshot target escaped configured root") from None
        target.write_text(json.dumps(document, indent=2, sort_keys=True))
        return target

    def load(
        self,
        path: Path,
        config: SimulationConfig,
        *,
        allow_migration: bool | None = None,
        allow_downgrade: bool | None = None,
        require_exact_config: bool | None = None,
    ) -> SimulationSnapshot:
        """Load SimulationSnapshot from JSON using Pydantic deserialization."""
        resolved = Path(path).expanduser().resolve()
        try:
            resolved.relative_to(self.root)
        except ValueError:
            raise ValueError("Snapshot path outside manager root") from None
        if not resolved.exists():
            raise FileNotFoundError(resolved)
        payload = json.loads(resolved.read_text())
        schema_version = payload.get("schema_version")
        snapshot_cfg = getattr(config, "snapshot", None)
        migrations_cfg = getattr(snapshot_cfg, "migrations", None)
        guardrails_cfg = getattr(snapshot_cfg, "guardrails", None)
        if allow_migration is None:
            allow_migration = getattr(migrations_cfg, "auto_apply", True)
        if allow_downgrade is None:
            allow_downgrade = getattr(guardrails_cfg, "allow_downgrade", False)
        if require_exact_config is None:
            require_exact_config = getattr(guardrails_cfg, "require_exact_config", True)

        if not isinstance(schema_version, str):
            raise ValueError("Snapshot missing schema_version string")

        if schema_version != SNAPSHOT_SCHEMA_VERSION:
            parsed_snapshot = _parse_version(schema_version)
            parsed_supported = _parse_version(SNAPSHOT_SCHEMA_VERSION)
            if parsed_snapshot and parsed_supported and parsed_snapshot > parsed_supported:
                if not allow_downgrade:
                    raise ValueError(
                        "Snapshot schema version "
                        f"{schema_version} is newer than supported {SNAPSHOT_SCHEMA_VERSION} "
                        "(enable snapshot.guardrails.allow_downgrade to override)"
                    )
            else:
                raise ValueError(f"Unsupported snapshot schema version: {schema_version}")
        state_payload = payload.get("state")
        if not isinstance(state_payload, Mapping):
            raise ValueError("Snapshot document missing state payload")

        # Deserialize using Pydantic
        state = SimulationSnapshot.model_validate(state_payload)

        # Handle config_id mismatch and migrations
        if state.config_id != config.config_id:
            if not allow_migration:
                if require_exact_config:
                    raise ValueError(
                        f"Snapshot config_id mismatch: expected {config.config_id}, got {state.config_id} (auto-migration disabled)"
                    )
                # Update migrations DTO to indicate required migration
                state.migrations = MigrationSnapshot(
                    applied=list(state.migrations.applied),
                    required=[f"{state.config_id}->{config.config_id}"],
                )
                return state
            # For actual migration, convert to legacy SnapshotState temporarily
            # TODO: Update migration system to work with SimulationSnapshot in later phase
            legacy_state = SnapshotState.from_dict(state_payload)
            try:
                migration_path = migration_registry.find_path(legacy_state.config_id, config.config_id)
            except MigrationNotFoundError as exc:
                raise ValueError(f"Snapshot config_id mismatch: expected {config.config_id}, got {legacy_state.config_id}") from exc
            try:
                legacy_state, applied = migration_registry.apply_path(migration_path, legacy_state, config)
            except MigrationExecutionError as exc:
                raise ValueError("Snapshot migration failed") from exc
            if legacy_state.config_id != config.config_id:
                raise ValueError(
                    f"Snapshot migration chain did not reach target config_id {config.config_id} "
                    f"(ended at {legacy_state.config_id})"
                )
            # Convert back to SimulationSnapshot after migration
            state = SimulationSnapshot.model_validate(legacy_state.as_dict())
            # Update migrations metadata
            applied_list = list(state.migrations.applied)
            applied_list.extend(applied)
            state.migrations = MigrationSnapshot(
                applied=applied_list,
                required=[],
            )
            logger.info("Applied snapshot migrations: %s", applied)

        # Enrich identity metadata from config
        identity_dict = state.identity.model_dump()
        identity_dict.setdefault("config_id", state.config_id)
        identity_cfg = getattr(getattr(config, "snapshot", None), "identity", None)
        if identity_cfg is not None:
            policy_hash = getattr(identity_cfg, "policy_hash", None)
            if policy_hash:
                identity_dict.setdefault("policy_hash", policy_hash)
            policy_artifact = getattr(identity_cfg, "policy_artifact", None)
            if policy_artifact is not None:
                identity_dict.setdefault("policy_artifact", str(policy_artifact))
            observation_variant = getattr(identity_cfg, "observation_variant", "infer")
            if observation_variant != "infer":
                identity_dict.setdefault("observation_variant", observation_variant)
            anneal_ratio = getattr(identity_cfg, "anneal_ratio", None)
            if anneal_ratio is not None:
                identity_dict.setdefault("anneal_ratio", anneal_ratio)

        # Rebuild IdentitySnapshot DTO with enriched metadata
        state.identity = IdentitySnapshot(
            config_id=identity_dict["config_id"],
            policy_hash=identity_dict.get("policy_hash"),
            observation_variant=identity_dict.get("observation_variant"),
            anneal_ratio=identity_dict.get("anneal_ratio"),
            policy_artifact=identity_dict.get("policy_artifact"),
        )
        return state
