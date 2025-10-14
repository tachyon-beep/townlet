"""Social snippet encoding for relationships and embeddings."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, cast

import numpy as np

if TYPE_CHECKING:
    from townlet.world.agents.snapshot import AgentSnapshot
    from townlet.world.observations.interfaces import WorldRuntimeAdapterProtocol


def _float_or_default(value: object, default: float = 0.0) -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def _string_or_empty(value: object) -> str:
    return value if isinstance(value, str) else ""


def encode_social_vector(
    *,
    world: WorldRuntimeAdapterProtocol,
    snapshot: AgentSnapshot,
    social_cfg: Any,  # SocialSnippetConfig
    config: Any,  # SimulationConfig
) -> tuple[np.ndarray, dict[str, object]]:
    """
    Encode social relationships into a fixed-length vector.

    The social vector contains:
    - Top friends (sorted by trust + familiarity)
    - Top rivals (sorted by rivalry, excluding friends)
    - Each slot: [embedding (N dims), trust, familiarity, rivalry]
    - Optional aggregates: trust_mean, trust_max, rivalry_mean, rivalry_max

    Args:
        world: World adapter
        snapshot: Agent state snapshot
        social_cfg: Social snippet configuration
        config: Simulation config (for relationships gate check)

    Returns:
        (vector, context) where vector is (N,) and context contains metadata
    """
    social_slots = max(0, social_cfg.top_friends + social_cfg.top_rivals)
    if social_slots and config.features.stages.relationships == "OFF":
        raise ValueError("Social snippet requires relationships stage enabled")

    slot_dim = social_cfg.embed_dim + 3  # embedding + trust/fam/rivalry
    social_vector_length = social_slots * slot_dim
    if social_cfg.include_aggregates:
        social_vector_length += 4  # trust_mean, trust_max, rivalry_mean, rivalry_max

    if social_slots == 0:
        empty_vector = np.zeros(social_vector_length, dtype=np.float32)
        return empty_vector, {
            "configured_slots": 0,
            "slot_dim": slot_dim,
            "aggregates": _aggregate_names(social_cfg),
            "filled_slots": 0,
            "relation_source": "disabled",
            "has_data": False,
        }

    vector = np.zeros(social_vector_length, dtype=np.float32)
    slot_values, slot_context = _collect_social_slots(
        world, snapshot, social_cfg, config
    )
    offset = 0
    for slot in slot_values:
        embed_vector = np.asarray(slot.get("embedding", ()), dtype=np.float32)
        if embed_vector.shape[0] != social_cfg.embed_dim:
            embed_vector = np.resize(embed_vector, social_cfg.embed_dim)
        vector[offset : offset + social_cfg.embed_dim] = embed_vector
        offset += social_cfg.embed_dim
        vector[offset] = _float_or_default(slot.get("trust", 0.0))
        offset += 1
        vector[offset] = _float_or_default(slot.get("familiarity", 0.0))
        offset += 1
        vector[offset] = _float_or_default(slot.get("rivalry", 0.0))
        offset += 1

    if social_cfg.include_aggregates:
        trust_values = [
            _float_or_default(slot.get("trust", 0.0))
            for slot in slot_values
            if bool(slot.get("valid"))
        ]
        rivalry_values = [
            _float_or_default(slot.get("rivalry", 0.0))
            for slot in slot_values
            if bool(slot.get("valid"))
        ]
        aggregates = _compute_aggregates(trust_values, rivalry_values)
        for value in aggregates:
            if offset < len(vector):
                vector[offset] = value
                offset += 1

    valid_slots = sum(1 for slot in slot_values if bool(slot.get("valid")))
    slot_context.update(
        {
            "configured_slots": social_slots,
            "slot_dim": slot_dim,
            "aggregates": _aggregate_names(social_cfg),
            "filled_slots": valid_slots,
            "has_data": bool(valid_slots),
        }
    )
    return vector, slot_context


def _collect_social_slots(
    world: WorldRuntimeAdapterProtocol,
    snapshot: AgentSnapshot,
    social_cfg: Any,
    config: Any,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    total_slots = max(0, social_cfg.top_friends + social_cfg.top_rivals)
    context: dict[str, object] = {
        "relation_source": "disabled" if total_slots == 0 else "empty",
    }
    if total_slots == 0:
        return [], context

    relations, relation_source = _resolve_relationships(
        world, snapshot.agent_id, social_cfg
    )
    context["relation_source"] = relation_source
    friend_candidates = sorted(
        relations,
        key=lambda entry: _float_or_default(entry.get("trust", 0.0))
        + _float_or_default(entry.get("familiarity", 0.0)),
        reverse=True,
    )
    rival_candidates = sorted(
        relations,
        key=lambda entry: _float_or_default(entry.get("rivalry", 0.0)),
        reverse=True,
    )

    friends = friend_candidates[: social_cfg.top_friends]
    rivals: list[dict[str, object]] = []
    for entry in rival_candidates:
        if entry in friends:
            continue
        rivals.append(entry)
        if len(rivals) >= social_cfg.top_rivals:
            break

    slots: list[dict[str, object]] = []
    for entry in friends + rivals:
        slots.append(_encode_relationship(entry, social_cfg))

    while len(slots) < total_slots:
        slots.append(_empty_relationship_entry(social_cfg))

    return slots[:total_slots], context


def _resolve_relationships(
    world: WorldRuntimeAdapterProtocol, agent_id: str, social_cfg: Any
) -> tuple[list[dict[str, object]], str]:
    snapshot_getter = getattr(world, "relationships_snapshot", None)
    relationships: dict[str, dict[str, object]] = {}
    if callable(snapshot_getter):
        data = snapshot_getter()
        if isinstance(data, dict):
            candidate = data.get(agent_id, {}) or {}
            if isinstance(candidate, dict):
                relationships = candidate

    entries: list[dict[str, object]] = []
    for other_id, metrics in relationships.items():
        # metrics is guaranteed to be Mapping due to relationships type
        entries.append(
            {
                "other_id": str(other_id),
                "trust": _float_or_default(metrics.get("trust", 0.0)),
                "familiarity": _float_or_default(metrics.get("familiarity", 0.0)),
                "rivalry": _float_or_default(metrics.get("rivalry", 0.0)),
            }
        )

    if entries:
        return entries, "relationships"

    # Fallback to rivalry ledger
    rivalry_data = list(world.rivalry_top(agent_id, limit=social_cfg.top_rivals))
    fallback_entries = []
    for other_id, rivalry in rivalry_data:
        fallback_entries.append(
            {
                "other_id": str(other_id),
                "trust": 0.0,
                "familiarity": 0.0,
                "rivalry": float(rivalry),
            }
        )
    if fallback_entries:
        return fallback_entries, "rivalry_fallback"
    return [], "empty"


def _encode_relationship(
    entry: Mapping[str, object], social_cfg: Any
) -> dict[str, object]:
    other_id = _string_or_empty(entry.get("other_id"))
    embedding = _embed_agent_id(other_id, social_cfg.embed_dim)
    return {
        "embedding": embedding,
        "trust": _float_or_default(entry.get("trust", 0.0)),
        "familiarity": _float_or_default(entry.get("familiarity", 0.0)),
        "rivalry": _float_or_default(entry.get("rivalry", 0.0)),
        "valid": True,
    }


def _empty_relationship_entry(social_cfg: Any) -> dict[str, object]:
    return {
        "embedding": np.zeros(social_cfg.embed_dim, dtype=np.float32),
        "trust": 0.0,
        "familiarity": 0.0,
        "rivalry": 0.0,
        "valid": False,
    }


def _embed_agent_id(other_id: str, embed_dim: int) -> np.ndarray:
    digest = hashlib.blake2s(other_id.encode("utf-8")).digest()
    values = np.frombuffer(digest, dtype=np.uint8)
    floats = values.astype(np.float32) / 255.0
    repeats = int(np.ceil(embed_dim / floats.size))
    tiled = np.tile(floats, repeats)
    return tiled[:embed_dim]


def _compute_aggregates(
    trust_values: Iterable[float], rivalry_values: Iterable[float]
) -> tuple[float, float, float, float]:
    trust_list = list(trust_values)
    rivalry_list = list(rivalry_values)
    trust_mean = float(np.mean(trust_list)) if trust_list else 0.0
    trust_max = float(np.max(trust_list)) if trust_list else 0.0
    rivalry_mean = float(np.mean(rivalry_list)) if rivalry_list else 0.0
    rivalry_max = float(np.max(rivalry_list)) if rivalry_list else 0.0
    return trust_mean, trust_max, rivalry_mean, rivalry_max


def _aggregate_names(social_cfg: Any) -> list[str]:
    if social_cfg.include_aggregates:
        return [
            "social_trust_mean",
            "social_trust_max",
            "social_rivalry_mean",
            "social_rivalry_max",
        ]
    return []


__all__ = ["encode_social_vector"]
