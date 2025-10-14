"""Map tensor encoding for observation variants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from townlet.world.agents.snapshot import AgentSnapshot
    from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


@dataclass(frozen=True)
class LocalCache:
    """Spatial cache for fast tile lookups."""

    agent_lookup: dict[tuple[int, int], list[str]]
    object_lookup: dict[tuple[int, int], list[str]]
    reservation_tiles: set[tuple[int, int]]


@dataclass(frozen=True)
class LocalSummary:
    """Summary statistics for local neighborhood."""

    agent_count: float
    object_count: float
    reserved_tiles: float
    radius: float
    agent_ratio: float
    object_ratio: float
    reserved_ratio: float
    nearest_agent_distance: float
    nearest_agent_distance_norm: float


def encode_map_tensor(
    *,
    channels: tuple[str, ...],
    snapshot: AgentSnapshot,
    radius: int,
    cache: LocalCache,
) -> tuple[np.ndarray, LocalSummary]:
    """
    Encode a local map tensor around an agent's position.

    Supports full and hybrid variants with channels: self, agents, objects,
    reservations, path_dx, path_dy.

    Args:
        channels: Channel names to encode (empty tuple for summary-only)
        snapshot: Agent state snapshot
        radius: Map radius in tiles
        cache: Prebuilt spatial lookup cache

    Returns:
        (tensor, summary) where tensor is (C, H, W) and summary contains local stats
    """
    window = radius * 2 + 1
    tensor = (
        np.zeros((len(channels), window, window), dtype=np.float32)
        if channels
        else np.zeros((0, 0, 0), dtype=np.float32)
    )
    if channels:
        # Mark self position (first channel is always "self")
        tensor[0, radius, radius] = 1.0

    other_agents = 0
    object_total = 0
    reserved_tiles = 0
    nearest_distance: float | None = None
    total_tiles = window * window

    channel_index = {name: idx for idx, name in enumerate(channels)}
    cx, cy = snapshot.position

    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            x = cx + dx
            y = cy + dy
            position = (x, y)
            agents = cache.agent_lookup.get(position, [])
            objects = cache.object_lookup.get(position, [])
            reserved = position in cache.reservation_tiles

            if agents:
                count = len(agents)
                # Exclude self when positioned on the same tile
                if position == snapshot.position:
                    count -= 1
                other_agents += max(0, count)
                if count > 0:
                    distance = float(np.hypot(dx, dy))
                    if distance > 0 and (
                        nearest_distance is None or distance < nearest_distance
                    ):
                        nearest_distance = distance
            object_total += len(objects)
            if reserved:
                reserved_tiles += 1

            if not channels:
                continue
            tile_x = dx + radius
            tile_y = dy + radius
            if "agents" in channel_index and agents:
                tensor[channel_index["agents"], tile_y, tile_x] = 1.0
            if "objects" in channel_index and objects:
                tensor[channel_index["objects"], tile_y, tile_x] = 1.0
            if "reservations" in channel_index and reserved:
                tensor[channel_index["reservations"], tile_y, tile_x] = 1.0
            if "path_dx" in channel_index or "path_dy" in channel_index:
                distance = float(np.hypot(dx, dy))
                if distance > 0:
                    if "path_dx" in channel_index:
                        tensor[channel_index["path_dx"], tile_y, tile_x] = float(
                            dx
                        ) / distance
                    if "path_dy" in channel_index:
                        tensor[channel_index["path_dy"], tile_y, tile_x] = float(
                            dy
                        ) / distance

    max_tiles = max(1, total_tiles - 1)
    agent_ratio = min(1.0, other_agents / max_tiles)
    object_ratio = min(1.0, object_total / max(1, total_tiles))
    reserved_ratio = min(1.0, reserved_tiles / max(1, total_tiles))
    if nearest_distance is None:
        nearest_norm = 0.0
    else:
        nearest_norm = max(0.0, min(1.0, nearest_distance / max(1, radius)))

    summary = LocalSummary(
        agent_count=float(other_agents),
        object_count=float(object_total),
        reserved_tiles=float(reserved_tiles),
        radius=float(radius),
        agent_ratio=float(agent_ratio),
        object_ratio=float(object_ratio),
        reserved_ratio=float(reserved_ratio),
        nearest_agent_distance=0.0 if nearest_distance is None else float(nearest_distance),
        nearest_agent_distance_norm=float(nearest_norm),
    )

    return tensor, summary


def encode_compact_map(
    *,
    world: WorldRuntimeAdapterProtocol,
    snapshot: AgentSnapshot,
    radius: int,
    cache: LocalCache,
    channels: tuple[str, ...],
    object_channels: list[str],
    normalize_counts: bool,
) -> np.ndarray:
    """
    Encode a compact map tensor with per-object-type channels.

    The compact variant includes:
    - self, agents, objects, reservations (base channels)
    - object:<type> (one channel per configured object type)
    - walkable (binary channel for navigable tiles)

    Args:
        world: World adapter for object snapshots
        snapshot: Agent state snapshot
        radius: Map radius in tiles
        cache: Prebuilt spatial lookup cache
        channels: All channel names (base + object:* + walkable)
        object_channels: List of object types to encode (e.g., ["fridge", "stove"])
        normalize_counts: If True, clamp counts to 1.0

    Returns:
        Tensor of shape (C, H, W) where C = len(channels)
    """
    window = radius * 2 + 1
    tensor = np.zeros((len(channels), window, window), dtype=np.float32)
    channel_index = {name: idx for idx, name in enumerate(channels)}
    if "self" in channel_index:
        tensor[channel_index["self"], radius, radius] = 1.0

    objects_snapshot = world.objects_snapshot()
    cx, cy = snapshot.position
    for dy in range(-radius, radius + 1):
        tile_y = dy + radius
        for dx in range(-radius, radius + 1):
            tile_x = dx + radius
            position = (cx + dx, cy + dy)
            agents_here = cache.agent_lookup.get(position, [])
            objects_here = cache.object_lookup.get(position, [])
            reserved = position in cache.reservation_tiles

            other_agents = [agent for agent in agents_here if agent != snapshot.agent_id]
            if "agents" in channel_index and other_agents:
                value = float(len(other_agents))
                if normalize_counts:
                    value = min(1.0, value)
                tensor[channel_index["agents"], tile_y, tile_x] = value

            if "objects" in channel_index and objects_here:
                value = float(len(objects_here))
                if normalize_counts:
                    value = min(1.0, value)
                tensor[channel_index["objects"], tile_y, tile_x] = value

            if reserved and "reservations" in channel_index:
                tensor[channel_index["reservations"], tile_y, tile_x] = 1.0

            if object_channels:
                counts: dict[str, int] = {}
                for object_id in objects_here:
                    payload = objects_snapshot.get(object_id, {})
                    obj_key = str(payload.get("object_type") or "").strip().lower()
                    if obj_key in object_channels:
                        counts[obj_key] = counts.get(obj_key, 0) + 1
                for obj_key, count in counts.items():
                    channel_name = f"object:{obj_key}"
                    idx = channel_index.get(channel_name)
                    if idx is None:
                        continue
                    value = float(count)
                    if normalize_counts:
                        value = min(1.0, value)
                    tensor[idx, tile_y, tile_x] = value

            walkable_idx = channel_index.get("walkable")
            if walkable_idx is not None:
                walkable = 1.0
                if (
                    other_agents
                    or objects_here
                    or reserved
                    or position == snapshot.position
                ):
                    walkable = 0.0
                tensor[walkable_idx, tile_y, tile_x] = walkable

    return tensor


__all__ = ["LocalCache", "LocalSummary", "encode_map_tensor", "encode_compact_map"]
