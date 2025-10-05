"""Snapshot persistence scaffolding."""

from __future__ import annotations

import json
import logging
import random
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from townlet.agents.models import Personality, personality_from_profile
from townlet.config import SimulationConfig
from townlet.lifecycle.manager import LifecycleManager
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.snapshots.migrations import (
    MigrationExecutionError,
    MigrationNotFoundError,
    migration_registry,
)
from townlet.utils import decode_rng_state, encode_rng, encode_rng_state
from townlet.world.grid import AgentSnapshot, InteractiveObject, WorldState

if TYPE_CHECKING:
    from townlet.stability.monitor import StabilityMonitor
    from townlet.stability.promotion import PromotionManager
    from townlet.telemetry.publisher import TelemetryPublisher


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
    agents: dict[str, dict[str, object]] = field(default_factory=dict)
    objects: dict[str, dict[str, object]] = field(default_factory=dict)
    queues: dict[str, object] = field(default_factory=dict)
    embeddings: dict[str, object] = field(default_factory=dict)
    employment: dict[str, object] = field(default_factory=dict)
    lifecycle: dict[str, object] = field(default_factory=dict)
    rng_state: str | None = None
    rng_streams: dict[str, str] = field(default_factory=dict)
    telemetry: dict[str, object] = field(default_factory=dict)
    console_buffer: list[object] = field(default_factory=list)
    perturbations: dict[str, object] = field(default_factory=dict)
    affordances: dict[str, object] = field(default_factory=dict)
    relationships: dict[str, dict[str, dict[str, float]]] = field(default_factory=dict)
    relationship_metrics: dict[str, object] = field(default_factory=dict)
    stability: dict[str, object] = field(default_factory=dict)
    promotion: dict[str, object] = field(default_factory=dict)
    identity: dict[str, object] = field(default_factory=dict)
    migrations: dict[str, object] = field(
        default_factory=lambda: {"applied": [], "required": []}
    )

    def as_dict(self) -> dict[str, object]:
        return {
            "config_id": self.config_id,
            "tick": self.tick,
            "agents": {
                agent_id: dict(payload) for agent_id, payload in self.agents.items()
            },
            "objects": {
                object_id: dict(payload) for object_id, payload in self.objects.items()
            },
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
                owner: {other: dict(values) for other, values in edges.items()}
                for owner, edges in self.relationships.items()
            },
            "relationship_metrics": dict(self.relationship_metrics),
            "stability": dict(self.stability),
            "promotion": dict(self.promotion),
            "identity": dict(self.identity),
            "migrations": dict(self.migrations),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> SnapshotState:
        if "config_id" not in payload or "tick" not in payload:
            raise ValueError("Snapshot payload missing required fields")
        config_id = str(payload["config_id"])
        tick = int(payload["tick"])
        agents_obj = payload.get("agents", {})
        if not isinstance(agents_obj, Mapping):
            raise ValueError("Snapshot agents field must be a mapping")
        agents: dict[str, dict[str, object]] = {
            str(agent_id): dict(data) for agent_id, data in agents_obj.items()
        }

        objects_obj = payload.get("objects", {})
        if not isinstance(objects_obj, Mapping):
            raise ValueError("Snapshot objects field must be a mapping")
        objects: dict[str, dict[str, object]] = {
            str(object_id): dict(data) for object_id, data in objects_obj.items()
        }

        queues_payload = payload.get("queues", {})
        if isinstance(queues_payload, Mapping):
            queues: dict[str, object] = dict(queues_payload)
        else:
            queues = {}

        embeddings_payload = payload.get("embeddings", {})
        if isinstance(embeddings_payload, Mapping):
            embeddings: dict[str, object] = dict(embeddings_payload)
        else:
            embeddings = {}

        employment_payload = payload.get("employment", {})
        if isinstance(employment_payload, Mapping):
            employment: dict[str, object] = dict(employment_payload)
        else:
            employment = {}

        lifecycle_payload = payload.get("lifecycle", {})
        if isinstance(lifecycle_payload, Mapping):
            lifecycle: dict[str, object] = dict(lifecycle_payload)
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
            rng_streams: dict[str, str] = {
                str(name): str(data)
                for name, data in rng_streams_payload.items()
                if isinstance(data, str)
            }
        else:
            rng_streams = {}
        if rng_state_str and "world" not in rng_streams:
            rng_streams["world"] = rng_state_str

        telemetry_payload = payload.get("telemetry", {})
        telemetry: dict[str, object] = (
            dict(telemetry_payload) if isinstance(telemetry_payload, Mapping) else {}
        )

        console_buffer_payload = payload.get("console_buffer", [])
        if isinstance(console_buffer_payload, list):
            console_buffer = list(console_buffer_payload)
        else:
            console_buffer = []

        perturbations_payload = payload.get("perturbations", {})
        if isinstance(perturbations_payload, Mapping):
            perturbations: dict[str, object] = dict(perturbations_payload)
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
            relationship_metrics: dict[str, object] = dict(metrics_payload)
        elif metrics_payload in (None,):
            relationship_metrics = {}
        else:
            raise ValueError("Snapshot relationship_metrics field must be a mapping if provided")
        affordances_payload = payload.get("affordances", {})
        if isinstance(affordances_payload, Mapping):
            affordances: dict[str, object] = {
                str(object_id): dict(data) if isinstance(data, Mapping) else {}
                for object_id, data in affordances_payload.items()
            }
        else:
            affordances = {}
        stability_payload = payload.get("stability", {})
        stability: dict[str, object] = (
            dict(stability_payload) if isinstance(stability_payload, Mapping) else {}
        )

        promotion_payload = payload.get("promotion", {})
        promotion: dict[str, object] = (
            dict(promotion_payload) if isinstance(promotion_payload, Mapping) else {}
        )

        identity_payload = payload.get("identity", {})
        if isinstance(identity_payload, Mapping):
            identity: dict[str, object] = dict(identity_payload)
        else:
            identity = {"config_id": config_id}

        migrations_payload = payload.get("migrations", {})
        if isinstance(migrations_payload, Mapping):
            migrations: dict[str, object] = dict(migrations_payload)
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
    telemetry: TelemetryPublisher | None = None,
    perturbations: PerturbationScheduler | None = None,
    stability: StabilityMonitor | None = None,
    promotion: PromotionManager | None = None,
    rng_streams: Mapping[str, random.Random] | None = None,
    identity: Mapping[str, object] | None = None,
) -> SnapshotState:
    """Capture the current world state into a snapshot payload."""

    agents_payload: dict[str, dict[str, object]] = {}
    for agent_id, snapshot in world.agents.items():
        agents_payload[agent_id] = {
            "position": list(snapshot.position),
            "needs": dict(snapshot.needs),
            "wallet": float(snapshot.wallet),
            "personality": {
                "extroversion": float(snapshot.personality.extroversion),
                "forgiveness": float(snapshot.personality.forgiveness),
                "ambition": float(snapshot.personality.ambition),
            },
            "personality_profile": snapshot.personality_profile,
            "inventory": dict(snapshot.inventory),
            "job_id": snapshot.job_id,
            "on_shift": bool(snapshot.on_shift),
            "lateness_counter": int(snapshot.lateness_counter),
            "last_late_tick": int(snapshot.last_late_tick),
            "shift_state": snapshot.shift_state,
            "late_ticks_today": int(snapshot.late_ticks_today),
            "attendance_ratio": float(snapshot.attendance_ratio),
            "absent_shifts_7d": int(snapshot.absent_shifts_7d),
            "wages_withheld": float(snapshot.wages_withheld),
            "exit_pending": bool(snapshot.exit_pending),
        }

    objects_payload: dict[str, dict[str, object]] = {}
    for object_id, obj in world.objects.items():
        objects_payload[object_id] = {
            "object_type": obj.object_type,
            "occupied_by": obj.occupied_by,
            "stock": dict(obj.stock),
        }

    queue_state = world.queue_manager.export_state()
    employment_payload = world.employment.export_state()
    employment_payload["exits_today"] = world.employment_exits_today()

    lifecycle_payload: dict[str, object] = {}
    if lifecycle is not None:
        lifecycle_payload = lifecycle.export_state()

    encoded_rngs: dict[str, str] = {}
    if rng_streams:
        for name, rng in rng_streams.items():
            if rng is None:
                continue
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

    telemetry_payload: dict[str, object] = {}
    console_buffer: list[object] = []
    if telemetry is not None:
        telemetry_payload = telemetry.export_state()
        console_buffer = telemetry.export_console_buffer()

    perturbations_payload = {}
    if perturbations is not None:
        perturbations_payload = perturbations.export_state()

    affordances_payload = world.affordance_runtime.export_state()

    stability_payload = {}
    if stability is not None:
        stability_payload = stability.export_state()

    promotion_payload = {}
    if promotion is not None:
        promotion_payload = promotion.export_state()

    identity_payload: dict[str, object] = {
        "config_id": config.config_id,
        "observation_variant": getattr(config, "observation_variant", None),
    }
    if identity:
        for key, value in identity.items():
            identity_payload[key] = value
    if identity_payload.get("observation_variant") is None:
        try:
            identity_payload["observation_variant"] = config.observation_variant
        except AttributeError:
            identity_payload.pop("observation_variant", None)

    migrations_payload = {"applied": [], "required": []}

    return SnapshotState(
        config_id=config.config_id,
        tick=world.tick,
        agents=agents_payload,
        objects=objects_payload,
        queues=queue_state,
        embeddings=world.embedding_allocator.export_state(),
        employment=employment_payload,
        lifecycle=lifecycle_payload,
        rng_state=rng_payload,
        rng_streams=encoded_rngs,
        telemetry=telemetry_payload,
        console_buffer=console_buffer,
        perturbations=perturbations_payload,
        affordances=affordances_payload,
        relationships=world.relationships_snapshot(),
        relationship_metrics=world.relationship_metrics_snapshot(),
        stability=stability_payload,
        promotion=promotion_payload,
        identity=identity_payload,
        migrations=migrations_payload,
    )


