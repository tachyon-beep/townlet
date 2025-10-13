"""Protocol definitions for core simulation interfaces.

These interfaces describe the contracts consumed by :class:`SimulationLoop` and
related orchestration code. They allow the loop to depend on behaviour rather
than concrete implementations, which matches the target architecture described
in ``docs/architecture_review/townlet-target-architecture.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Protocol, TypeAlias, runtime_checkable

if TYPE_CHECKING:  # pragma: no cover
    from townlet.world.dto.observation import ObservationEnvelope
    from townlet.world.grid import WorldState

ObservationBatch: TypeAlias = Mapping[str, object]
RewardMapping: TypeAlias = Mapping[str, float]
TerminationMapping: TypeAlias = Mapping[str, bool]
TransitionFrames: TypeAlias = list[dict[str, object]]

@runtime_checkable
class PolicyBackendProtocol(Protocol):
    """Interface consumed by the simulation loop to drive agent policies."""

    def register_ctx_reset_callback(self, callback: Callable[[str], None] | None) -> None:
        """Register a callback invoked when an agent context reset is requested."""

    def enable_anneal_blend(self, enabled: bool) -> None:
        """Toggle anneal blending behaviour if supported by the backend."""

    def set_anneal_ratio(self, ratio: float | None) -> None:
        """Update the anneal ratio applied to blended scripted/learned policies."""

    def reset_state(self) -> None:
        """Reset any cached policy state (e.g., trajectories, RNG streams)."""

    def supports_observation_envelope(self) -> bool:
        """Return True when the backend expects DTO observation envelopes."""

    def decide(
        self,
        world: WorldState,
        tick: int,
        *,
        envelope: ObservationEnvelope,
    ) -> Mapping[str, object]:
        """Return an action mapping for the provided world/tick."""

    def post_step(
        self,
        rewards: RewardMapping,
        terminated: TerminationMapping,
    ) -> None:
        """Record rewards and termination flags emitted by the environment."""

    def flush_transitions(
        self,
        *,
        envelope: ObservationEnvelope,
    ) -> Mapping[str, object] | TransitionFrames | None:
        """Flush buffered transitions once the DTO envelope is available."""

    def latest_policy_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        """Expose the most recent policy metadata snapshot."""

    def possessed_agents(self) -> list[str]:
        """Return the list of agents currently possessed by external controllers."""

    def consume_option_switch_counts(self) -> Mapping[str, int]:
        """Return and reset per-agent option switch counters."""

    def active_policy_hash(self) -> str | None:
        """Return a hash identifying the active policy parameters."""

    def current_anneal_ratio(self) -> float | None:
        """Expose the current anneal blend ratio, if any."""


@runtime_checkable
class TelemetrySinkProtocol(Protocol):
    """Interface for telemetry pipelines consumed by the simulation loop."""

    def schema(self) -> str:
        """Return the telemetry schema version for compatibility checks."""

    def set_runtime_variant(self, variant: str | None) -> None:
        """Record which runtime flavour produced the latest telemetry."""

    def update_policy_identity(self, identity: Mapping[str, object] | None) -> None:
        """Update the policy identity metadata emitted to downstream systems."""

    def latest_policy_identity(self) -> Mapping[str, object] | None: ...

    def drain_console_buffer(self) -> Iterable[object]:
        """Return buffered console commands collected since the last tick."""

    def queue_console_command(self, command: object) -> None: ...
    def export_console_buffer(self) -> list[object]: ...
    def latest_console_results(self) -> Iterable[Mapping[str, object]]: ...
    def console_history(self) -> Iterable[Mapping[str, object]]: ...
    def current_tick(self) -> int: ...
    def emit_manual_narration(
        self,
        *,
        message: str,
        category: str = "operator_story",
        tick: int | None = None,
        priority: bool = False,
        data: Mapping[str, object] | None = None,
        dedupe_key: str | None = None,
    ) -> Mapping[str, object] | None: ...
    def register_event_subscriber(self, subscriber: Callable[[list[dict[str, object]]], None]) -> None: ...

    def emit_event(self, name: str, payload: Mapping[str, object] | None = None) -> None:
        """Dispatch a telemetry event payload."""

    def latest_queue_metrics(self) -> Mapping[str, int] | None:
        """Return the most recent queue metrics payload."""

    def latest_embedding_metrics(self) -> Mapping[str, object] | None:
        """Return the most recent embedding allocator metrics payload."""

    def latest_job_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        """Return the latest job snapshot emitted by telemetry."""

    def latest_events(self) -> Iterable[Mapping[str, object]]:
        """Return the most recently streamed event payloads."""

    # Read-only accessors commonly used by consoles/observers
    def latest_economy_snapshot(self) -> Mapping[str, Mapping[str, object]]: ...
    def latest_economy_settings(self) -> Mapping[str, float]: ...
    def latest_price_spikes(self) -> Mapping[str, Mapping[str, object]]: ...
    def latest_utilities(self) -> Mapping[str, bool]: ...
    def latest_conflict_snapshot(self) -> Mapping[str, object]: ...
    def latest_relationship_metrics(self) -> Mapping[str, object] | None: ...
    def latest_relationship_snapshot(self) -> Mapping[str, Mapping[str, Mapping[str, float]]]: ...
    def latest_relationship_updates(self) -> Iterable[Mapping[str, object]]: ...
    def latest_relationship_summary(self) -> Mapping[str, object]: ...
    def latest_social_events(self) -> Iterable[Mapping[str, object]]: ...
    def latest_narrations(self) -> Iterable[Mapping[str, object]]: ...
    def latest_narration_state(self) -> Mapping[str, object]: ...
    def latest_anneal_status(self) -> Mapping[str, object] | None: ...
    def latest_policy_snapshot(self) -> Mapping[str, Mapping[str, object]]: ...
    def latest_snapshot_migrations(self) -> Iterable[str]: ...
    def latest_affordance_manifest(self) -> Mapping[str, object]: ...
    def latest_affordance_runtime(self) -> Mapping[str, object]: ...
    def latest_reward_breakdown(self) -> Mapping[str, Mapping[str, float]]: ...
    def latest_personality_snapshot(self) -> Mapping[str, object]: ...

    def latest_employment_metrics(self) -> Mapping[str, object] | None:
        """Return the latest employment metrics payload."""

    def latest_rivalry_events(self) -> Iterable[Mapping[str, object]]:
        """Return recent rivalry events captured by telemetry."""

    def latest_stability_metrics(self) -> Mapping[str, object]: ...
    def latest_stability_alerts(self) -> Iterable[str]: ...

    def latest_transport_status(self) -> Mapping[str, object]:
        """Expose transport worker status information for health checks."""

    def latest_health_status(self) -> Mapping[str, object]: ...

    def import_state(self, payload: Mapping[str, object]) -> None:
        """Restore telemetry state from a snapshot payload."""

    def import_console_buffer(self, payload: Iterable[object]) -> None:
        """Restore buffered console commands from a snapshot payload."""

    def update_relationship_metrics(self, metrics: Mapping[str, object]) -> None:
        """Replace the cached relationship metrics with a snapshot payload."""
