"""Observation encoding across variants."""
from __future__ import annotations

import hashlib
from math import cos, sin, tau
from typing import Dict, Iterable, List, Tuple, TYPE_CHECKING

import numpy as np

from townlet.config import ObservationVariant, SimulationConfig

if TYPE_CHECKING:
    from townlet.world.grid import AgentSnapshot, WorldState


class ObservationBuilder:
    """Constructs per-agent observation payloads."""

    MAP_CHANNELS = ("self", "agents", "objects", "reservations")
    SHIFT_STATES = ("pre_shift", "on_time", "late", "absent", "post_shift")

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.variant: ObservationVariant = config.observation_variant
        self.hybrid_cfg = config.observations_config.hybrid
        self.social_cfg = config.observations_config.social_snippet
        self._shift_feature_map = {
            "pre_shift": "shift_pre",
            "on_time": "shift_on_time",
            "late": "shift_late",
            "absent": "shift_absent",
            "post_shift": "shift_post",
        }
        base_feature_names = [
            "need_hunger",
            "need_hygiene",
            "need_energy",
            "wallet",
            "lateness_counter",
            "on_shift",
            "time_sin",
            "time_cos",
            "attendance_ratio",
            "wages_withheld",
            *self._shift_feature_map.values(),
            "embedding_slot_norm",
            "ctx_reset_flag",
            "episode_progress",
            "rivalry_max",
            "rivalry_avoid_count",
        ]

        self._social_slots = max(0, self.social_cfg.top_friends + self.social_cfg.top_rivals)
        if self._social_slots and self.variant != "hybrid":
            raise ValueError("Social snippet is only supported for hybrid observations")
        if self._social_slots and self.config.features.stages.relationships == "OFF":
            raise ValueError(
                "Social snippet requires relationships stage enabled"
            )

        self._social_slot_dim = self.social_cfg.embed_dim + 3  # id embedding + trust/fam/rivalry
        social_feature_names: List[str] = []
        for slot_index in range(self._social_slots):
            for component_index in range(self._social_slot_dim):
                social_feature_names.append(f"social_slot{slot_index}_d{component_index}")

        if self.social_cfg.include_aggregates:
            self._social_aggregate_names = [
                "social_trust_mean",
                "social_trust_max",
                "social_rivalry_mean",
                "social_rivalry_max",
            ]
        else:
            self._social_aggregate_names = []
        social_feature_names.extend(self._social_aggregate_names)

        self._feature_names = base_feature_names + social_feature_names
        self._feature_index = {name: idx for idx, name in enumerate(self._feature_names)}
        self._base_feature_len = len(base_feature_names)
        self._social_vector_length = len(social_feature_names)
        self._social_slice = slice(
            self._base_feature_len,
            self._base_feature_len + self._social_vector_length,
        )

        self._empty_social_vector = np.zeros(self._social_vector_length, dtype=np.float32)

    def build_batch(self, world: "WorldState", terminated: Dict[str, bool]) -> Dict[str, Dict[str, np.ndarray]]:
        """Return a mapping from agent_id to observation payloads."""
        observations: Dict[str, Dict[str, np.ndarray]] = {}
        snapshots = world.snapshot()
        for agent_id, snapshot in snapshots.items():
            slot = world.embedding_allocator.allocate(agent_id, world.tick)
            obs = self._build_single(world, snapshot, slot)
            if terminated.get(agent_id):
                obs["features"][self._feature_index["ctx_reset_flag"]] = 1.0
                world.embedding_allocator.release(agent_id, world.tick)
            observations[agent_id] = obs
        return observations

    def _build_single(
        self,
        world: "WorldState",
        snapshot: "AgentSnapshot",
        slot: int,
    ) -> Dict[str, np.ndarray | Dict[str, object]]:
        if self.variant != "hybrid":
            return {
                "map": np.zeros((1, 1, 1), dtype=np.float32),
                "features": np.zeros(1, dtype=np.float32),
                "metadata": {"variant": self.variant},
            }

        window = self.hybrid_cfg.local_window
        radius = window // 2
        map_tensor = np.zeros((len(self.MAP_CHANNELS), window, window), dtype=np.float32)

        center = radius
        map_tensor[0, center, center] = 1.0

        cx, cy = snapshot.position
        for other in world.agents.values():
            if other.agent_id == snapshot.agent_id:
                continue
            ox, oy = other.position
            dx = ox - cx
            dy = oy - cy
            if abs(dx) <= radius and abs(dy) <= radius:
                map_tensor[1, center + dy, center + dx] = 1.0

        features = np.zeros(len(self._feature_names), dtype=np.float32)

        features[self._feature_index["need_hunger"]] = snapshot.needs.get("hunger", 0.0)
        features[self._feature_index["need_hygiene"]] = snapshot.needs.get("hygiene", 0.0)
        features[self._feature_index["need_energy"]] = snapshot.needs.get("energy", 0.0)
        features[self._feature_index["wallet"]] = float(snapshot.wallet)
        features[self._feature_index["lateness_counter"]] = float(snapshot.lateness_counter)
        features[self._feature_index["on_shift"]] = 1.0 if snapshot.on_shift else 0.0

        ticks_per_day = self.hybrid_cfg.time_ticks_per_day
        phase = (world.tick % ticks_per_day) / ticks_per_day
        features[self._feature_index["time_sin"]] = sin(tau * phase)
        features[self._feature_index["time_cos"]] = cos(tau * phase)

        features[self._feature_index["attendance_ratio"]] = float(snapshot.attendance_ratio)
        features[self._feature_index["wages_withheld"]] = float(snapshot.wages_withheld)

        shift_state = snapshot.shift_state if snapshot.shift_state in self.SHIFT_STATES else "pre_shift"
        for name, feature_name in self._shift_feature_map.items():
            features[self._feature_index[feature_name]] = 1.0 if name == shift_state else 0.0

        max_slots = self.config.embedding_allocator.max_slots
        features[self._feature_index["embedding_slot_norm"]] = float(slot) / float(max_slots)

        features[self._feature_index["episode_progress"]] = 0.0  # Placeholder until episode tracking exists.

        top_rivals = world.rivalry_top(snapshot.agent_id, limit=self.config.conflict.rivalry.max_edges)
        max_rivalry = top_rivals[0][1] if top_rivals else 0.0
        avoid_threshold = self.config.conflict.rivalry.avoid_threshold
        avoid_count = sum(1 for _, value in top_rivals if value >= avoid_threshold)
        features[self._feature_index["rivalry_max"]] = float(max_rivalry)
        features[self._feature_index["rivalry_avoid_count"]] = float(avoid_count)

        if self._social_vector_length:
            social_vector = self._build_social_vector(world, snapshot)
            features[self._social_slice] = social_vector

        metadata = {
            "variant": self.variant,
            "map_shape": map_tensor.shape,
            "map_channels": list(self.MAP_CHANNELS),
            "feature_names": self._feature_names,
            "embedding_slot": slot,
        }

        return {
            "map": map_tensor,
            "features": features,
            "metadata": metadata,
        }

    # ------------------------------------------------------------------
    # Social snippet helpers
    # ------------------------------------------------------------------
    def _build_social_vector(
        self,
        world: "WorldState",
        snapshot: "AgentSnapshot",
    ) -> np.ndarray:
        if not self._social_vector_length:
            return self._empty_social_vector

        vector = np.zeros(self._social_vector_length, dtype=np.float32)
        slot_values = self._collect_social_slots(world, snapshot)
        offset = 0
        for slot in slot_values:
            embed_vector = slot["embedding"]
            vector[offset : offset + self.social_cfg.embed_dim] = embed_vector
            offset += self.social_cfg.embed_dim
            vector[offset] = slot["trust"]
            offset += 1
            vector[offset] = slot["familiarity"]
            offset += 1
            vector[offset] = slot["rivalry"]
            offset += 1

        if self._social_aggregate_names:
            trust_values = [slot["trust"] for slot in slot_values if slot["valid" ]]
            rivalry_values = [slot["rivalry"] for slot in slot_values if slot["valid"]]
            aggregates = self._compute_aggregates(trust_values, rivalry_values)
            for value in aggregates:
                if offset < len(vector):
                    vector[offset] = value
                    offset += 1
        return vector

    def _collect_social_slots(
        self,
        world: "WorldState",
        snapshot: "AgentSnapshot",
    ) -> List[Dict[str, float]]:
        total_slots = self._social_slots
        if total_slots == 0:
            return []

        relations = self._resolve_relationships(world, snapshot.agent_id)
        friend_candidates = sorted(
            relations,
            key=lambda entry: entry["trust"] + entry["familiarity"],
            reverse=True,
        )
        rival_candidates = sorted(
            relations,
            key=lambda entry: entry["rivalry"],
            reverse=True,
        )

        friends = friend_candidates[: self.social_cfg.top_friends]
        rivals: List[Dict[str, float]] = []
        for entry in rival_candidates:
            if entry in friends:
                continue
            rivals.append(entry)
            if len(rivals) >= self.social_cfg.top_rivals:
                break

        slots: List[Dict[str, float]] = []
        for entry in friends + rivals:
            slots.append(self._encode_relationship(entry))

        while len(slots) < total_slots:
            slots.append(self._empty_relationship_entry())

        return slots[:total_slots]

    def _resolve_relationships(
        self,
        world: "WorldState",
        agent_id: str,
    ) -> List[Dict[str, float]]:
        snapshot_getter = getattr(world, "relationships_snapshot", None)
        relationships: Dict[str, Dict[str, float]] = {}
        if callable(snapshot_getter):
            data = snapshot_getter()
            if isinstance(data, dict):
                relationships = data.get(agent_id, {}) or {}

        entries: List[Dict[str, float]] = []
        for other_id, metrics in relationships.items():
            if not isinstance(metrics, dict):
                continue
            entries.append(
                {
                    "other_id": str(other_id),
                    "trust": float(metrics.get("trust", 0.0)),
                    "familiarity": float(metrics.get("familiarity", 0.0)),
                    "rivalry": float(metrics.get("rivalry", 0.0)),
                }
            )

        if entries:
            return entries

        # Fallback to rivalry ledger until full relationship system lands.
        rivalry_data = world.rivalry_top(agent_id, limit=self.social_cfg.top_rivals)
        fallback_entries = []
        for other_id, rivalry in rivalry_data:
            fallback_entries.append(
                {
                    "other_id": other_id,
                    "trust": 0.0,
                    "familiarity": 0.0,
                    "rivalry": float(rivalry),
                }
            )
        return fallback_entries

    def _encode_relationship(self, entry: Dict[str, float]) -> Dict[str, float]:
        other_id = entry["other_id"]
        embedding = self._embed_agent_id(other_id)
        return {
            "embedding": embedding,
            "trust": entry.get("trust", 0.0),
            "familiarity": entry.get("familiarity", 0.0),
            "rivalry": entry.get("rivalry", 0.0),
            "valid": True,
        }

    def _empty_relationship_entry(self) -> Dict[str, float]:
        return {
            "embedding": np.zeros(self.social_cfg.embed_dim, dtype=np.float32),
            "trust": 0.0,
            "familiarity": 0.0,
            "rivalry": 0.0,
            "valid": False,
        }

    def _embed_agent_id(self, other_id: str) -> np.ndarray:
        digest = hashlib.blake2s(other_id.encode("utf-8")).digest()
        values = np.frombuffer(digest, dtype=np.uint8)
        floats = values.astype(np.float32) / 255.0
        repeats = int(np.ceil(self.social_cfg.embed_dim / floats.size))
        tiled = np.tile(floats, repeats)
        return tiled[: self.social_cfg.embed_dim]

    def _compute_aggregates(
        self,
        trust_values: Iterable[float],
        rivalry_values: Iterable[float],
    ) -> Tuple[float, float, float, float]:
        trust_list = list(trust_values)
        rivalry_list = list(rivalry_values)
        trust_mean = float(np.mean(trust_list)) if trust_list else 0.0
        trust_max = float(np.max(trust_list)) if trust_list else 0.0
        rivalry_mean = float(np.mean(rivalry_list)) if rivalry_list else 0.0
        rivalry_max = float(np.max(rivalry_list)) if rivalry_list else 0.0
        return trust_mean, trust_max, rivalry_mean, rivalry_max
