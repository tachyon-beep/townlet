"""Observation service wrapper owned by the world context."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

import numpy as np

from townlet.config import ObservationVariant, SimulationConfig
from townlet.world.core.runtime_adapter import ensure_world_adapter
from townlet.world.observations.cache import build_local_cache
from townlet.world.observations.context import agent_context
from townlet.world.observations.encoders import (
    encode_compact_map,
    encode_feature_vector,
    encode_map_tensor,
    encode_social_vector,
)
from townlet.world.observations.encoders.map import LocalCache
from townlet.world.observations.interfaces import (
    AdapterSource,
    ObservationServiceProtocol,
)


class WorldObservationService(ObservationServiceProtocol):
    """Observation service using native encoder functions."""

    MAP_CHANNELS = ("self", "agents", "objects", "reservations")
    SHIFT_STATES = ("pre_shift", "on_time", "late", "absent", "post_shift")

    def __init__(self, *, config: SimulationConfig) -> None:
        self.config = config
        self._variant: ObservationVariant = config.observation_variant
        self.hybrid_cfg = config.observations_config.hybrid
        self.compact_cfg = config.observations_config.compact
        self.social_cfg = config.observations_config.social_snippet

        # Validate relationships stage is enabled (required for social features)
        if config.features.stages.relationships == "OFF":
            raise ValueError(
                "WorldObservationService requires relationships stage to be enabled"
            )

        # Personality (must be set before _build_feature_names)
        self._personality_enabled = False
        if hasattr(config, "personality_channels_enabled"):
            try:
                self._personality_enabled = bool(config.personality_channels_enabled())
            except Exception:  # pragma: no cover
                self._personality_enabled = False

        # Build feature name list
        self._feature_names, self._feature_index = self._build_feature_names()
        self._social_slots = max(0, self.social_cfg.top_friends + self.social_cfg.top_rivals)
        self._social_slot_dim = self.social_cfg.embed_dim + 3
        self._social_vector_length = self._compute_social_vector_length()

        # Build map channel lists
        self.full_channels = (*self.MAP_CHANNELS, "path_dx", "path_dy")
        self.compact_map_channels, self._compact_object_channels = self._build_compact_channels()

        # Landmarks - calculate slices based on where landmarks appear in feature names
        self._landmarks: list[str] = ["fridge", "stove", "bed", "shower"]
        self._landmark_slices: dict[str, slice] = {}
        # Check include_targets based on current variant
        include_targets_for_variant = (
            self.compact_cfg.include_targets
            if self._variant == "compact"
            else self.hybrid_cfg.include_targets
        )
        if include_targets_for_variant:
            # Find the first landmark feature index
            try:
                first_landmark_idx = self._feature_index[f"{self._landmarks[0]}_dx"]
                for idx, landmark in enumerate(self._landmarks):
                    start = first_landmark_idx + idx * 3
                    self._landmark_slices[landmark] = slice(start, start + 3)
            except KeyError:
                pass  # Landmarks not in feature names

    def _build_feature_names(self) -> tuple[list[str], dict[str, int]]:
        """Build the feature name list for observation encoding."""
        shift_feature_map = {
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
            *shift_feature_map.values(),
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

        local_summary_names = [
            "neighbor_agent_ratio",
            "neighbor_object_ratio",
            "reserved_tile_ratio",
            "nearest_agent_distance",
        ]
        base_feature_names.extend(local_summary_names)

        # Check include_targets based on current variant
        include_targets = (
            self.compact_cfg.include_targets
            if self._variant == "compact"
            else self.hybrid_cfg.include_targets
        )
        if include_targets:
            for landmark in ["fridge", "stove", "bed", "shower"]:
                base_feature_names.extend(
                    [f"{landmark}_dx", f"{landmark}_dy", f"{landmark}_dist"]
                )

        if self._personality_enabled:
            base_feature_names.extend([
                "personality_extroversion",
                "personality_forgiveness",
                "personality_ambition",
            ])

        # Social features
        social_slots = max(0, self.social_cfg.top_friends + self.social_cfg.top_rivals)
        social_slot_dim = self.social_cfg.embed_dim + 3
        social_feature_names: list[str] = []
        for slot_index in range(social_slots):
            for component_index in range(social_slot_dim):
                social_feature_names.append(f"social_slot{slot_index}_d{component_index}")

        if self.social_cfg.include_aggregates:
            social_feature_names.extend([
                "social_trust_mean",
                "social_trust_max",
                "social_rivalry_mean",
                "social_rivalry_max",
            ])

        feature_names = base_feature_names + social_feature_names
        feature_index = {name: idx for idx, name in enumerate(feature_names)}
        return feature_names, feature_index

    def _build_compact_channels(self) -> tuple[tuple[str, ...], list[str]]:
        """Build compact map channels with object type channels."""
        compact_channels: list[str] = ["self", "agents", "objects", "reservations"]
        object_channels: list[str] = []
        for name in self.compact_cfg.object_channels:
            sanitized = str(name).strip().lower()
            if sanitized and sanitized not in object_channels:
                object_channels.append(sanitized)
                compact_channels.append(f"object:{sanitized}")
        compact_channels.append("walkable")
        return tuple(compact_channels), object_channels

    def _compute_social_vector_length(self) -> int:
        """Compute social vector length including aggregates."""
        length = self._social_slots * self._social_slot_dim
        if self.social_cfg.include_aggregates:
            length += 4  # trust_mean, trust_max, rivalry_mean, rivalry_max
        return length

    @property
    def variant(self) -> object:
        return self._variant

    @property
    def feature_names(self) -> tuple[str, ...]:
        return tuple(self._feature_names)

    @property
    def social_vector_length(self) -> int:
        return self._social_vector_length

    def build_batch(
        self,
        world: AdapterSource,
        terminated: Mapping[str, bool],
    ) -> Mapping[str, Mapping[str, Any]]:
        """Build observation batch for all active agents."""
        adapter = ensure_world_adapter(world)
        observations: dict[str, dict[str, np.ndarray | dict[str, object]]] = {}
        snapshots = dict(adapter.agent_snapshots_view())
        pending_resets = set(adapter.consume_ctx_reset_requests())

        # Build spatial cache
        agent_lookup, object_lookup, reservation_tiles = build_local_cache(
            adapter, snapshots
        )
        cache = LocalCache(agent_lookup, object_lookup, reservation_tiles)

        for agent_id, snapshot in snapshots.items():
            slot = adapter.embedding_allocator.allocate(agent_id, adapter.tick)
            obs = self._build_single(adapter, snapshot, slot, cache)
            features_array = cast(np.ndarray, obs["features"])

            # Handle ctx_reset flags
            if agent_id in pending_resets:
                features_array[self._feature_index["ctx_reset_flag"]] = 1.0
                pending_resets.discard(agent_id)
            if terminated.get(agent_id, False):
                features_array[self._feature_index["ctx_reset_flag"]] = 1.0
                adapter.embedding_allocator.release(agent_id, adapter.tick)

            observations[agent_id] = obs

        return observations

    def build_single(
        self,
        world: AdapterSource,
        agent_id: str,
        *,
        slot: int | None = None,
    ) -> Mapping[str, Any]:
        """Build observation for a single agent (fallback implementation)."""
        batch = self.build_batch(world, {})
        if agent_id not in batch:
            raise KeyError(f"agent '{agent_id}' not present in observation batch")
        entry = batch[agent_id]
        if slot is None:
            return entry
        payload = dict(entry)
        metadata = dict(payload.get("metadata", {}))  # type: ignore[arg-type]
        metadata["embedding_slot"] = slot
        payload["metadata"] = metadata
        return payload

    def _build_single(
        self,
        world: Any,  # WorldRuntimeAdapterProtocol
        snapshot: Any,  # AgentSnapshot
        slot: int,
        cache: LocalCache,
    ) -> dict[str, np.ndarray | dict[str, object]]:
        """Build observation for a single agent using encoders."""
        if self._variant == "hybrid":
            return self._build_hybrid(world, snapshot, slot, cache)
        if self._variant == "full":
            return self._build_full(world, snapshot, slot, cache)
        if self._variant == "compact":
            return self._build_compact(world, snapshot, slot, cache)
        raise ValueError(f"Unsupported observation variant: {self._variant}")

    def _build_hybrid(
        self, world: Any, snapshot: Any, slot: int, cache: LocalCache
    ) -> dict[str, np.ndarray | dict[str, object]]:
        """Build hybrid variant observation."""
        window = self.hybrid_cfg.local_window
        radius = window // 2
        map_tensor, local_summary = encode_map_tensor(
            channels=self.MAP_CHANNELS, snapshot=snapshot, radius=radius, cache=cache
        )

        context = agent_context(world, snapshot.agent_id)
        features, local_summary_dict, personality_context = encode_feature_vector(
            world=world,
            snapshot=snapshot,
            context=context,
            slot=slot,
            cache=cache,
            feature_index=self._feature_index,
            config=self.config,
            local_summary=local_summary,
            landmarks=self._landmarks if self.hybrid_cfg.include_targets else None,
            landmark_slices=self._landmark_slices if self.hybrid_cfg.include_targets else None,
            personality_enabled=self._personality_enabled,
        )

        # Encode social vector
        social_context: dict[str, object] = {
            "configured_slots": self._social_slots,
            "slot_dim": self._social_slot_dim,
            "aggregates": self._aggregate_names(),
            "filled_slots": 0,
            "relation_source": "disabled" if self._social_vector_length == 0 else "empty",
            "has_data": False,
        }
        if self._social_vector_length:
            social_vector, social_ctx = encode_social_vector(
                world=world,
                snapshot=snapshot,
                social_cfg=self.social_cfg,
                config=self.config,
            )
            base_len = len(self._feature_names) - self._social_vector_length
            social_slice = slice(base_len, base_len + self._social_vector_length)
            features[social_slice] = social_vector
            social_context.update(social_ctx)

        metadata = self._build_metadata(
            slot=slot,
            map_shape=map_tensor.shape,
            map_channels=self.MAP_CHANNELS,
            social_context=social_context,
            local_summary=local_summary_dict,
            personality_context=personality_context,
        )

        return {
            "map": map_tensor,
            "features": features,
            "metadata": metadata,
        }

    def _build_full(
        self, world: Any, snapshot: Any, slot: int, cache: LocalCache
    ) -> dict[str, np.ndarray | dict[str, object]]:
        """Build full variant observation."""
        window = self.hybrid_cfg.local_window
        radius = window // 2
        map_tensor, local_summary = encode_map_tensor(
            channels=self.full_channels, snapshot=snapshot, radius=radius, cache=cache
        )

        context = agent_context(world, snapshot.agent_id)
        features, local_summary_dict, personality_context = encode_feature_vector(
            world=world,
            snapshot=snapshot,
            context=context,
            slot=slot,
            cache=cache,
            feature_index=self._feature_index,
            config=self.config,
            local_summary=local_summary,
            landmarks=self._landmarks if self.hybrid_cfg.include_targets else None,
            landmark_slices=self._landmark_slices if self.hybrid_cfg.include_targets else None,
            personality_enabled=self._personality_enabled,
        )

        # Encode social vector
        social_context: dict[str, object] = {
            "configured_slots": self._social_slots,
            "slot_dim": self._social_slot_dim,
            "aggregates": self._aggregate_names(),
            "filled_slots": 0,
            "relation_source": "disabled" if self._social_vector_length == 0 else "empty",
            "has_data": False,
        }
        if self._social_vector_length:
            social_vector, social_ctx = encode_social_vector(
                world=world,
                snapshot=snapshot,
                social_cfg=self.social_cfg,
                config=self.config,
            )
            base_len = len(self._feature_names) - self._social_vector_length
            social_slice = slice(base_len, base_len + self._social_vector_length)
            features[social_slice] = social_vector
            social_context.update(social_ctx)

        metadata = self._build_metadata(
            slot=slot,
            map_shape=map_tensor.shape,
            map_channels=self.full_channels,
            social_context=social_context,
            local_summary=local_summary_dict,
            personality_context=personality_context,
        )

        return {
            "map": map_tensor,
            "features": features,
            "metadata": metadata,
        }

    def _build_compact(
        self, world: Any, snapshot: Any, slot: int, cache: LocalCache
    ) -> dict[str, np.ndarray | dict[str, object]]:
        """Build compact variant observation."""
        window = self.compact_cfg.map_window
        radius = window // 2

        # Get local summary for features (no map needed)
        _, local_summary = encode_map_tensor(
            channels=(), snapshot=snapshot, radius=radius, cache=cache
        )

        # Encode compact map
        map_tensor = encode_compact_map(
            world=world,
            snapshot=snapshot,
            radius=radius,
            cache=cache,
            channels=self.compact_map_channels,
            object_channels=self._compact_object_channels,
            normalize_counts=self.compact_cfg.normalize_counts,
        )

        context = agent_context(world, snapshot.agent_id)
        features, local_summary_dict, personality_context = encode_feature_vector(
            world=world,
            snapshot=snapshot,
            context=context,
            slot=slot,
            cache=cache,
            feature_index=self._feature_index,
            config=self.config,
            local_summary=local_summary,
            landmarks=self._landmarks if self.compact_cfg.include_targets else None,
            landmark_slices=self._landmark_slices if self.compact_cfg.include_targets else None,
            personality_enabled=self._personality_enabled,
        )

        # Encode social vector
        social_context: dict[str, object] = {
            "configured_slots": self._social_slots,
            "slot_dim": self._social_slot_dim,
            "aggregates": self._aggregate_names(),
            "filled_slots": 0,
            "relation_source": "disabled" if self._social_vector_length == 0 else "empty",
            "has_data": False,
        }
        if self._social_vector_length:
            social_vector, social_ctx = encode_social_vector(
                world=world,
                snapshot=snapshot,
                social_cfg=self.social_cfg,
                config=self.config,
            )
            base_len = len(self._feature_names) - self._social_vector_length
            social_slice = slice(base_len, base_len + self._social_vector_length)
            features[social_slice] = social_vector
            social_context.update(social_ctx)

        metadata = self._build_metadata(
            slot=slot,
            map_shape=map_tensor.shape,
            map_channels=self.compact_map_channels,
            social_context=social_context,
            local_summary=local_summary_dict,
            personality_context=personality_context,
        )
        metadata["compact"] = {
            "map_window": window,
            "object_channels": list(self._compact_object_channels),
            "normalize_counts": bool(self.compact_cfg.normalize_counts),
            "include_targets": bool(self.compact_cfg.include_targets),
        }

        return {
            "map": map_tensor,
            "features": features,
            "metadata": metadata,
        }

    def _build_metadata(
        self,
        *,
        slot: int,
        map_shape: tuple[int, int, int],
        map_channels: tuple[str, ...] | list[str],
        social_context: dict[str, object] | None = None,
        local_summary: dict[str, float] | None = None,
        personality_context: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Build metadata dictionary."""
        metadata: dict[str, object] = {
            "variant": self._variant,
            "map_shape": map_shape,
            "map_channels": list(map_channels),
            "feature_names": list(self._feature_names),
            "embedding_slot": slot,
        }
        if self._landmark_slices:
            metadata["landmark_slices"] = {
                name: (slice_.start, slice_.stop)
                for name, slice_ in self._landmark_slices.items()
            }
        if social_context is not None and social_context.get("configured_slots"):
            metadata["social_context"] = social_context
        if local_summary is not None:
            metadata["local_summary"] = local_summary
        if personality_context is not None:
            metadata["personality"] = personality_context
        return metadata

    def _aggregate_names(self) -> list[str]:
        """Get social aggregate names."""
        if self.social_cfg.include_aggregates:
            return [
                "social_trust_mean",
                "social_trust_max",
                "social_rivalry_mean",
                "social_rivalry_max",
            ]
        return []


__all__ = ["WorldObservationService"]
