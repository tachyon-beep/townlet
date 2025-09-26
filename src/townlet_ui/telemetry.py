"""Schema-aware telemetry client utilities for observer UI components."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional

SUPPORTED_SCHEMA_PREFIX = "0.3"


@dataclass(frozen=True)
class EmploymentMetrics:
    pending: List[str]
    pending_count: int
    exits_today: int
    daily_exit_cap: int
    queue_limit: int
    review_window: int


@dataclass(frozen=True)
class ConflictMetrics:
    queue_cooldown_events: int
    queue_ghost_step_events: int
    rivalry_agents: int
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class RelationshipChurn:
    window_start: int
    window_end: int
    total_evictions: int
    per_owner: Mapping[str, int]
    per_reason: Mapping[str, int]


@dataclass(frozen=True)
class AgentSummary:
    agent_id: str
    wallet: float
    shift_state: str
    attendance_ratio: float
    wages_withheld: float
    lateness_counter: int
    on_shift: bool


@dataclass(frozen=True)
class TelemetrySnapshot:
    schema_version: str
    schema_warning: Optional[str]
    employment: EmploymentMetrics
    conflict: ConflictMetrics
    relationships: Optional[RelationshipChurn]
    agents: List[AgentSummary]
    raw: Mapping[str, Any]


class SchemaMismatchError(RuntimeError):
    """Raised when telemetry schema is newer than the client supports."""


class TelemetryClient:
    """Lightweight helper to parse telemetry payloads for the observer UI."""

    def __init__(self, *, expected_schema_prefix: str = SUPPORTED_SCHEMA_PREFIX) -> None:
        self.expected_schema_prefix = expected_schema_prefix

    def parse_snapshot(self, payload: Mapping[str, Any]) -> TelemetrySnapshot:
        """Validate and convert a telemetry payload into dataclasses."""
        schema_version = str(payload.get("schema_version", ""))
        if not schema_version:
            raise SchemaMismatchError("Telemetry payload missing schema_version")

        schema_warning = self._check_schema(schema_version)
        employment_payload = self._get_section(payload, "employment", dict)
        jobs_payload = self._get_section(payload, "jobs", dict)
        conflict_payload = self._get_section(payload, "conflict", Mapping)
        relationships_payload = payload.get("relationships")

        employment = EmploymentMetrics(
            pending=list(employment_payload.get("pending", [])),
            pending_count=int(employment_payload.get("pending_count", 0)),
            exits_today=int(employment_payload.get("exits_today", 0)),
            daily_exit_cap=int(employment_payload.get("daily_exit_cap", 0)),
            queue_limit=int(employment_payload.get("queue_limit", 0)),
            review_window=int(employment_payload.get("review_window", 0)),
        )

        queue_metrics = conflict_payload.get("queues", {})
        rivalry_metrics = conflict_payload.get("rivalry", {})
        queue_cooldowns = 0
        queue_ghost_steps = 0
        rivalry_agents = 0
        if isinstance(queue_metrics, Mapping):
            queue_cooldowns = int(queue_metrics.get("cooldown_events", 0))
            queue_ghost_steps = int(queue_metrics.get("ghost_step_events", 0))
        if isinstance(rivalry_metrics, Mapping):
            rivalry_agents = len(rivalry_metrics)

        conflict = ConflictMetrics(
            queue_cooldown_events=queue_cooldowns,
            queue_ghost_step_events=queue_ghost_steps,
            rivalry_agents=rivalry_agents,
            raw=conflict_payload,
        )

        relationships = None
        if isinstance(relationships_payload, Mapping) and relationships_payload:
            relationships = RelationshipChurn(
                window_start=int(relationships_payload.get("window_start", 0)),
                window_end=int(relationships_payload.get("window_end", 0)),
                total_evictions=int(relationships_payload.get("total", 0)),
                per_owner={
                    str(owner): int(count)
                    for owner, count in (relationships_payload.get("owners", {}) or {}).items()
                },
                per_reason={
                    str(reason): int(count)
                    for reason, count in (relationships_payload.get("reasons", {}) or {}).items()
                },
            )

        agents: List[AgentSummary] = []
        for agent_id, info in jobs_payload.items():
            agents.append(
                AgentSummary(
                    agent_id=agent_id,
                    wallet=float(info.get("wallet", 0.0)),
                    shift_state=str(info.get("shift_state", "unknown")),
                    attendance_ratio=float(info.get("attendance_ratio", 0.0)),
                    wages_withheld=float(info.get("wages_withheld", 0.0)),
                    lateness_counter=int(info.get("lateness_counter", 0)),
                    on_shift=bool(info.get("on_shift", False)),
                )
            )

        agents.sort(key=lambda summary: summary.agent_id)

        return TelemetrySnapshot(
            schema_version=schema_version,
            schema_warning=schema_warning,
            employment=employment,
            conflict=conflict,
            relationships=relationships,
            agents=agents,
            raw=payload,
        )

    def from_console(self, router: Any) -> TelemetrySnapshot:
        """Fetch snapshot via console router (expects telemetry_snapshot command)."""
        command = getattr(router, "dispatch", None)
        if not callable(command):
            raise TypeError("Console router must expose a dispatch callable")
        payload = command(_console_command("telemetry_snapshot"))
        if not isinstance(payload, Mapping):
            raise TypeError("Console returned non-mapping telemetry payload")
        return self.parse_snapshot(payload)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _check_schema(self, version: str) -> Optional[str]:
        if version.startswith(self.expected_schema_prefix):
            return None
        message = (
            f"Client supports schema prefix {self.expected_schema_prefix}, but shard reported {version}."
        )
        if version.split(".")[0] != self.expected_schema_prefix.split(".")[0]:
            raise SchemaMismatchError(message)
        return message

    @staticmethod
    def _get_section(payload: Mapping[str, Any], key: str, expected: type) -> Mapping[str, Any]:
        value = payload.get(key)
        if not isinstance(value, expected):
            raise SchemaMismatchError(f"Telemetry payload missing expected section '{key}'")
        return value


def _console_command(name: str) -> Any:
    """Helper to build console command dataclass without importing CLI package."""
    from townlet.console.handlers import ConsoleCommand

    return ConsoleCommand(name=name, args=(), kwargs={})
