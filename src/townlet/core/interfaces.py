"""Protocol definitions for core simulation interfaces.

These interfaces describe the contracts consumed by :class:`SimulationLoop` and
related orchestration code. They allow the loop to depend on behaviour rather
than concrete implementations, which matches the target architecture described
in ``docs/architecture_review/townlet-target-architecture.md``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import TYPE_CHECKING, Protocol, TypeAlias, runtime_checkable

from townlet.world.runtime import ActionMapping, ActionProvider, RuntimeStepResult

if TYPE_CHECKING:  # pragma: no cover
    from townlet.console.command import ConsoleCommandEnvelope, ConsoleCommandResult
    from townlet.world.grid import WorldState

ObservationBatch: TypeAlias = Mapping[str, object]
RewardMapping: TypeAlias = Mapping[str, float]
TerminationMapping: TypeAlias = Mapping[str, bool]


@runtime_checkable
class WorldRuntimeProtocol(Protocol):
    """Interface for advancing world state and handling console/actions."""

    def bind_world(self, world: WorldState) -> None:
        """Rebind the runtime to a freshly constructed world instance."""

    def queue_console(self, operations: Iterable[ConsoleCommandEnvelope]) -> None:
        """Buffer console operations for the next tick."""

    def apply_actions(self, actions: ActionMapping) -> None:
        """Stage policy actions that should execute on the next tick."""

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable[ConsoleCommandEnvelope] | None = None,
        action_provider: ActionProvider | None = None,
        policy_actions: ActionMapping | None = None,
    ) -> RuntimeStepResult:
        """Advance the world by one tick and return observable artefacts."""

    def snapshot(self) -> Mapping[str, object]:
        """Return a diagnostic snapshot of the underlying world state."""


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

    def decide(self, world: WorldState, tick: int) -> Mapping[str, object]:
        """Return an action mapping for the provided world/tick."""

    def post_step(
        self,
        rewards: RewardMapping,
        terminated: TerminationMapping,
    ) -> None:
        """Record rewards and termination flags emitted by the environment."""

    def flush_transitions(self, observations: ObservationBatch) -> None:
        """Flush buffered transitions once observations have been produced."""

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

    def set_runtime_variant(self, variant: str | None) -> None:
        """Record which runtime flavour produced the latest telemetry."""

    def update_policy_identity(self, identity: Mapping[str, object] | None) -> None:
        """Update the policy identity metadata emitted to downstream systems."""

    def drain_console_buffer(self) -> Iterable[object]:
        """Return buffered console commands collected since the last tick."""

    def record_console_results(self, results: Iterable[ConsoleCommandResult]) -> None:
        """Persist console outputs generated during tick execution."""

    def publish_tick(
        self,
        *,
        tick: int,
        world: WorldState,
        observations: ObservationBatch,
        rewards: RewardMapping,
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
        """Publish telemetry for the given tick."""

    def latest_queue_metrics(self) -> Mapping[str, int] | None:
        """Return the most recent queue metrics payload."""

    def latest_embedding_metrics(self) -> Mapping[str, object] | None:
        """Return the most recent embedding allocator metrics payload."""

    def latest_job_snapshot(self) -> Mapping[str, Mapping[str, object]]:
        """Return the latest job snapshot emitted by telemetry."""

    def latest_events(self) -> Iterable[Mapping[str, object]]:
        """Return the most recently streamed event payloads."""

    def latest_employment_metrics(self) -> Mapping[str, object] | None:
        """Return the latest employment metrics payload."""

    def latest_rivalry_events(self) -> Iterable[Mapping[str, object]]:
        """Return recent rivalry events captured by telemetry."""

    def record_stability_metrics(self, metrics: Mapping[str, object]) -> None:
        """Persist the latest stability metrics for downstream consumers."""

    def latest_transport_status(self) -> Mapping[str, object]:
        """Expose transport worker status information for health checks."""

    def record_health_metrics(self, metrics: Mapping[str, object]) -> None:
        """Record per-tick health information for monitoring."""

    def record_loop_failure(self, payload: Mapping[str, object]) -> None:
        """Emit telemetry describing a simulation loop failure."""

    def import_state(self, payload: Mapping[str, object]) -> None:
        """Restore telemetry state from a snapshot payload."""

    def import_console_buffer(self, payload: Iterable[object]) -> None:
        """Restore buffered console commands from a snapshot payload."""

    def update_relationship_metrics(self, metrics: Mapping[str, object]) -> None:
        """Replace the cached relationship metrics with a snapshot payload."""

    def record_snapshot_migrations(self, applied: Iterable[str]) -> None:
        """Record the list of snapshot migrations applied during restore."""
