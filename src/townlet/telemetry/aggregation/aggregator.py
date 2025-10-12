"""Aggregation adapters producing telemetry events from world artefacts."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from collections.abc import Iterable as TypingIterable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - typing aid
    from townlet.telemetry.interfaces import TelemetryEvent

from .collector import StreamPayloadBuilder

__all__ = ["TelemetryAggregator"]


class TelemetryAggregator:
    """Compose telemetry events using the stream payload builder."""

    def __init__(
        self,
        builder: StreamPayloadBuilder,
        *,
        console_sink: Callable[[TypingIterable[object]], None] | None = None,
        failure_sink: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> None:
        self._builder = builder
        self._console_sink = console_sink
        self._failure_sink = failure_sink

    def collect_tick(
        self,
        *,
        tick: int,
        world,
        rewards,
        events: Iterable[Mapping[str, Any]] | None = None,
        policy_snapshot: Mapping[str, Mapping[str, Any]] | None = None,
        kpi_history: bool = False,
        reward_breakdown: Mapping[str, Mapping[str, Any]] | None = None,
        stability_inputs: Mapping[str, Any] | None = None,
        perturbations: Mapping[str, Any] | None = None,
        policy_identity: Mapping[str, Any] | None = None,
        possessed_agents: Iterable[str] | None = None,
        social_events: Iterable[Mapping[str, Any]] | None = None,
        runtime_variant: str | None = None,
        global_context: Mapping[str, Any] | None = None,
        **extra: Any,
    ) -> Iterable[TelemetryEvent]:
        context_payload = global_context if isinstance(global_context, Mapping) else None
        payload: Mapping[str, Any] | None = extra.get("snapshot_payload")
        if payload is None:
            stability_alerts = extra.get("stability_alerts", ())
            kpi_history_payload = extra.get("kpi_history_payload", {})
            payload = self._builder.build(
                tick=tick,
                runtime_variant=runtime_variant,
                queue_metrics=extra.get("queue_metrics"),
                embedding_metrics=extra.get("embedding_metrics"),
                employment_metrics=extra.get("employment_metrics"),
                conflict_snapshot=extra.get("conflict_snapshot", {}),
                relationship_metrics=extra.get("relationship_metrics"),
                relationship_snapshot=extra.get("relationship_snapshot"),
                relationship_updates=extra.get("relationship_updates", ()),
                relationship_overlay=extra.get("relationship_overlay", {}),
                events=events or (),
                narrations=extra.get("narrations", ()),
                job_snapshot=extra.get("job_snapshot"),
                economy_snapshot=extra.get("economy_snapshot"),
                economy_settings=extra.get("economy_settings"),
                price_spikes=extra.get("price_spikes"),
                utilities=extra.get("utilities"),
                affordance_manifest=extra.get("affordance_manifest", {}),
                reward_breakdown=reward_breakdown or {},
                stability_metrics=extra.get("stability_metrics"),
                stability_alerts=stability_alerts,
                stability_inputs=stability_inputs or {},
                promotion=extra.get("promotion"),
                perturbations=perturbations,
                policy_identity=policy_identity or {},
                policy_snapshot=policy_snapshot or {},
                anneal_status=extra.get("anneal_status"),
                kpi_history=kpi_history_payload if kpi_history else {},
                global_context=context_payload,
            )
        kind = payload.get("payload_type", "snapshot")
        metadata = {
            "schema_version": self._builder.schema_version,
            "diff_enabled": self._builder.diff_enabled,
        }
        from townlet.telemetry.interfaces import TelemetryEvent  # local import to avoid cycles

        yield TelemetryEvent(tick=tick, kind=kind, payload=dict(payload), metadata=metadata)

    def record_console_results(self, results: TypingIterable[object]) -> None:
        if self._console_sink is None:
            return
        self._console_sink(results)

    def record_loop_failure(self, payload: Mapping[str, object]) -> Iterable[TelemetryEvent]:
        if self._failure_sink is not None:
            self._failure_sink(payload)
        metadata = {"kind": "loop_failure"}
        tick = int(payload.get("tick", 0))
        from townlet.telemetry.interfaces import TelemetryEvent

        yield TelemetryEvent(tick=tick, kind="health", payload=dict(payload), metadata=metadata)
