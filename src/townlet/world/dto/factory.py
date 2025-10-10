"""Helpers that convert legacy observations into DTO envelopes."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, is_dataclass
from typing import Any

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
) -> ObservationEnvelope:
    """Build an observation envelope ready for policy/telemetry consumers."""

    agent_ids = sorted(observations.keys())
    agent_dtos: list[AgentObservationDTO] = []
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

    return ObservationEnvelope(
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
        return value.tolist()
    if isinstance(value, (list, tuple)):
        return [_to_builtin(item) for item in value]
    return _to_builtin(value)


def _iter_mapping(value: Mapping[str, Any] | None) -> Sequence[tuple[Any, Any]]:
    if not value or not isinstance(value, Mapping):
        return ()
    try:
        return tuple(sorted(value.items(), key=lambda item: str(item[0])))
    except TypeError:
        return tuple(value.items())


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
    if is_dataclass(value):
        return _to_builtin(asdict(value))
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
