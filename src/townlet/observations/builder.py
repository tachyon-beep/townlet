"""Observation encoding across variants."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from math import cos, sin, tau
from typing import TYPE_CHECKING

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
        # Precompute hybrid target landmarks (optional).
        self._landmarks: list[str] = [
            "fridge",
            "stove",
            "bed",
            "shower",
        ]
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
            "last_action_id_hash",
            "last_action_success",
            "last_action_duration",
            "reservation_active",
            "in_queue",
        ]
        path_hint_names = [
            "path_hint_north",
            "path_hint_south",
            "path_hint_east",
            "path_hint_west",
        ]
        base_feature_names.extend(path_hint_names)

        self._landmark_slices: dict[str, slice] = {}
        if self.hybrid_cfg.include_targets:
            for landmark in self._landmarks:
                start = len(base_feature_names)
                base_feature_names.extend(
                    [f"{landmark}_dx", f"{landmark}_dy", f"{landmark}_dist"]
                )
                self._landmark_slices[landmark] = slice(start, start + 3)

        self._path_hint_indices = {
            direction: base_feature_names.index(name)
            for direction, name in zip(
                ("north", "south", "east", "west"), path_hint_names
            )
        }

        self._social_slots = max(
            0, self.social_cfg.top_friends + self.social_cfg.top_rivals
        )
        if self._social_slots and self.config.features.stages.relationships == "OFF":
            raise ValueError("Social snippet requires relationships stage enabled")

        self._social_slot_dim = (
            self.social_cfg.embed_dim + 3
        )  # id embedding + trust/fam/rivalry
        self.full_channels = self.MAP_CHANNELS + ("path_dx", "path_dy")
        social_feature_names: list[str] = []
        for slot_index in range(self._social_slots):
            for component_index in range(self._social_slot_dim):
                social_feature_names.append(
                    f"social_slot{slot_index}_d{component_index}"
                )

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
        self._feature_index = {
            name: idx for idx, name in enumerate(self._feature_names)
        }
        self._base_feature_len = len(base_feature_names)
        self._social_vector_length = len(social_feature_names)
        self._social_slice = slice(
            self._base_feature_len,
            self._base_feature_len + self._social_vector_length,
        )

        self._empty_social_vector = np.zeros(
            self._social_vector_length, dtype=np.float32
        )

    def build_batch(
        self, world: "WorldState", terminated: dict[str, bool]
    ) -> dict[str, dict[str, np.ndarray]]:
        """Return a mapping from agent_id to observation payloads."""
        observations: dict[str, dict[str, np.ndarray]] = {}
        snapshots = world.snapshot()
        for agent_id, snapshot in snapshots.items():
            slot = world.embedding_allocator.allocate(agent_id, world.tick)
            obs = self._build_single(world, snapshot, slot)
            if terminated.get(agent_id):
                obs["features"][self._feature_index["ctx_reset_flag"]] = 1.0
                world.embedding_allocator.release(agent_id, world.tick)
            observations[agent_id] = obs
        return observations

    def _encode_common_features(
        self,
        features: np.ndarray,
        *,
        context: dict[str, object],
        slot: int,
        snapshot: "AgentSnapshot",
        world_tick: int,
    ) -> None:
        needs = context.get("needs", {})
        features[self._feature_index["need_hunger"]] = float(needs.get("hunger", 0.0))
        features[self._feature_index["need_hygiene"]] = float(needs.get("hygiene", 0.0))
        features[self._feature_index["need_energy"]] = float(needs.get("energy", 0.0))
        features[self._feature_index["wallet"]] = float(context.get("wallet", 0.0))
        features[self._feature_index["lateness_counter"]] = float(
            context.get("lateness_counter", 0.0)
        )
        features[self._feature_index["on_shift"]] = (
            1.0 if context.get("on_shift") else 0.0
        )

        ticks_per_day = self.hybrid_cfg.time_ticks_per_day
        phase = (world_tick % ticks_per_day) / ticks_per_day
        features[self._feature_index["time_sin"]] = sin(tau * phase)
        features[self._feature_index["time_cos"]] = cos(tau * phase)

        features[self._feature_index["attendance_ratio"]] = float(
            context.get("attendance_ratio", 0.0)
        )
        features[self._feature_index["wages_withheld"]] = float(
            context.get("wages_withheld", 0.0)
        )

        last_action_id = context.get("last_action_id") or ""
        if last_action_id:
            digest = hashlib.blake2s(last_action_id.encode("utf-8")).digest()
            value = int.from_bytes(digest[:4], "little") / float(2**32)
        else:
            value = 0.0
        features[self._feature_index["last_action_id_hash"]] = float(value)
        features[self._feature_index["last_action_success"]] = (
            1.0 if context.get("last_action_success") else 0.0
        )
        features[self._feature_index["last_action_duration"]] = float(
            context.get("last_action_duration", 0.0)
        )

        shift_state = context.get("shift_state", "pre_shift")
        if shift_state not in self.SHIFT_STATES:
            shift_state = "pre_shift"
        for name, feature_name in self._shift_feature_map.items():
            features[self._feature_index[feature_name]] = (
                1.0 if name == shift_state else 0.0
            )

        max_slots = self.config.embedding_allocator.max_slots
        features[self._feature_index["embedding_slot_norm"]] = float(slot) / float(
            max_slots
        )
        features[self._feature_index["ctx_reset_flag"]] = 0.0

        episode_length = max(1, self.hybrid_cfg.time_ticks_per_day)
        progress = float(getattr(snapshot, "episode_tick", 0)) / float(episode_length)
        features[self._feature_index["episode_progress"]] = max(0.0, min(1.0, progress))

    def _encode_rivalry(
        self,
        features: np.ndarray,
        world: "WorldState",
        snapshot: "AgentSnapshot",
    ) -> None:
        top_rivals = world.rivalry_top(
            snapshot.agent_id, limit=self.config.conflict.rivalry.max_edges
        )
        max_rivalry = top_rivals[0][1] if top_rivals else 0.0
        avoid_threshold = self.config.conflict.rivalry.avoid_threshold
        avoid_count = sum(1 for _, value in top_rivals if value >= avoid_threshold)
        features[self._feature_index["rivalry_max"]] = float(max_rivalry)
        features[self._feature_index["rivalry_avoid_count"]] = float(avoid_count)

    def _encode_environmental_flags(
        self,
        features: np.ndarray,
        world: "WorldState",
        snapshot: "AgentSnapshot",
    ) -> None:
        reservation_idx = self._feature_index.get("reservation_active")
        if reservation_idx is not None:
            reservations = world.active_reservations
            active = snapshot.agent_id in reservations.values()
            features[reservation_idx] = 1.0 if active else 0.0

        queue_idx = self._feature_index.get("in_queue")
        if queue_idx is not None:
            in_queue = False
            for object_id in world.objects.keys():
                queue = world.queue_manager.queue_snapshot(object_id)
                if snapshot.agent_id in queue:
                    in_queue = True
                    break
            features[queue_idx] = 1.0 if in_queue else 0.0

    def _encode_path_hint(
        self,
        features: np.ndarray,
        world: "WorldState",
        snapshot: "AgentSnapshot",
    ) -> None:
        if not self._path_hint_indices:
            return
        target = world.find_nearest_object_of_type("stove", snapshot.position)
        if target is None:
            north = south = east = west = 0.0
        else:
            dx = target[0] - snapshot.position[0]
            dy = target[1] - snapshot.position[1]
            norm = abs(dx) + abs(dy)
            if norm == 0:
                north = south = east = west = 0.0
            else:
                north = max(0.0, -dy) / norm
                south = max(0.0, dy) / norm
                east = max(0.0, dx) / norm
                west = max(0.0, -dx) / norm
        features[self._path_hint_indices["north"]] = north
        features[self._path_hint_indices["south"]] = south
        features[self._path_hint_indices["east"]] = east
        features[self._path_hint_indices["west"]] = west

    def _build_single(
        self,
        world: "WorldState",
        snapshot: "AgentSnapshot",
        slot: int,
    ) -> dict[str, np.ndarray | dict[str, object]]:
        if self.variant == "hybrid":
            return self._build_hybrid(world, snapshot, slot)
        if self.variant == "full":
            return self._build_full(world, snapshot, slot)
        if self.variant == "compact":
            return self._build_compact(world, snapshot, slot)
        # TODO(@townlet): implement compact variant.
        return {
            "map": np.zeros((1, 1, 1), dtype=np.float32),
            "features": np.zeros(1, dtype=np.float32),
            "metadata": {"variant": self.variant},
        }

    def _map_from_view(
        self,
        channels: tuple[str, ...],
        local_view: dict[str, object],
        window: int,
        center: int,
        snapshot: "AgentSnapshot",
    ) -> np.ndarray:
        tensor = np.zeros((len(channels), window, window), dtype=np.float32)
        tensor[0, center, center] = 1.0
        for row in local_view.get("tiles", []):
            for tile in row:
                tx, ty = tile["position"]
                dx = tx - snapshot.position[0]
                dy = ty - snapshot.position[1]
                x = center + dx
                y = center + dy
                if 0 <= x < window and 0 <= y < window:
                    if "agents" in channels and tile.get("agent_ids"):
                        tensor[channels.index("agents"), y, x] = 1.0
                    if "objects" in channels and tile.get("object_ids"):
                        tensor[channels.index("objects"), y, x] = 1.0
                    if "reservations" in channels and tile.get("reservation_active"):
                        tensor[channels.index("reservations"), y, x] = 1.0
                    if "path_dx" in channels or "path_dy" in channels:
                        distance = float(np.hypot(dx, dy))
                        if distance > 0:
                            norm = distance
                            if "path_dx" in channels:
                                tensor[channels.index("path_dx"), y, x] = (
                                    float(dx) / norm
                                )
                            if "path_dy" in channels:
                                tensor[channels.index("path_dy"), y, x] = (
                                    float(dy) / norm
                                )
        return tensor

    def _build_hybrid(
        self,
        world: "WorldState",
        snapshot: "AgentSnapshot",
        slot: int,
    ) -> dict[str, np.ndarray | dict[str, object]]:
        window = self.hybrid_cfg.local_window
        radius = window // 2
        local_view = world.local_view(snapshot.agent_id, radius)
        map_tensor = self._map_from_view(
            self.MAP_CHANNELS, local_view, window, radius, snapshot
        )

        features = np.zeros(len(self._feature_names), dtype=np.float32)
        context = world.agent_context(snapshot.agent_id)
        self._encode_common_features(
            features,
            context=context,
            slot=slot,
            snapshot=snapshot,
            world_tick=world.tick,
        )
        self._encode_environmental_flags(features, world, snapshot)
        self._encode_path_hint(features, world, snapshot)

        if self.hybrid_cfg.include_targets and self._landmark_slices:
            self._encode_landmarks(features, world, snapshot)

        self._encode_rivalry(features, world, snapshot)

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
        if self._landmark_slices:
            metadata["landmark_slices"] = {
                name: (slice_.start, slice_.stop)
                for name, slice_ in self._landmark_slices.items()
            }

        return {
            "map": map_tensor,
            "features": features,
            "metadata": metadata,
        }

    def _build_full(
        self,
        world: "WorldState",
        snapshot: "AgentSnapshot",
        slot: int,
    ) -> dict[str, np.ndarray | dict[str, object]]:
        window = self.hybrid_cfg.local_window
        radius = window // 2
        local_view = world.local_view(snapshot.agent_id, radius)
        map_tensor = self._map_from_view(
            self.full_channels, local_view, window, radius, snapshot
        )

        features = np.zeros(len(self._feature_names), dtype=np.float32)
        context = world.agent_context(snapshot.agent_id)
        self._encode_common_features(
            features,
            context=context,
            slot=slot,
            snapshot=snapshot,
            world_tick=world.tick,
        )
        self._encode_environmental_flags(features, world, snapshot)
        self._encode_path_hint(features, world, snapshot)

        if self.hybrid_cfg.include_targets and self._landmark_slices:
            self._encode_landmarks(features, world, snapshot)

        self._encode_rivalry(features, world, snapshot)

        if self._social_vector_length:
            social_vector = self._build_social_vector(world, snapshot)
            features[self._social_slice] = social_vector

        metadata = {
            "variant": self.variant,
            "map_shape": map_tensor.shape,
            "map_channels": list(self.full_channels),
            "feature_names": self._feature_names,
            "embedding_slot": slot,
        }
        if self._landmark_slices:
            metadata["landmark_slices"] = {
                name: (slice_.start, slice_.stop)
                for name, slice_ in self._landmark_slices.items()
            }

        return {
            "map": map_tensor,
            "features": features,
            "metadata": metadata,
        }

    def _build_compact(
        self,
        world: "WorldState",
        snapshot: "AgentSnapshot",
        slot: int,
    ) -> dict[str, np.ndarray | dict[str, object]]:
        features = np.zeros(len(self._feature_names), dtype=np.float32)
        context = world.agent_context(snapshot.agent_id)
        self._encode_common_features(
            features,
            context=context,
            slot=slot,
            snapshot=snapshot,
            world_tick=world.tick,
        )
        self._encode_environmental_flags(features, world, snapshot)
        self._encode_path_hint(features, world, snapshot)

        if self.hybrid_cfg.include_targets and self._landmark_slices:
            self._encode_landmarks(features, world, snapshot)

        self._encode_rivalry(features, world, snapshot)

        if self._social_vector_length:
            social_vector = self._build_social_vector(world, snapshot)
            features[self._social_slice] = social_vector

        metadata = {
            "variant": self.variant,
            "map_shape": (0, 0, 0),
            "map_channels": [],
            "feature_names": self._feature_names,
            "embedding_slot": slot,
        }
        if self._landmark_slices:
            metadata["landmark_slices"] = {
                name: (slice_.start, slice_.stop)
                for name, slice_ in self._landmark_slices.items()
            }

        return {
            "map": np.zeros((0, 0, 0), dtype=np.float32),
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
            trust_values = [slot["trust"] for slot in slot_values if slot["valid"]]
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
    ) -> list[dict[str, float]]:
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
        rivals: list[dict[str, float]] = []
        for entry in rival_candidates:
            if entry in friends:
                continue
            rivals.append(entry)
            if len(rivals) >= self.social_cfg.top_rivals:
                break

        slots: list[dict[str, float]] = []
        for entry in friends + rivals:
            slots.append(self._encode_relationship(entry))

        while len(slots) < total_slots:
            slots.append(self._empty_relationship_entry())

        return slots[:total_slots]

    def _resolve_relationships(
        self,
        world: "WorldState",
        agent_id: str,
    ) -> list[dict[str, float]]:
        snapshot_getter = getattr(world, "relationships_snapshot", None)
        relationships: dict[str, dict[str, float]] = {}
        if callable(snapshot_getter):
            data = snapshot_getter()
            if isinstance(data, dict):
                relationships = data.get(agent_id, {}) or {}

        entries: list[dict[str, float]] = []
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

    def _encode_landmarks(
        self,
        features: np.ndarray,
        world: "WorldState",
        snapshot: "AgentSnapshot",
    ) -> None:
        cx, cy = snapshot.position
        for landmark in self._landmarks:
            slice_ = self._landmark_slices.get(landmark)
            if slice_ is None:
                continue
            position = world.find_nearest_object_of_type(landmark, snapshot.position)
            if position is None:
                features[slice_] = 0.0
                continue
            dx = position[0] - cx
            dy = position[1] - cy
            distance = float(np.hypot(dx, dy))
            norm = distance if distance > 0 else 1.0
            values = np.array(
                [float(dx) / norm, float(dy) / norm, distance], dtype=np.float32
            )
            features[slice_] = values

    def _encode_relationship(self, entry: dict[str, float]) -> dict[str, float]:
        other_id = entry["other_id"]
        embedding = self._embed_agent_id(other_id)
        return {
            "embedding": embedding,
            "trust": entry.get("trust", 0.0),
            "familiarity": entry.get("familiarity", 0.0),
            "rivalry": entry.get("rivalry", 0.0),
            "valid": True,
        }

    def _empty_relationship_entry(self) -> dict[str, float]:
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
    ) -> tuple[float, float, float, float]:
        trust_list = list(trust_values)
        rivalry_list = list(rivalry_values)
        trust_mean = float(np.mean(trust_list)) if trust_list else 0.0
        trust_max = float(np.max(trust_list)) if trust_list else 0.0
        rivalry_mean = float(np.mean(rivalry_list)) if rivalry_list else 0.0
        rivalry_max = float(np.max(rivalry_list)) if rivalry_list else 0.0
        return trust_mean, trust_max, rivalry_mean, rivalry_max
