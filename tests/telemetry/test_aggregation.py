from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

import pytest

from townlet.telemetry.aggregation import StreamPayloadBuilder, TelemetryAggregator


@dataclass
class _SnapshotInputs:
    tick: int = 1
    runtime_variant: str | None = "facade"
    queue_metrics: Mapping[str, int] | None = None
    embedding_metrics: Mapping[str, float] | None = None
    employment_metrics: Mapping[str, object] | None = None
    conflict_snapshot: Mapping[str, object] | None = None
    relationship_metrics: Mapping[str, object] | None = None
    relationship_snapshot: Mapping[str, Mapping[str, Mapping[str, float]]] | None = None
    relationship_updates: Iterable[Mapping[str, object]] | None = None
    relationship_overlay: Mapping[str, Iterable[Mapping[str, object]]] | None = None
    events: Iterable[Mapping[str, object]] | None = None
    narrations: Iterable[Mapping[str, object]] | None = None
    job_snapshot: Mapping[str, Mapping[str, object]] | None = None
    economy_snapshot: Mapping[str, Mapping[str, object]] | None = None
    economy_settings: Mapping[str, object] | None = None
    price_spikes: Mapping[str, Mapping[str, object]] | None = None
    utilities: Mapping[str, bool] | None = None
    affordance_manifest: Mapping[str, object] | None = None
    reward_breakdown: Mapping[str, Mapping[str, float]] | None = None
    stability_metrics: Mapping[str, object] | None = None
    stability_alerts: Iterable[Mapping[str, object]] | None = None
    stability_inputs: Mapping[str, object] | None = None
    promotion: Mapping[str, object] | None = None
    perturbations: Mapping[str, object] | None = None
    policy_identity: Mapping[str, object] | None = None
    policy_snapshot: Mapping[str, Mapping[str, object]] | None = None
    anneal_status: Mapping[str, object] | None = None
    kpi_history: Mapping[str, Iterable[float]] | None = None

    def apply_defaults(self) -> None:
        self.queue_metrics = self.queue_metrics or {"cooldown_events": 0}
        self.embedding_metrics = self.embedding_metrics or {"allocations_total": 0.0}
        self.employment_metrics = self.employment_metrics or {"pending_count": 0}
        self.conflict_snapshot = self.conflict_snapshot or {
            "queues": {"cooldown_events": 0},
            "queue_history": [],
            "rivalry": {},
            "rivalry_events": [],
        }
        self.relationship_metrics = self.relationship_metrics or {"total": 0}
        self.relationship_snapshot = self.relationship_snapshot or {}
        self.relationship_updates = self.relationship_updates or ()
        self.relationship_overlay = self.relationship_overlay or {}
        self.events = self.events or ()
        self.narrations = self.narrations or ()
        self.job_snapshot = self.job_snapshot or {}
        self.economy_snapshot = self.economy_snapshot or {}
        self.economy_settings = self.economy_settings or {"wage_income": 0.1}
        self.price_spikes = self.price_spikes or {}
        self.utilities = self.utilities or {"power": True}
        self.affordance_manifest = self.affordance_manifest or {"affordance_count": 0}
        self.reward_breakdown = self.reward_breakdown or {}
        self.stability_metrics = self.stability_metrics or {}
        self.stability_alerts = self.stability_alerts or ()
        self.stability_inputs = self.stability_inputs or {}
        self.perturbations = self.perturbations or {"active": {}}
        self.policy_identity = self.policy_identity or {}
        self.policy_snapshot = self.policy_snapshot or {}
        self.kpi_history = self.kpi_history or {}

    def to_global_context(self) -> dict[str, Any]:
        ctx: dict[str, Any] = {}
        if self.queue_metrics is not None:
            ctx["queue_metrics"] = dict(self.queue_metrics)
        if self.relationship_metrics is not None:
            ctx["relationship_metrics"] = dict(self.relationship_metrics)
        if self.relationship_snapshot is not None:
            ctx["relationship_snapshot"] = {
                owner: {
                    other: dict(metrics) for other, metrics in ties.items() if isinstance(metrics, Mapping)
                }
                for owner, ties in self.relationship_snapshot.items()
                if isinstance(ties, Mapping)
            }
        if self.job_snapshot is not None:
            ctx["job_snapshot"] = {
                agent: dict(snapshot)
                for agent, snapshot in self.job_snapshot.items()
                if isinstance(snapshot, Mapping)
            }
        if self.economy_snapshot is not None:
            ctx["economy_snapshot"] = {
                key: dict(snapshot)
                for key, snapshot in self.economy_snapshot.items()
                if isinstance(snapshot, Mapping)
            }
        if self.economy_settings is not None:
            ctx["economy_settings"] = dict(self.economy_settings)
        if self.price_spikes is not None:
            ctx["price_spikes"] = {
                key: dict(snapshot)
                for key, snapshot in self.price_spikes.items()
                if isinstance(snapshot, Mapping)
            }
        if self.utilities is not None:
            ctx["utilities"] = dict(self.utilities)
        if self.employment_metrics is not None:
            ctx["employment_snapshot"] = dict(self.employment_metrics)
        if self.stability_metrics is not None:
            ctx["stability_metrics"] = dict(self.stability_metrics)
        if self.perturbations is not None:
            ctx["perturbations"] = dict(self.perturbations)
        if self.promotion is not None:
            ctx["promotion_state"] = dict(self.promotion)
        if self.anneal_status is not None:
            ctx["anneal_context"] = dict(self.anneal_status)
        return ctx


