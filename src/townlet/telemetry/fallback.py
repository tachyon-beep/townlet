"""Stub telemetry sink used when optional transports are unavailable."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping
from typing import Any

from townlet.core.interfaces import TelemetrySinkProtocol

logger = logging.getLogger(__name__)


class StubTelemetrySink(TelemetrySinkProtocol):
    """No-op telemetry implementation that logs missing capability."""

    def __init__(self, config: Any | None = None) -> None:
        self.config = config
        self._console_buffer: list[object] = []
        logger.warning("telemetry_stub_active provider=stub message='Telemetry transport disabled; install extras or configure stdout.'")

    def set_runtime_variant(self, variant: str | None) -> None:
        _ = variant

    def update_policy_identity(self, identity: Mapping[str, object] | None) -> None:
        _ = identity

    def drain_console_buffer(self) -> Iterable[object]:
        drained = list(self._console_buffer)
        self._console_buffer.clear()
        return drained

    def record_console_results(self, results: Iterable[Mapping[str, object]]) -> None:
        _ = list(results)

    def publish_tick(
        self,
        *,
        tick: int,
        world: Any,
        observations: Mapping[str, object],
        rewards: Mapping[str, float],
        events: Iterable[Mapping[str, object]] | None = None,
        policy_snapshot: Mapping[str, Mapping[str, object]] | None = None,
        kpi_history: bool = False,
        reward_breakdown: Mapping[str, Mapping[str, float]] | None = None,
        stability_inputs: Mapping[str, object] | None = None,
        perturbations: Mapping[str, object] | None = None,
        policy_identity: Mapping[str, object] | None = None,
        possessed_agents: Iterable[str] | None = None,
        social_events: Iterable[Mapping[str, object]] | None = None,
        runtime_variant: str | None = None,
    ) -> None:
        _ = (
            tick,
            world,
            observations,
            rewards,
            events,
            policy_snapshot,
            kpi_history,
            reward_breakdown,
            stability_inputs,
            perturbations,
            policy_identity,
            possessed_agents,
            social_events,
            runtime_variant,
        )

    def latest_queue_metrics(self) -> Mapping[str, int] | None:
        return {}

    def latest_embedding_metrics(self) -> Mapping[str, object] | None:
        return {}

    def latest_job_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        return {}

    def latest_events(self) -> Iterable[Mapping[str, object]]:
        return []

    def latest_employment_metrics(self) -> Mapping[str, object] | None:
        return {}

    def latest_rivalry_events(self) -> Iterable[Mapping[str, object]]:
        return []

    def record_stability_metrics(self, metrics: Mapping[str, object]) -> None:
        _ = metrics

    def latest_transport_status(self) -> Mapping[str, object]:
        return {"provider": "stub", "status": "inactive"}

    def record_health_metrics(self, metrics: Mapping[str, object]) -> None:
        _ = metrics

    def record_loop_failure(self, payload: Mapping[str, object]) -> None:
        logger.error("telemetry_stub_loop_failure payload=%s", dict(payload))

    def import_state(self, payload: Mapping[str, object]) -> None:
        _ = payload

    def import_console_buffer(self, payload: Iterable[object]) -> None:
        self._console_buffer.extend(payload)

    def update_relationship_metrics(self, metrics: Mapping[str, object]) -> None:
        _ = metrics

    def record_snapshot_migrations(self, applied: Iterable[str]) -> None:
        _ = list(applied)

    def close(self) -> None:
        self._console_buffer.clear()
