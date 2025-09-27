"""Snapshot persistence scaffolding."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping, Optional, TYPE_CHECKING

from townlet.agents.models import Personality
from townlet.config import SimulationConfig
from townlet.lifecycle.manager import LifecycleManager
from townlet.scheduler.perturbations import PerturbationScheduler
from townlet.utils import decode_rng_state, encode_rng, encode_rng_state
from townlet.world.grid import AgentSnapshot, InteractiveObject, WorldState

if TYPE_CHECKING:
    from townlet.telemetry.publisher import TelemetryPublisher
    from townlet.stability.monitor import StabilityMonitor


SNAPSHOT_SCHEMA_VERSION = "1.4"


@dataclass
class SnapshotState:
    config_id: str
    tick: int
    agents: Dict[str, Dict[str, object]] = field(default_factory=dict)
    objects: Dict[str, Dict[str, object]] = field(default_factory=dict)
    queues: Dict[str, object] = field(default_factory=dict)
    embeddings: Dict[str, object] = field(default_factory=dict)
    employment: Dict[str, object] = field(default_factory=dict)
    lifecycle: Dict[str, object] = field(default_factory=dict)
    rng_state: Optional[str] = None
    rng_streams: Dict[str, str] = field(default_factory=dict)
    telemetry: Dict[str, object] = field(default_factory=dict)
    console_buffer: list[object] = field(default_factory=list)
    perturbations: Dict[str, object] = field(default_factory=dict)
    relationships: Dict[str, Dict[str, Dict[str, float]]] = field(default_factory=dict)
    stability: Dict[str, object] = field(default_factory=dict)
    identity: Dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, object]:
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
            "relationships": {
                owner: {
                    other: dict(values) for other, values in edges.items()
                }
                for owner, edges in self.relationships.items()
            },
            "stability": dict(self.stability),
            "identity": dict(self.identity),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "SnapshotState":
        if "config_id" not in payload or "tick" not in payload:
            raise ValueError("Snapshot payload missing required fields")
        config_id = str(payload["config_id"])
        tick = int(payload["tick"])
        agents_obj = payload.get("agents", {})
        if not isinstance(agents_obj, Mapping):
            raise ValueError("Snapshot agents field must be a mapping")
        agents: Dict[str, Dict[str, object]] = {
            str(agent_id): dict(data) for agent_id, data in agents_obj.items()
        }

        objects_obj = payload.get("objects", {})
        if not isinstance(objects_obj, Mapping):
            raise ValueError("Snapshot objects field must be a mapping")
        objects: Dict[str, Dict[str, object]] = {
            str(object_id): dict(data) for object_id, data in objects_obj.items()
        }

        queues_payload = payload.get("queues", {})
        if isinstance(queues_payload, Mapping):
            queues: Dict[str, object] = dict(queues_payload)
        else:
            queues = {}

        embeddings_payload = payload.get("embeddings", {})
        if isinstance(embeddings_payload, Mapping):
            embeddings: Dict[str, object] = dict(embeddings_payload)
        else:
            embeddings = {}

        employment_payload = payload.get("employment", {})
        if isinstance(employment_payload, Mapping):
            employment: Dict[str, object] = dict(employment_payload)
        else:
            employment = {}

        lifecycle_payload = payload.get("lifecycle", {})
        if isinstance(lifecycle_payload, Mapping):
            lifecycle: Dict[str, object] = dict(lifecycle_payload)
        else:
            lifecycle = {}

        rng_state = payload.get("rng_state")
        rng_state_str: Optional[str]
        if isinstance(rng_state, str):
            rng_state_str = rng_state
        else:
            rng_state_str = None

        rng_streams_payload = payload.get("rng_streams", {})
        if isinstance(rng_streams_payload, Mapping):
            rng_streams: Dict[str, str] = {
                str(name): str(data) for name, data in rng_streams_payload.items()
                if isinstance(data, str)
            }
        else:
            rng_streams = {}
        if rng_state_str and "world" not in rng_streams:
            rng_streams["world"] = rng_state_str

        telemetry_payload = payload.get("telemetry", {})
        telemetry: Dict[str, object] = (
            dict(telemetry_payload) if isinstance(telemetry_payload, Mapping) else {}
        )

        console_buffer_payload = payload.get("console_buffer", [])
        if isinstance(console_buffer_payload, list):
            console_buffer = list(console_buffer_payload)
        else:
            console_buffer = []

        perturbations_payload = payload.get("perturbations", {})
        if isinstance(perturbations_payload, Mapping):
            perturbations: Dict[str, object] = dict(perturbations_payload)
        else:
            perturbations = {}

        if "relationships" not in payload:
            raise ValueError("Snapshot payload missing relationships field")
        relationships_obj = payload["relationships"]
        if not isinstance(relationships_obj, Mapping):
            raise ValueError("Snapshot relationships field must be a mapping")
        relationships: Dict[str, Dict[str, Dict[str, float]]] = {}
        for owner, edges in relationships_obj.items():
            if not isinstance(edges, Mapping):
                raise ValueError("Relationship edges must be mappings")
            owner_id = str(owner)
            owner_edges: Dict[str, Dict[str, float]] = {}
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
        stability_payload = payload.get("stability", {})
        stability: Dict[str, object] = (
            dict(stability_payload) if isinstance(stability_payload, Mapping) else {}
        )

        identity_payload = payload.get("identity", {})
        if isinstance(identity_payload, Mapping):
            identity: Dict[str, object] = dict(identity_payload)
        else:
            identity = {"config_id": config_id}

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
            relationships=relationships,
            stability=stability,
            identity=identity,
        )


def snapshot_from_world(
    config: SimulationConfig,
    world: WorldState,
    *,
    lifecycle: Optional[LifecycleManager] = None,
    telemetry: Optional["TelemetryPublisher"] = None,
    perturbations: Optional[PerturbationScheduler] = None,
    stability: Optional["StabilityMonitor"] = None,
    rng_streams: Optional[Mapping[str, random.Random]] = None,
    identity: Optional[Mapping[str, object]] = None,
) -> SnapshotState:
    """Capture the current world state into a snapshot payload."""

    agents_payload: Dict[str, Dict[str, object]] = {}
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

    objects_payload: Dict[str, Dict[str, object]] = {}
    for object_id, obj in world.objects.items():
        objects_payload[object_id] = {
            "object_type": obj.object_type,
            "occupied_by": obj.occupied_by,
            "stock": dict(obj.stock),
        }

    queue_state = world.queue_manager.export_state()
    employment_payload = {
        "exit_queue": list(world._employment_exit_queue),
        "queue_timestamps": dict(world._employment_exit_queue_timestamps),
        "manual_exits": list(world._employment_manual_exits),
        "exits_today": world._employment_exits_today,
    }

    lifecycle_payload: Dict[str, object] = {}
    if lifecycle is not None:
        lifecycle_payload = lifecycle.export_state()

    encoded_rngs: Dict[str, str] = {}
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

    telemetry_payload: Dict[str, object] = {}
    console_buffer: list[object] = []
    if telemetry is not None:
        telemetry_payload = telemetry.export_state()
        console_buffer = telemetry.export_console_buffer()

    perturbations_payload = {}
    if perturbations is not None:
        perturbations_payload = perturbations.export_state()

    stability_payload = {}
    if stability is not None:
        stability_payload = stability.export_state()

    identity_payload: Dict[str, object] = {
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
        relationships=world.relationships_snapshot(),
        stability=stability_payload,
        identity=identity_payload,
    )


def apply_snapshot_to_world(
    world: WorldState,
    snapshot: SnapshotState,
    *,
    lifecycle: Optional[LifecycleManager] = None,
) -> None:
    """Restore world, queue, embeddings, and lifecycle state from snapshot."""

    world.tick = snapshot.tick

    world.agents.clear()
    for agent_id, payload in snapshot.agents.items():
        position = tuple(payload.get("position", (0, 0)))
        needs = dict(payload.get("needs", {}))
        personality_data = payload.get("personality", {})
        personality = Personality(
            extroversion=float(personality_data.get("extroversion", 0.0)),
            forgiveness=float(personality_data.get("forgiveness", 0.0)),
            ambition=float(personality_data.get("ambition", 0.0)),
        )
        agent = AgentSnapshot(
            agent_id=agent_id,
            position=position,
            needs=needs,
            wallet=float(payload.get("wallet", 0.0)),
            personality=personality,
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
            {str(object_id): str(agent_id) for object_id, agent_id in active_payload.items()}
        )

    world.embedding_allocator.import_state(snapshot.embeddings)

    employment_payload = snapshot.employment
    exit_queue = employment_payload.get("exit_queue", [])
    if isinstance(exit_queue, list):
        world._employment_exit_queue = [str(agent_id) for agent_id in exit_queue]
    timestamps = employment_payload.get("queue_timestamps", {})
    if isinstance(timestamps, Mapping):
        world._employment_exit_queue_timestamps = {
            str(agent_id): int(tick) for agent_id, tick in timestamps.items()
        }
    manual = employment_payload.get("manual_exits", [])
    if isinstance(manual, list):
        world._employment_manual_exits = {str(agent_id) for agent_id in manual}
    world._employment_exits_today = int(employment_payload.get("exits_today", 0))

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


def apply_snapshot_to_telemetry(
    telemetry: "TelemetryPublisher",
    snapshot: SnapshotState,
) -> None:
    telemetry.import_state(snapshot.telemetry)
    telemetry.import_console_buffer(snapshot.console_buffer)
    stability_metrics = snapshot.stability.get("latest_metrics")
    if isinstance(stability_metrics, Mapping):
        telemetry.record_stability_metrics(dict(stability_metrics))
    if snapshot.identity:
        telemetry.update_policy_identity(snapshot.identity)


class SnapshotManager:
    """Handles save/load of simulation state and RNG streams."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def save(self, state: SnapshotState) -> Path:
        document = {
            "schema_version": SNAPSHOT_SCHEMA_VERSION,
            "state": state.as_dict(),
        }
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.root / f"snapshot-{state.tick}.json"
        target.write_text(json.dumps(document, indent=2, sort_keys=True))
        return target

    def load(self, path: Path, config: SimulationConfig) -> SnapshotState:
        if not path.exists():
            raise FileNotFoundError(path)
        payload = json.loads(path.read_text())
        schema_version = payload.get("schema_version")
        if schema_version != SNAPSHOT_SCHEMA_VERSION:
            raise ValueError(
                f"Unsupported snapshot schema version: {schema_version}"
            )
        state_payload = payload.get("state")
        if not isinstance(state_payload, Mapping):
            raise ValueError("Snapshot document missing state payload")
        state = SnapshotState.from_dict(state_payload)
        if state.config_id != config.config_id:
            raise ValueError(
                "Snapshot config_id mismatch: expected %s, got %s"
                % (config.config_id, state.config_id)
            )
        return state