def apply_snapshot_to_world(
    world: WorldState,
    snapshot: SnapshotState,
    *,
    lifecycle: LifecycleManager | None = None,
) -> None:
    """Restore world, queue, embeddings, and lifecycle state from snapshot."""

    world.tick = snapshot.tick

    world.agents.clear()
    for agent_id, payload in snapshot.agents.items():
        position = tuple(payload.get("position", (0, 0)))
        needs = dict(payload.get("needs", {}))
        personality_data = payload.get("personality", {})
        fallback_personality = Personality(
            extroversion=float(personality_data.get("extroversion", 0.0)),
            forgiveness=float(personality_data.get("forgiveness", 0.0)),
            ambition=float(personality_data.get("ambition", 0.0)),
        )
        profile_field = payload.get("personality_profile")
        try:
            profile_name, resolved_personality = personality_from_profile(
                profile_field if isinstance(profile_field, str) else None
            )
        except KeyError:
            fallback_name = "custom" if profile_field else "balanced"
            logger.warning(
                "snapshot.unknown_personality_profile name=%s fallback=%s",
                profile_field,
                fallback_name,
            )
            profile_name = fallback_name
            resolved_personality = fallback_personality
        agent = AgentSnapshot(
            agent_id=agent_id,
            position=position,
            needs=needs,
            wallet=float(payload.get("wallet", 0.0)),
            personality=resolved_personality,
            personality_profile=profile_name,
            inventory=dict(payload.get("inventory", {})),
            job_id=payload.get("job_id"),
            on_shift=bool(payload.get("on_shift", False)),
            lateness_counter=int(payload.get("lateness_counter", 0)),
            last_late_tick=int(payload.get("last_late_tick", -1)),
            shift_state=str(payload.get("shift_state", "pre_shift")),
            late_ticks_today=int(payload.get("late_ticks_today", 0)),
            attendance_ratio=float(payload.get("attendance_ratio", 0.0)),
            absent_shifts_7d=int(payload.get("absent_shifts_7d", 0)),
            wages_withheld=float(payload.get("wages_withheld", 0.0)),
            exit_pending=bool(payload.get("exit_pending", False)),
        )
        world.agents[agent_id] = agent

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

    world._active_reservations.clear()
    world._running_affordances.clear()
    world._pending_events.clear()
    world._recent_meal_participants.clear()

    world.queue_manager.import_state(snapshot.queues)
    active_payload = snapshot.queues.get("active", {})
    if isinstance(active_payload, dict):
        world._active_reservations.update(
            {
                str(object_id): str(agent_id)
                for object_id, agent_id in active_payload.items()
            }
        )

    world.rebuild_spatial_index()

    world.embedding_allocator.import_state(snapshot.embeddings)

    affordance_state = snapshot.affordances
    if affordance_state:
        world.affordance_runtime.import_state(affordance_state)
    else:
        world.affordance_runtime.clear()
    if hasattr(world, "_queue_conflicts"):
        world._queue_conflicts.reset()  # pylint: disable=protected-access

    employment_payload = snapshot.employment
    world.employment.import_state(employment_payload)
    world.set_employment_exits_today(employment_payload.get("exits_today", 0))

    if lifecycle is not None:
        lifecycle.import_state(snapshot.lifecycle)

    rng_payload = snapshot.rng_streams.get("world") or snapshot.rng_state
    if rng_payload:
        state_tuple = decode_rng_state(rng_payload)
        if hasattr(world, "set_rng_state"):
            world.set_rng_state(state_tuple)
        else:
            random.setstate(state_tuple)

    world.load_relationship_snapshot(snapshot.relationships)
    world.load_relationship_metrics(snapshot.relationship_metrics)