class _RecordingAggregator(TelemetryAggregator):
    def __init__(self, builder: StreamPayloadBuilder) -> None:
        self.events: list[dict[str, object]] = []
        super().__init__(builder)

    def collect_tick(self, *args, **kwargs):
        events = list(super().collect_tick(*args, **kwargs))
        self.events.extend(event.payload for event in events)
        return events


@pytest.fixture()
def builder() -> StreamPayloadBuilder:
    return StreamPayloadBuilder(schema_version="1.0.0", diff_enabled=False)


@pytest.fixture()
def aggregator(builder: StreamPayloadBuilder) -> _RecordingAggregator:
    return _RecordingAggregator(builder)


def test_collect_tick_builds_snapshot(aggregator: _RecordingAggregator) -> None:
    inputs = _SnapshotInputs()
    inputs.apply_defaults()
    global_context = inputs.to_global_context()

    list(
        aggregator.collect_tick(
            tick=inputs.tick,
            world=None,
            rewards={},
            events=inputs.events,
            policy_snapshot=inputs.policy_snapshot,
            kpi_history=True,
            reward_breakdown=inputs.reward_breakdown,
            stability_inputs=inputs.stability_inputs,
            perturbations=inputs.perturbations,
            policy_identity=inputs.policy_identity,
            possessed_agents=(),
            social_events=inputs.events,
            runtime_variant=inputs.runtime_variant,
            conflict_snapshot=inputs.conflict_snapshot,
            relationship_updates=inputs.relationship_updates,
            relationship_overlay=inputs.relationship_overlay,
            narrations=inputs.narrations,
            affordance_manifest=inputs.affordance_manifest,
            stability_metrics=inputs.stability_metrics,
            stability_alerts=inputs.stability_alerts,
            promotion=inputs.promotion,
            anneal_status=inputs.anneal_status,
            kpi_history_payload=inputs.kpi_history,
            embedding_metrics=inputs.embedding_metrics,
            global_context=global_context,
        )
    )

    assert len(aggregator.events) == 1
    payload = aggregator.events[0]
    assert payload["tick"] == inputs.tick
    assert payload["schema_version"] == "1.0.0"
    assert payload["queue_metrics"] == dict(inputs.queue_metrics)
    assert payload["relationship_updates"] == []
    assert payload["kpi_history"] == inputs.kpi_history


