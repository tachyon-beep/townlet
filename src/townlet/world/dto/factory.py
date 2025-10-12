"""Helpers that convert legacy observations into DTO envelopes."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Tuple, cast

import numpy as np

from townlet.world.actions import Action

from .observation import (
    AgentObservationDTO,
    GlobalObservationDTO,
    ObservationEnvelope,
)


def build_observation_envelope(
    *,
    tick: int,
    observations: Mapping[str, Mapping[str, Any]],
    actions: Mapping[str, Any] | None,
    terminated: Mapping[str, bool],
    termination_reasons: Mapping[str, str],
    queue_metrics: Mapping[str, int],
    rewards: Mapping[str, float],
    reward_breakdown: Mapping[str, Mapping[str, float]],
    perturbations: Mapping[str, Any],
    policy_snapshot: Mapping[str, Any],
    policy_metadata: Mapping[str, Any],
    rivalry_events: Sequence[Mapping[str, Any]],
    stability_metrics: Mapping[str, Any],
    promotion_state: Mapping[str, Any] | None,
    rng_seed: int | None,
    queues: Mapping[str, Any] | None = None,
    running_affordances: Mapping[str, Any] | None = None,
    relationship_snapshot: Mapping[str, Any] | None = None,
    relationship_metrics: Mapping[str, Any] | None = None,
    agent_snapshots: Mapping[str, Any] | None = None,
    job_snapshot: Mapping[str, Any] | None = None,
    queue_affinity_metrics: Mapping[str, Any] | None = None,
    employment_snapshot: Mapping[str, Any] | None = None,
    economy_snapshot: Mapping[str, Any] | None = None,
    anneal_context: Mapping[str, Any] | None = None,
    agent_contexts: Mapping[str, Mapping[str, Any]] | None = None,
    ) -> ObservationEnvelope:
    """Build an observation envelope ready for policy/telemetry consumers."""

    agent_ids = sorted(observations.keys())
    agent_dtos: list[AgentObservationDTO] = []

    active_lookup: dict[str, str] = {}
    queue_entries: dict[str, list[Mapping[str, Any]]] = {}
    cooldown_entries: list[Mapping[str, Any]] = []
    if isinstance(queues, Mapping):
        active_lookup = {
            str(object_id): str(agent)
            for object_id, agent in _iter_mapping(queues.get("active", {}))
        }
        queue_payload = queues.get("queues", {})
        if isinstance(queue_payload, Mapping):
            queue_entries = {}
            for object_id, entries in queue_payload.items():
                if not isinstance(entries, Iterable):
                    continue
                cleaned: list[Mapping[str, Any]] = []
                for entry in entries:
                    if isinstance(entry, Mapping):
                        cleaned.append({str(k): _to_builtin(v) for k, v in entry.items()})
                if cleaned:
                    queue_entries[str(object_id)] = cleaned
        cooldown_entries = []
        for entry in queues.get("cooldowns", []) or []:
            if isinstance(entry, Mapping):
                cooldown_entries.append(
                    {
                        "object_id": str(entry.get("object_id", "")),
                        "expiry": int(entry.get("expiry", 0)),
                        "agent_id": str(entry.get("agent_id", "")),
                    }
                )

    for agent_id in agent_ids:
        payload = observations.get(agent_id, {})
        map_tensor = _coerce_ndarray(payload.get("map"))
        features = _coerce_ndarray(payload.get("features"))
        metadata = _to_builtin(payload.get("metadata", {}))
        agent_rewards = reward_breakdown.get(agent_id)
        if agent_rewards is not None:
            rewards_dict = {
                str(component): float(value)
                for component, value in _iter_mapping(agent_rewards)
            }
        else:
            rewards_dict = None

        snapshot = agent_snapshots.get(agent_id) if agent_snapshots else None
        context = agent_contexts.get(agent_id) if agent_contexts else None

        needs_payload: Mapping[str, float] | None = None
        wallet_value: float | None = None
        inventory_payload: Mapping[str, Any] | None = None
        position_payload: Sequence[float] | None = None
        personality_payload: Mapping[str, Any] | None = None
        job_payload: Mapping[str, Any] | None = None

        if snapshot is not None:
            needs_payload = {
                str(key): float(value)
                for key, value in getattr(snapshot, "needs", {}).items()
            }
            wallet_value = float(getattr(snapshot, "wallet", 0.0))
            inventory = getattr(snapshot, "inventory", None)
            if isinstance(inventory, Mapping):
                inventory_payload = {
                    str(key): _to_builtin(value) for key, value in inventory.items()
                }
            position = getattr(snapshot, "position", None)
            if position is not None and len(position) >= 2:
                try:
                    position_payload = [float(position[0]), float(position[1])]
                except Exception:
                    position_payload = None
            personality = getattr(snapshot, "personality", None)
            if _is_dataclass_instance(personality):
                personality_payload = {
                    str(key): _to_builtin(val)
                    for key, val in asdict(personality).items()  # type: ignore[arg-type]
                }
            if job_snapshot and agent_id in job_snapshot:
                job_payload = _to_builtin(job_snapshot[agent_id])
            else:
                job_payload = {
                    "job_id": getattr(snapshot, "job_id", None),
                    "on_shift": bool(getattr(snapshot, "on_shift", False)),
                    "shift_state": getattr(snapshot, "shift_state", None),
                    "lateness_counter": int(getattr(snapshot, "lateness_counter", 0)),
                    "attendance_ratio": float(getattr(snapshot, "attendance_ratio", 0.0)),
                    "exit_pending": bool(getattr(snapshot, "exit_pending", False)),
                }

        queue_state = _build_queue_state(
            agent_id=agent_id,
            active_lookup=active_lookup,
            queue_entries=queue_entries,
            cooldown_entries=cooldown_entries,
        )

        pending_intent = None
        if context and "pending_intent" in context:
            pending_intent = _to_builtin(context["pending_intent"])

        agent_dtos.append(
            AgentObservationDTO(
                agent_id=agent_id,
                map=map_tensor,
                features=features,
                metadata=metadata,
                rewards=rewards_dict,
                terminated=bool(terminated.get(agent_id, False))
                if terminated
                else None,
                position=position_payload,
                needs=needs_payload,
                wallet=wallet_value,
                inventory=inventory_payload,
                job=job_payload,
                personality=personality_payload,
                queue_state=queue_state,
                pending_intent=pending_intent,
            )
        )

    global_context = GlobalObservationDTO(
        queue_metrics={
            str(key): int(value) for key, value in _iter_mapping(queue_metrics)
        },
        rewards={
            str(agent_id): {
                str(component): float(value)
                for component, value in _iter_mapping(breakdown)
            }
    for agent_id, breakdown in _iter_mapping(reward_breakdown)
        },
        perturbations=_to_builtin(perturbations),
        policy_snapshot=_to_builtin(policy_snapshot),
        rivalry_events=[_to_builtin(event) for event in rivalry_events],
        stability_metrics=_to_builtin(stability_metrics),
        promotion_state=_to_builtin(promotion_state) if promotion_state else None,
        policy_metadata=_to_builtin(policy_metadata),
        rng_seed=int(rng_seed) if isinstance(rng_seed, (int, np.integer)) else rng_seed,
        queues=_to_builtin(queues) if queues is not None else {},
        running_affordances=_to_builtin(running_affordances) if running_affordances is not None else {},
        relationship_snapshot=_to_builtin(relationship_snapshot) if relationship_snapshot is not None else {},
        relationship_metrics=_to_builtin(relationship_metrics) if relationship_metrics is not None else {},
        employment_snapshot=_to_builtin(employment_snapshot) if employment_snapshot is not None else {},
        queue_affinity_metrics=_to_builtin(queue_affinity_metrics) if queue_affinity_metrics is not None else {},
        economy_snapshot=_to_builtin(economy_snapshot) if economy_snapshot is not None else {},
        anneal_context=_to_builtin(anneal_context) if anneal_context is not None else {},
    )

    actions_payload = (
        {str(agent_id): _to_builtin(action) for agent_id, action in _iter_mapping(actions)}
        if actions
        else {}
    )

    terminated_payload = {
        str(agent_id): bool(value) for agent_id, value in _iter_mapping(terminated)
    }
    termination_reasons_payload = {
        str(agent_id): str(reason)
        for agent_id, reason in _iter_mapping(termination_reasons)
    }

    return ObservationEnvelope.model_construct(
        tick=int(tick),
        agents=agent_dtos,
        global_context=global_context,
        actions=actions_payload,
        terminated=terminated_payload,
        termination_reasons=termination_reasons_payload,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _coerce_ndarray(value: Any) -> Sequence[Any] | None:
    if value is None:
        return None
    if isinstance(value, np.ndarray):
        return cast(Sequence[Any], value.tolist())
    if isinstance(value, (list, tuple)):
        return [_to_builtin(item) for item in value]
    coerced = _to_builtin(value)
    if coerced is None:
        return None
    if isinstance(coerced, (list, tuple)):
        return [_to_builtin(item) for item in coerced]
    return [coerced]


def _iter_mapping(value: Mapping[str, Any] | None) -> Tuple[tuple[Any, Any], ...]:
    if not value or not isinstance(value, Mapping):
        return ()
    try:
        return tuple(sorted(value.items(), key=lambda item: str(item[0])))
    except TypeError:
        return tuple(value.items())


def _is_dataclass_instance(value: Any) -> bool:
    return is_dataclass(value) and not isinstance(value, type)


def _to_builtin(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, bool)):
        return value
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if _is_dataclass_instance(value):
        return {str(key): _to_builtin(val) for key, val in asdict(value).items()}
    if isinstance(value, Action):
        return {
            "agent_id": value.agent_id,
            "kind": value.kind,
            "payload": _to_builtin(value.payload),
        }
    if hasattr(value, "to_dict") and callable(value.to_dict):
        try:
            return _to_builtin(value.to_dict())
        except Exception:  # pragma: no cover - defensive
            return str(value)
    if isinstance(value, Mapping):
        items = _iter_mapping(value)
        return {str(key): _to_builtin(val) for key, val in items}
    if isinstance(value, set):
        return sorted(_to_builtin(item) for item in value)
    if isinstance(value, Sequence):
        return [_to_builtin(item) for item in value]
    return value


__all__ = ["build_observation_envelope"]


def _build_queue_state(
    *,
    agent_id: str,
    active_lookup: Mapping[str, str],
    queue_entries: Mapping[str, Sequence[Mapping[str, Any]]],
    cooldown_entries: Sequence[Mapping[str, Any]],
) -> Mapping[str, Any] | None:
    active_objects = [
        object_id for object_id, occupant in active_lookup.items() if occupant == agent_id
    ]
    queue_memberships: list[Mapping[str, Any]] = []
    for object_id, entries in queue_entries.items():
        if not entries:
            continue
        for index, entry in enumerate(entries):
            entry_agent = entry.get("agent_id") or entry.get("agent")
            if str(entry_agent) == agent_id:
                queue_memberships.append(
                    {
                        "object_id": object_id,
                        "position": int(index),
                        "joined_tick": int(entry.get("joined_tick", 0)),
                    }
                )
    cooldowns = [
        {
            "object_id": str(entry.get("object_id", "")),
            "expiry": int(entry.get("expiry", 0)),
        }
        for entry in cooldown_entries
        if str(entry.get("agent_id", "")) == agent_id
    ]
    if not (active_objects or queue_memberships or cooldowns):
        return None
    return {
        "active_objects": active_objects,
        "queue_memberships": queue_memberships,
        "cooldowns": cooldowns,
    }