def apply_snapshot_to_telemetry(
    telemetry: TelemetryPublisher,
    snapshot: SnapshotState,
) -> None:
    telemetry.import_state(snapshot.telemetry)
    telemetry.import_console_buffer(snapshot.console_buffer)
    if snapshot.relationship_metrics:
        telemetry.update_relationship_metrics(dict(snapshot.relationship_metrics))
    stability_metrics = snapshot.stability.get("latest_metrics")
    if isinstance(stability_metrics, Mapping):
        telemetry.record_stability_metrics(dict(stability_metrics))
    if snapshot.identity:
        telemetry.update_policy_identity(snapshot.identity)
    migrations_applied = (
        snapshot.migrations.get("applied")
        if isinstance(snapshot.migrations, Mapping)
        else None
    )
    if migrations_applied:
        telemetry.record_snapshot_migrations([str(item) for item in migrations_applied])


class SnapshotManager:
    """Handles save/load of simulation state and RNG streams."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).expanduser().resolve()

    def save(self, state: SnapshotState) -> Path:
        document = {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "state": state.as_dict(),
        }
        self.root.mkdir(parents=True, exist_ok=True)
        target = (self.root / f"snapshot-{state.tick}.json").resolve()
        if not target.is_relative_to(self.root):  # type: ignore[attr-defined]
            raise ValueError("Snapshot target escaped configured root")
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
    ) -> SnapshotState:
        resolved = Path(path).expanduser().resolve()
        if not resolved.is_relative_to(self.root):  # type: ignore[attr-defined]
            raise ValueError("Snapshot path outside manager root")
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
            if (
                parsed_snapshot
                and parsed_supported
                and parsed_snapshot > parsed_supported
            ):
                if not allow_downgrade:
                    raise ValueError(
                        "Snapshot schema version %s is newer than supported %s "
                        "(enable snapshot.guardrails.allow_downgrade to override)"
                        % (schema_version, SNAPSHOT_SCHEMA_VERSION)
                    )
            else:
                raise ValueError(
                    f"Unsupported snapshot schema version: {schema_version}"
                )
        state_payload = payload.get("state")
        if not isinstance(state_payload, Mapping):
            raise ValueError("Snapshot document missing state payload")
        state = SnapshotState.from_dict(state_payload)
        if state.config_id != config.config_id:
            if not allow_migration:
                if require_exact_config:
                    raise ValueError(
                        "Snapshot config_id mismatch: expected %s, got %s (auto-migration disabled)"
                        % (config.config_id, state.config_id)
                    )
                migrations_meta = (
                    state.migrations if isinstance(state.migrations, Mapping) else {}
                )
                state.migrations = {
                    "applied": list(migrations_meta.get("applied", [])),
                    "required": ["%s->%s" % (state.config_id, config.config_id)],
                }
                return state
            try:
                path = migration_registry.find_path(state.config_id, config.config_id)
            except MigrationNotFoundError as exc:
                raise ValueError(
                    "Snapshot config_id mismatch: expected %s, got %s"
                    % (config.config_id, state.config_id)
                ) from exc
            try:
                state, applied = migration_registry.apply_path(path, state, config)
            except MigrationExecutionError as exc:
                raise ValueError("Snapshot migration failed") from exc
            if state.config_id != config.config_id:
                raise ValueError(
                    "Snapshot migration chain did not reach target config_id %s (ended at %s)"
                    % (config.config_id, state.config_id)
                )
            migrations_meta = (
                state.migrations if isinstance(state.migrations, Mapping) else {}
            )
            applied_list = list(migrations_meta.get("applied", []))
            applied_list.extend(applied)
            state.migrations = {
                "applied": applied_list,
                "required": [],
            }
            logger.info("Applied snapshot migrations: %s", applied)
        identity_meta = dict(state.identity)
        identity_meta.setdefault("config_id", state.config_id)
        identity_cfg = getattr(getattr(config, "snapshot", None), "identity", None)
        if identity_cfg is not None:
            policy_hash = getattr(identity_cfg, "policy_hash", None)
            if policy_hash:
                identity_meta.setdefault("policy_hash", policy_hash)
            policy_artifact = getattr(identity_cfg, "policy_artifact", None)
            if policy_artifact is not None:
                identity_meta.setdefault("policy_artifact", str(policy_artifact))
            observation_variant = getattr(identity_cfg, "observation_variant", "infer")
            if observation_variant != "infer":
                identity_meta.setdefault("observation_variant", observation_variant)
            anneal_ratio = getattr(identity_cfg, "anneal_ratio", None)
            if anneal_ratio is not None:
                identity_meta.setdefault("anneal_ratio", anneal_ratio)
        state.identity = identity_meta
        return state