def test_collect_tick_diff_enabled(builder: StreamPayloadBuilder) -> None:
    builder.diff_enabled = True
    aggregator = _RecordingAggregator(builder)

    base_inputs = _SnapshotInputs()
    base_inputs.apply_defaults()
    base_context = base_inputs.to_global_context()

    list(
        aggregator.collect_tick(
            tick=1,
            world=None,
            rewards={},
            events=(),
            policy_snapshot={},
            kpi_history=False,
            reward_breakdown={},
            stability_inputs={},
            perturbations={"active": {}},
            policy_identity={},
            possessed_agents=(),
            social_events=(),
            runtime_variant="facade",
            conflict_snapshot=base_inputs.conflict_snapshot,
            relationship_updates=(),
            relationship_overlay={},
            narrations=(),
            affordance_manifest={},
            stability_metrics={},
            stability_alerts=(),
            promotion=None,
            anneal_status=None,
            kpi_history_payload={},
            embedding_metrics=base_inputs.embedding_metrics,
            global_context=base_context,
        )
    )

    updated_inputs = _SnapshotInputs(
        tick=2,
        queue_metrics={"cooldown_events": 1},
        embedding_metrics={"allocations_total": 1.0},
        employment_metrics={"pending_count": 2},
        conflict_snapshot={
            "queues": {"cooldown_events": 1},
            "queue_history": [],
            "rivalry": {},
            "rivalry_events": [],
        },
        relationship_metrics={"total": 1},
        relationship_snapshot={},
        perturbations={"active": {"event": "storm"}},
    )
    updated_inputs.apply_defaults()
    updated_context = updated_inputs.to_global_context()

    list(
        aggregator.collect_tick(
            tick=updated_inputs.tick,
            world=None,
            rewards={},
            events=(),
            policy_snapshot={},
            kpi_history=False,
            reward_breakdown={},
            stability_inputs={},
            perturbations=updated_inputs.perturbations,
            policy_identity={},
            possessed_agents=(),
            social_events=(),
            runtime_variant="facade",
            conflict_snapshot=updated_inputs.conflict_snapshot,
            relationship_updates=(),
            relationship_overlay={},
            narrations=(),
            affordance_manifest={},
            stability_metrics=updated_inputs.stability_metrics,
            stability_alerts=(),
            promotion=None,
            anneal_status=None,
            kpi_history_payload={},
            embedding_metrics=updated_inputs.embedding_metrics,
            global_context=updated_context,
        )
    )

    assert len(aggregator.events) == 2
    first, second = aggregator.events
    assert first["payload_type"] == "snapshot"
    assert second["payload_type"] == "diff"
    assert second["changes"]["queue_metrics"]["cooldown_events"] == 1


def test_record_loop_failure_emits_health_event(builder: StreamPayloadBuilder) -> None:
    aggregator = TelemetryAggregator(builder)
    payload = {
        "tick": 12,
        "error": "boom",
        "status": "error",
        "duration_ms": 5.0,
        "transport": {
            "provider": "port",
            "queue_length": 2,
            "dropped_messages": 1,
            "last_flush_duration_ms": None,
            "payloads_flushed_total": 10,
            "bytes_flushed_total": 1024,
            "auth_enabled": False,
            "worker": {"alive": True, "error": None, "restart_count": 0},
        },
        "summary": {
            "duration_ms": 5.0,
            "queue_length": 2,
            "dropped_messages": 1,
        },
    }
    events = list(aggregator.record_loop_failure(payload))
    assert len(events) == 1
    event = events[0]
    assert event.kind == "health"
    assert event.payload["error"] == "boom"
    assert event.metadata["kind"] == "loop_failure"


def test_record_console_results_no_sink(builder: StreamPayloadBuilder) -> None:
    aggregator = TelemetryAggregator(builder)
    aggregator.record_console_results([{"status": "ok"}])


def test_record_console_results_invokes_sink(builder: StreamPayloadBuilder) -> None:
    captured: list[list[object]] = []

    def sink(batch: Iterable[object]) -> None:
        captured.append(list(batch))

    aggregator = TelemetryAggregator(builder, console_sink=sink)
    aggregator.record_console_results([{"status": "ok"}])
    assert captured == [[{"status": "ok"}]]
