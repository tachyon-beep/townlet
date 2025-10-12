"""Telemetry payload normalization helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

__all__ = [
    "copy_relationship_snapshot",
    "normalize_perturbations_payload",
    "normalize_snapshot_payload",
]


def copy_relationship_snapshot(
    snapshot: Mapping[str, Mapping[str, Mapping[str, float]]],
) -> dict[str, dict[str, dict[str, float]]]:
    """Return a deep copy of the relationship snapshot with numeric coercion."""

    copied: dict[str, dict[str, dict[str, float]]] = {}
    for owner, ties in snapshot.items():
        owner_key = str(owner)
        owner_snapshot: dict[str, dict[str, float]] = {}
        if isinstance(ties, Mapping):
            for other, values in ties.items():
                if not isinstance(values, Mapping):
                    continue
                owner_snapshot[str(other)] = {
                    "trust": float(values.get("trust", 0.0)),
                    "familiarity": float(values.get("familiarity", 0.0)),
                    "rivalry": float(values.get("rivalry", 0.0)),
                }
        copied[owner_key] = owner_snapshot
    return copied


def normalize_perturbations_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Coerce perturbation payloads into a stable schema for telemetry."""

    active = payload.get("active", {})
    pending = payload.get("pending", [])
    cooldowns = payload.get("cooldowns", {})

    active_map: dict[str, dict[str, Any]] = {}
    if isinstance(active, Mapping):
        active_map = {
            str(event_id): dict(entry)
            for event_id, entry in active.items()
            if isinstance(entry, Mapping)
        }

    pending_list: list[dict[str, Any]] = []
    if isinstance(pending, list):
        pending_list = [dict(entry) for entry in pending if isinstance(entry, Mapping)]

    spec_cd: dict[str, int] = {}
    agent_cd: dict[str, int] = {}
    if isinstance(cooldowns, Mapping):
        spec_payload = cooldowns.get("spec", {})
        if isinstance(spec_payload, Mapping):
            spec_cd = {
                str(name): int(expiry)
                for name, expiry in spec_payload.items()
                if isinstance(expiry, int)
            }
        agent_payload = cooldowns.get("agents", {})
        if isinstance(agent_payload, Mapping):
            agent_cd = {
                str(agent): int(expiry)
                for agent, expiry in agent_payload.items()
                if isinstance(expiry, int)
            }

    return {
        "active": active_map,
        "pending": pending_list,
        "cooldowns": {"spec": spec_cd, "agents": agent_cd},
    }


def normalize_snapshot_payload(
    *,
    schema_version: str,
    tick: int,
    runtime_variant: str | None,
    queue_metrics: Mapping[str, Any] | None,
    embedding_metrics: Mapping[str, Any] | None,
    employment_metrics: Mapping[str, Any] | None,
    conflict_snapshot: Mapping[str, Any],
    relationship_metrics: Mapping[str, Any] | None,
    relationship_snapshot: Mapping[str, Mapping[str, Mapping[str, float]]],
    relationship_updates: Iterable[Mapping[str, Any]],
    relationship_overlay: Mapping[str, Iterable[Mapping[str, Any]]],
    events: Iterable[Mapping[str, Any]],
    narrations: Iterable[Mapping[str, Any]],
    job_snapshot: Mapping[str, Mapping[str, Any]],
    economy_snapshot: Mapping[str, Mapping[str, Any]],
    economy_settings: Mapping[str, Any],
    price_spikes: Mapping[str, Mapping[str, Any]],
    utilities: Mapping[str, Any],
    affordance_manifest: Mapping[str, Any],
    reward_breakdown: Mapping[str, Mapping[str, Any]],
    stability_metrics: Mapping[str, Any],
    stability_alerts: Iterable[Any],
    stability_inputs: Mapping[str, Any],
    promotion: Mapping[str, Any] | None,
    perturbations: Mapping[str, Any],
    policy_identity: Mapping[str, Any] | None,
    policy_snapshot: Mapping[str, Mapping[str, Any]],
    anneal_status: Mapping[str, Any] | None,
    kpi_history: Mapping[str, Iterable[Any]],
) -> dict[str, Any]:
    """Normalise a snapshot payload into the canonical telemetry schema."""

    alerts_list: list[Any] = []
    for alert in stability_alerts:
        if isinstance(alert, Mapping):
            alerts_list.append(dict(alert))
        else:
            alerts_list.append(alert)

    payload: dict[str, Any] = {
        "schema_version": schema_version,
        "tick": int(tick),
        "runtime_variant": runtime_variant,
        "queue_metrics": dict(queue_metrics or {}),
        "embedding_metrics": dict(embedding_metrics or {}),
        "employment": dict(employment_metrics or {}),
        "conflict": dict(conflict_snapshot),
        "relationships": dict(relationship_metrics or {}),
        "relationship_snapshot": copy_relationship_snapshot(relationship_snapshot),
        "relationship_updates": [dict(entry) for entry in relationship_updates],
        "relationship_overlay": {
            str(owner): [dict(item) for item in entries]
            for owner, entries in (relationship_overlay or {}).items()
        },
        "events": [dict(entry) for entry in events],
        "narrations": [dict(entry) for entry in narrations],
        "jobs": {
            str(agent_id): dict(snapshot)
            for agent_id, snapshot in job_snapshot.items()
        },
        "economy": {
            str(object_id): dict(obj)
            for object_id, obj in economy_snapshot.items()
        },
        "economy_settings": {str(key): value for key, value in economy_settings.items()},
        "price_spikes": {
            str(event_id): {
                "magnitude": float(details.get("magnitude", 0.0)),
                "targets": list(details.get("targets", ())),
            }
            for event_id, details in price_spikes.items()
            if isinstance(details, Mapping)
        },
        "utilities": {str(name): bool(state) for name, state in utilities.items()},
        "affordance_manifest": dict(affordance_manifest),
        "reward_breakdown": {
            str(agent): {str(name): float(value) for name, value in components.items()}
            for agent, components in reward_breakdown.items()
        },
        "stability": {
            "metrics": dict(stability_metrics),
            "alerts": alerts_list,
            "inputs": dict(stability_inputs),
        },
        "promotion": dict(promotion) if promotion else None,
        "perturbations": dict(perturbations),
        "policy_identity": dict(policy_identity or {}),
        "policy_snapshot": {
            str(agent): dict(data)
            for agent, data in policy_snapshot.items()
        },
        "anneal_status": dict(anneal_status) if anneal_status else None,
        "kpi_history": {
            str(name): list(values)
            for name, values in kpi_history.items()
        },
    }
    return payload
