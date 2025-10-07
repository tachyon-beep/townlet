"""Snapshot and diff builders for telemetry aggregation."""

from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from townlet.telemetry.transform.normalizers import normalize_snapshot_payload

__all__ = ["StreamPayloadBuilder"]


@dataclass
class StreamPayloadBuilder:
    """Build streaming telemetry payloads and optional diffs."""

    schema_version: str
    diff_enabled: bool = False
    _previous_snapshot: dict[str, Any] | None = field(default=None, init=False, repr=False)

    def build(
        self,
        *,
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
        """Return the payload for the given tick, applying diffs when enabled."""

        snapshot = normalize_snapshot_payload(
            schema_version=self.schema_version,
            tick=tick,
            runtime_variant=runtime_variant,
            queue_metrics=queue_metrics,
            embedding_metrics=embedding_metrics,
            employment_metrics=employment_metrics,
            conflict_snapshot=conflict_snapshot,
            relationship_metrics=relationship_metrics,
            relationship_snapshot=relationship_snapshot,
            relationship_updates=relationship_updates,
            relationship_overlay=relationship_overlay,
            events=events,
            narrations=narrations,
            job_snapshot=job_snapshot,
            economy_snapshot=economy_snapshot,
            economy_settings=economy_settings,
            price_spikes=price_spikes,
            utilities=utilities,
            affordance_manifest=affordance_manifest,
            reward_breakdown=reward_breakdown,
            stability_metrics=stability_metrics,
            stability_alerts=stability_alerts,
            stability_inputs=stability_inputs,
            promotion=promotion,
            perturbations=perturbations,
            policy_identity=policy_identity,
            policy_snapshot=policy_snapshot,
            anneal_status=anneal_status,
            kpi_history=kpi_history,
        )
        if not self.diff_enabled:
            return snapshot
        return self._apply_diff(snapshot)

    def _apply_diff(self, payload: dict[str, Any]) -> dict[str, Any]:
        snapshot = copy.deepcopy(payload)
        if self._previous_snapshot is None:
            self._previous_snapshot = snapshot
            initial = dict(snapshot)
            initial["payload_type"] = "snapshot"
            return initial

        previous = self._previous_snapshot
        changes: dict[str, Any] = {}
        for key, value in snapshot.items():
            if key not in previous or previous[key] != value:
                changes[str(key)] = value
        removed = [str(key) for key in previous.keys() if key not in snapshot]

        self._previous_snapshot = snapshot

        changes.pop("schema_version", None)
        changes.pop("tick", None)
        changes.pop("payload_type", None)

        diff_payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "tick": snapshot.get("tick"),
            "payload_type": "diff",
            "changes": changes,
        }
        if removed:
            diff_payload["removed"] = removed
        return diff_payload

    def reset(self) -> None:
        """Reset diff tracking state (used after imports)."""

        self._previous_snapshot = None
