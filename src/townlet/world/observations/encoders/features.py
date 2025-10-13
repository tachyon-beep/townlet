"""Feature vector encoding for agent observations."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from math import cos, sin, tau
from typing import TYPE_CHECKING, Any, cast

import numpy as np

from townlet.agents.models import PersonalityProfiles
from townlet.world.observations.views import find_nearest_object_of_type

if TYPE_CHECKING:
    from townlet.world.agents.snapshot import AgentSnapshot
    from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol

    from .map import LocalCache, LocalSummary


def _mapping_or_empty(value: object) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return cast(Mapping[str, object], value)
    return cast(Mapping[str, object], {})


def _string_or_empty(value: object) -> str:
    return value if isinstance(value, str) else ""


def _float_or_default(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _bool_flag(value: object) -> float:
    return 1.0 if bool(value) else 0.0


def encode_feature_vector(
    *,
    world: WorldRuntimeAdapterProtocol,
    snapshot: AgentSnapshot,
    context: dict[str, object],
    slot: int,
    cache: LocalCache,
    feature_index: dict[str, int],
    config: Any,  # SimulationConfig
    local_summary: LocalSummary | None = None,
    landmarks: list[str] | None = None,
    landmark_slices: dict[str, slice] | None = None,
    personality_enabled: bool = False,
) -> tuple[np.ndarray, dict[str, object], dict[str, object] | None]:
    """
    Encode a complete feature vector for an agent.

    Args:
        world: World adapter
        snapshot: Agent state snapshot
        context: Agent context dict (needs, wallet, shift state, etc.)
        slot: Embedding allocator slot
        cache: Spatial cache
        feature_index: Mapping of feature name to index
        config: Simulation config
        local_summary: Optional precomputed local summary
        landmarks: Optional list of landmark types to encode
        landmark_slices: Optional dict mapping landmark name to feature slice
        personality_enabled: Whether to encode personality features

    Returns:
        (features, local_summary_dict, personality_context)
    """
    features = np.zeros(len(feature_index), dtype=np.float32)

    # Core features: needs, wallet, shift state, time
    _encode_needs(features, context, feature_index)
    _encode_wallet_and_employment(features, context, feature_index)
    _encode_time(features, world.tick, config, feature_index)
    _encode_shift_state(features, context, feature_index, config)
    _encode_embedding_slot(features, slot, feature_index, config)
    _encode_episode_progress(features, snapshot, feature_index, config)

    # Action history
    _encode_last_action(features, context, feature_index)

    # Environmental flags
    _encode_environmental_flags(features, world, snapshot, feature_index)

    # Rivalry
    _encode_rivalry(features, world, snapshot, feature_index, config)

    # Path hints (hardcoded to "stove")
    _encode_path_hint(features, world, snapshot, feature_index)

    # Local summary (neighbor counts, distances)
    local_summary_dict = _encode_local_summary(
        features, snapshot, cache, feature_index, local_summary, config
    )

    # Landmarks (if enabled)
    if landmarks and landmark_slices:
        _encode_landmarks(features, world, snapshot, landmarks, landmark_slices)

    # Personality (if enabled)
    personality_context = None
    if personality_enabled:
        personality_context = _encode_personality(features, snapshot, feature_index)

    return features, local_summary_dict, personality_context


def _encode_needs(
    features: np.ndarray, context: dict[str, object], feature_index: dict[str, int]
) -> None:
    needs = _mapping_or_empty(context.get("needs"))
    features[feature_index["need_hunger"]] = _float_or_default(needs.get("hunger", 0.0))
    features[feature_index["need_hygiene"]] = _float_or_default(
        needs.get("hygiene", 0.0)
    )
    features[feature_index["need_energy"]] = _float_or_default(needs.get("energy", 0.0))


def _encode_wallet_and_employment(
    features: np.ndarray, context: dict[str, object], feature_index: dict[str, int]
) -> None:
    features[feature_index["wallet"]] = _float_or_default(context.get("wallet", 0.0))
    features[feature_index["lateness_counter"]] = _float_or_default(
        context.get("lateness_counter", 0.0)
    )
    features[feature_index["on_shift"]] = _bool_flag(context.get("on_shift"))
    features[feature_index["attendance_ratio"]] = _float_or_default(
        context.get("attendance_ratio", 0.0)
    )
    features[feature_index["wages_withheld"]] = _float_or_default(
        context.get("wages_withheld", 0.0)
    )


def _encode_time(
    features: np.ndarray, tick: int, config: Any, feature_index: dict[str, int]
) -> None:
    ticks_per_day = config.observations_config.hybrid.time_ticks_per_day
    phase = (tick % ticks_per_day) / ticks_per_day
    features[feature_index["time_sin"]] = sin(tau * phase)
    features[feature_index["time_cos"]] = cos(tau * phase)


def _encode_shift_state(
    features: np.ndarray,
    context: dict[str, object],
    feature_index: dict[str, int],
    config: Any,
) -> None:
    SHIFT_STATES = ("pre_shift", "on_time", "late", "absent", "post_shift")
    shift_feature_map = {
        "pre_shift": "shift_pre",
        "on_time": "shift_on_time",
        "late": "shift_late",
        "absent": "shift_absent",
        "post_shift": "shift_post",
    }
    shift_state = context.get("shift_state", "pre_shift")
    if shift_state not in SHIFT_STATES:
        shift_state = "pre_shift"
    for name, feature_name in shift_feature_map.items():
        features[feature_index[feature_name]] = 1.0 if name == shift_state else 0.0


def _encode_embedding_slot(
    features: np.ndarray, slot: int, feature_index: dict[str, int], config: Any
) -> None:
    max_slots = config.embedding_allocator.max_slots
    features[feature_index["embedding_slot_norm"]] = float(slot) / float(max_slots)
    features[feature_index["ctx_reset_flag"]] = 0.0


def _encode_episode_progress(
    features: np.ndarray,
    snapshot: AgentSnapshot,
    feature_index: dict[str, int],
    config: Any,
) -> None:
    episode_length = max(1, config.observations_config.hybrid.time_ticks_per_day)
    progress = float(getattr(snapshot, "episode_tick", 0)) / float(episode_length)
    features[feature_index["episode_progress"]] = max(0.0, min(1.0, progress))


def _encode_last_action(
    features: np.ndarray, context: dict[str, object], feature_index: dict[str, int]
) -> None:
    last_action_id = _string_or_empty(context.get("last_action_id"))
    if last_action_id:
        digest = hashlib.blake2s(last_action_id.encode("utf-8")).digest()
        value = int.from_bytes(digest[:4], "little") / float(2**32)
    else:
        value = 0.0
    features[feature_index["last_action_id_hash"]] = float(value)
    features[feature_index["last_action_success"]] = _bool_flag(
        context.get("last_action_success")
    )
    features[feature_index["last_action_duration"]] = _float_or_default(
        context.get("last_action_duration", 0.0)
    )


def _encode_environmental_flags(
    features: np.ndarray,
    world: WorldRuntimeAdapterProtocol,
    snapshot: AgentSnapshot,
    feature_index: dict[str, int],
) -> None:
    reservation_idx = feature_index.get("reservation_active")
    if reservation_idx is not None:
        reservations = world.active_reservations
        active = snapshot.agent_id in reservations.values()
        features[reservation_idx] = 1.0 if active else 0.0

    queue_idx = feature_index.get("in_queue")
    if queue_idx is not None:
        in_queue = False
        for object_id in world.objects_snapshot().keys():
            queue = world.queue_manager.queue_snapshot(object_id)
            if snapshot.agent_id in queue:
                in_queue = True
                break
        features[queue_idx] = 1.0 if in_queue else 0.0


def _encode_rivalry(
    features: np.ndarray,
    world: WorldRuntimeAdapterProtocol,
    snapshot: AgentSnapshot,
    feature_index: dict[str, int],
    config: Any,
) -> None:
    top_rivals = list(
        world.rivalry_top(
            snapshot.agent_id, limit=config.conflict.rivalry.max_edges
        )
    )
    max_rivalry = top_rivals[0][1] if top_rivals else 0.0
    avoid_threshold = config.conflict.rivalry.avoid_threshold
    avoid_count = sum(1 for _, value in top_rivals if value >= avoid_threshold)
    features[feature_index["rivalry_max"]] = float(max_rivalry)
    features[feature_index["rivalry_avoid_count"]] = float(avoid_count)


def _encode_path_hint(
    features: np.ndarray,
    world: WorldRuntimeAdapterProtocol,
    snapshot: AgentSnapshot,
    feature_index: dict[str, int],
) -> None:
    path_hint_indices = {
        "north": feature_index.get("path_hint_north"),
        "south": feature_index.get("path_hint_south"),
        "east": feature_index.get("path_hint_east"),
        "west": feature_index.get("path_hint_west"),
    }
    if not any(idx is not None for idx in path_hint_indices.values()):
        return
    target = find_nearest_object_of_type(world, "stove", snapshot.position)
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
    if path_hint_indices["north"] is not None:
        features[path_hint_indices["north"]] = north
    if path_hint_indices["south"] is not None:
        features[path_hint_indices["south"]] = south
    if path_hint_indices["east"] is not None:
        features[path_hint_indices["east"]] = east
    if path_hint_indices["west"] is not None:
        features[path_hint_indices["west"]] = west


def _encode_local_summary(
    features: np.ndarray,
    snapshot: AgentSnapshot,
    cache: LocalCache,
    feature_index: dict[str, int],
    local_summary: LocalSummary | None,
    config: Any,
) -> dict[str, float]:
    from .map import encode_map_tensor

    window = config.observations_config.hybrid.local_window
    radius = max(1, window // 2)
    if local_summary is None:
        _, local_summary = encode_map_tensor(
            channels=(), snapshot=snapshot, radius=radius, cache=cache
        )

    local_summary_indices = {
        "neighbor_agent_ratio": feature_index["neighbor_agent_ratio"],
        "neighbor_object_ratio": feature_index["neighbor_object_ratio"],
        "reserved_tile_ratio": feature_index["reserved_tile_ratio"],
        "nearest_agent_distance": feature_index["nearest_agent_distance"],
    }

    features[local_summary_indices["neighbor_agent_ratio"]] = local_summary.agent_ratio
    features[local_summary_indices["neighbor_object_ratio"]] = local_summary.object_ratio
    features[local_summary_indices["reserved_tile_ratio"]] = local_summary.reserved_ratio
    features[local_summary_indices["nearest_agent_distance"]] = (
        local_summary.nearest_agent_distance_norm
    )

    return {
        "agent_count": local_summary.agent_count,
        "object_count": local_summary.object_count,
        "reserved_tiles": local_summary.reserved_tiles,
        "radius": local_summary.radius,
        "agent_ratio": local_summary.agent_ratio,
        "object_ratio": local_summary.object_ratio,
        "reserved_ratio": local_summary.reserved_ratio,
        "nearest_agent_distance": local_summary.nearest_agent_distance,
        "nearest_agent_distance_norm": local_summary.nearest_agent_distance_norm,
    }


def _encode_landmarks(
    features: np.ndarray,
    world: WorldRuntimeAdapterProtocol,
    snapshot: AgentSnapshot,
    landmarks: list[str],
    landmark_slices: dict[str, slice],
) -> None:
    cx, cy = snapshot.position
    for landmark in landmarks:
        slice_ = landmark_slices.get(landmark)
        if slice_ is None:
            continue
        position = find_nearest_object_of_type(world, landmark, snapshot.position)
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


def _encode_personality(
    features: np.ndarray, snapshot: AgentSnapshot, feature_index: dict[str, int]
) -> dict[str, object] | None:
    personality_indices = {
        "personality_extroversion": feature_index.get("personality_extroversion"),
        "personality_forgiveness": feature_index.get("personality_forgiveness"),
        "personality_ambition": feature_index.get("personality_ambition"),
    }
    if not any(idx is not None for idx in personality_indices.values()):
        return None

    personality = getattr(snapshot, "personality", None)
    extroversion = float(getattr(personality, "extroversion", 0.0))
    forgiveness = float(getattr(personality, "forgiveness", 0.0))
    ambition = float(getattr(personality, "ambition", 0.0))

    if personality_indices["personality_extroversion"] is not None:
        features[personality_indices["personality_extroversion"]] = extroversion
    if personality_indices["personality_forgiveness"] is not None:
        features[personality_indices["personality_forgiveness"]] = forgiveness
    if personality_indices["personality_ambition"] is not None:
        features[personality_indices["personality_ambition"]] = ambition

    profile_name = str(getattr(snapshot, "personality_profile", "") or "balanced")
    metadata: dict[str, object] = {
        "profile": profile_name,
        "traits": {
            "extroversion": extroversion,
            "forgiveness": forgiveness,
            "ambition": ambition,
        },
    }

    try:
        profile = PersonalityProfiles.get(profile_name)
    except KeyError:
        profile = None

    if profile is not None:
        metadata["multipliers"] = {
            "needs": dict(profile.need_multipliers),
            "rewards": dict(profile.reward_bias),
            "behaviour": dict(profile.behaviour_bias),
        }

    return metadata


__all__ = ["encode_feature_vector"]
