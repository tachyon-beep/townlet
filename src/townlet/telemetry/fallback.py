"""Stub telemetry sink used when optional transports are unavailable."""

from __future__ import annotations

import logging
from collections import deque
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from townlet.core.interfaces import TelemetrySinkProtocol
from townlet.dto.telemetry import TelemetryEventDTO

logger = logging.getLogger(__name__)


class StubTelemetrySink(TelemetrySinkProtocol):
    """No-op telemetry implementation that logs missing capability."""

    def __init__(self, config: Any | None = None, publisher: Any | None = None) -> None:
        self.config = config
        self.publisher = publisher
        self._latest_console_events: deque[Mapping[str, object]] = deque(maxlen=50)
        logger.warning("telemetry_stub_active provider=stub message='Telemetry transport disabled; install extras or configure stdout.'")

    # ---------------------------
    # Basic identity/schema
    # ---------------------------
    def schema(self) -> str:
        return "0.9.0"

    def set_runtime_variant(self, variant: str | None) -> None:
        _ = variant

    def update_policy_identity(self, identity: Mapping[str, object] | None) -> None:
        _ = identity

    def drain_console_buffer(self) -> Iterable[object]:
        # Drain console events cached from dispatcher emissions
        drained = list(self._latest_console_events)
        self._latest_console_events.clear()
        return drained

    def emit_event(self, event: TelemetryEventDTO) -> None:
        """Emit a typed telemetry event (stub implementation)."""
        logger.debug("telemetry_stub_event type=%s tick=%s", event.event_type, event.tick)
        # Cache console.result events for snapshot restore
        if event.event_type == "console.result":
            self._latest_console_events.append(event.payload)

    def emit_metric(self, name: str, value: float, **tags: Any) -> None:
        logger.debug("telemetry_stub_metric name=%s value=%s tags=%s", name, value, tags)

    def latest_queue_metrics(self) -> Mapping[str, int] | None:
        return {}

    def latest_embedding_metrics(self) -> Mapping[str, object] | None:
        return {}

    def latest_job_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        return {}

    def latest_economy_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        return {}

    def latest_economy_settings(self) -> Mapping[str, float]:
        return {}

    def latest_price_spikes(self) -> Mapping[str, Mapping[str, object]]:
        return {}

    def latest_utilities(self) -> Mapping[str, bool]:
        return {}

    def latest_events(self) -> Iterable[Mapping[str, object]]:
        return []

    def latest_employment_metrics(self) -> Mapping[str, object] | None:
        return {}

    def latest_rivalry_events(self) -> Iterable[Mapping[str, object]]:
        return []

    def latest_conflict_snapshot(self) -> Mapping[str, object]:
        return {}

    def latest_relationship_metrics(self) -> Mapping[str, object] | None:
        return {}

    def latest_relationship_snapshot(self) -> Mapping[str, Mapping[str, Mapping[str, float]]]:
        return {}

    def latest_relationship_updates(self) -> Iterable[Mapping[str, object]]:
        return []

    def latest_relationship_summary(self) -> Mapping[str, object]:
        return {}

    def latest_social_events(self) -> Iterable[Mapping[str, object]]:
        return []

    def latest_narrations(self) -> Iterable[Mapping[str, object]]:
        return []

    def latest_narration_state(self) -> Mapping[str, object]:
        return {}

    def latest_anneal_status(self) -> Mapping[str, object] | None:
        return None

    def latest_policy_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        return {}

    def latest_policy_identity(self) -> Mapping[str, object] | None:
        return {}

    def latest_snapshot_migrations(self) -> Iterable[str]:
        return []

    def latest_affordance_manifest(self) -> Mapping[str, object]:
        return {}

    def latest_affordance_runtime(self) -> Mapping[str, object]:
        return {
            "running": {},
            "running_count": 0,
            "active_reservations": {},
            "event_counts": {"start": 0, "finish": 0, "fail": 0, "precondition_fail": 0},
        }

    def latest_reward_breakdown(self) -> Mapping[str, Mapping[str, float]]:
        return {}

    def latest_personality_snapshot(self) -> Mapping[str, object]:
        return {}

    def latest_transport_status(self) -> Mapping[str, object]:
        return {"provider": "stub", "status": "inactive"}

    def transport_status(self) -> Mapping[str, object]:
        return {"provider": "stub", "status": "inactive"}

    def latest_health_status(self) -> Mapping[str, object]:
        return {}

    def import_state(self, payload: Mapping[str, object]) -> None:
        _ = payload

    def import_console_buffer(self, payload: Iterable[object]) -> None:
        # Import from snapshot - convert to event format if needed
        for item in payload:
            if isinstance(item, Mapping):
                self._latest_console_events.append(item)

    def update_relationship_metrics(self, metrics: Mapping[str, object]) -> None:
        _ = metrics

    def latest_stability_alerts(self) -> Iterable[str]:
        return []

    def latest_perturbations(self) -> Mapping[str, object]:
        return {}

    def latest_console_results(self) -> Iterable[Mapping[str, object]]:
        return list(self._latest_console_events)

    def console_history(self) -> Iterable[Mapping[str, object]]:
        return []

    def latest_possessed_agents(self) -> Iterable[str]:
        return []

    def latest_precondition_failures(self) -> Iterable[Mapping[str, object]]:
        return []

    def current_tick(self) -> int:
        return 0

    def emit_manual_narration(
        self,
        *,
        message: str,
        category: str = "operator_story",
        tick: int | None = None,
        priority: bool = False,
        data: Mapping[str, object] | None = None,
        dedupe_key: str | None = None,
    ) -> Mapping[str, object] | None:
        _ = (message, category, tick, priority, data, dedupe_key)
        # Stub does not emit narrated entries.
        return None

    def register_event_subscriber(self, subscriber: Callable[[list[dict[str, object]]], None]) -> None:
        _ = subscriber

    def close(self) -> None:
        self._latest_console_events.clear()


def is_stub_telemetry(telemetry: TelemetrySinkProtocol, provider: str | None = None) -> bool:
    """Check if a telemetry sink is a stub implementation.

    Args:
        telemetry: Telemetry sink to check
        provider: Optional provider name hint

    Returns:
        True if telemetry is a stub sink
    """
    if isinstance(telemetry, StubTelemetrySink):
        return True
    if provider is None:
        return False
    return provider == "stub"
