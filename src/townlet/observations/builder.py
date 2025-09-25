"""Observation encoding across variants."""
from __future__ import annotations

from math import cos, sin, tau
from typing import Dict, TYPE_CHECKING

import numpy as np

from townlet.config import ObservationVariant, SimulationConfig

if TYPE_CHECKING:
    from townlet.world.grid import AgentSnapshot, WorldState


class ObservationBuilder:
    """Constructs per-agent observation payloads."""

    MAP_CHANNELS = ("self", "agents", "objects", "reservations")
    SHIFT_STATES = ("pre_shift", "on_time", "late", "absent", "post_shift")
    SOCIAL_PLACEHOLDER_DIM = 16

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.variant: ObservationVariant = config.observation_variant
        self.hybrid_cfg = config.observations_config.hybrid
        self._shift_feature_map = {
            "pre_shift": "shift_pre",
            "on_time": "shift_on_time",
            "late": "shift_late",
            "absent": "shift_absent",
            "post_shift": "shift_post",
        }
        self._feature_names = [
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
        ] + [f"social_placeholder_{i}" for i in range(self.SOCIAL_PLACEHOLDER_DIM)]
        self._feature_index = {name: idx for idx, name in enumerate(self._feature_names)}

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
