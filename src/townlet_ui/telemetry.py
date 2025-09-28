"""Schema-aware telemetry client utilities for observer UI components."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast


def _maybe_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _coerce_float(value: object, default: float = 0.0) -> float:
    maybe = _maybe_float(value)
    return maybe if maybe is not None else default


SUPPORTED_SCHEMA_PREFIX = "0.9"


@dataclass(frozen=True)
class EmploymentMetrics:
    pending: list[str]
    pending_count: int
    exits_today: int
    daily_exit_cap: int
    queue_limit: int
    review_window: int


@dataclass(frozen=True)
class QueueHistoryEntry:
    tick: int
    cooldown_delta: int
    ghost_step_delta: int
    rotation_delta: int
    totals: Mapping[str, int]


@dataclass(frozen=True)
class RivalryEventEntry:
    tick: int
    agent_a: str
    agent_b: str
    intensity: float
    reason: str


@dataclass(frozen=True)
class ConflictMetrics:
    queue_cooldown_events: int
    queue_ghost_step_events: int
    queue_rotation_events: int
    queue_history: tuple[QueueHistoryEntry, ...]
    rivalry_agents: int
    rivalry_events: tuple[RivalryEventEntry, ...]
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class NarrationEntry:
    tick: int
    category: str
    message: str
    priority: bool
    data: Mapping[str, Any]


@dataclass(frozen=True)
class RelationshipChurn:
    window_start: int
    window_end: int
    total_evictions: int
    per_owner: Mapping[str, int]
    per_reason: Mapping[str, int]


@dataclass(frozen=True)
class RelationshipUpdate:
    owner: str
    other: str
    status: str
    trust: float
    familiarity: float
    rivalry: float
    delta_trust: float
    delta_familiarity: float
    delta_rivalry: float


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
class RelationshipOverlayEntry:
    other: str
    trust: float
    familiarity: float
    rivalry: float
    delta_trust: float
    delta_familiarity: float
    delta_rivalry: float


@dataclass(frozen=True)
class PolicyInspectorAction:
    action: str
    probability: float


@dataclass(frozen=True)
class PolicyInspectorEntry:
    agent_id: str
    tick: int
    selected_action: str
    log_prob: float
    value_pred: float
    top_actions: list[PolicyInspectorAction]


@dataclass(frozen=True)
class AnnealStatus:
    stage: str
    cycle: float | None
    dataset: str
    bc_accuracy: float | None
    bc_threshold: float | None
    bc_passed: bool
    loss_flag: bool
    queue_flag: bool
    intensity_flag: bool
    loss_baseline: float | None
    queue_baseline: float | None
    intensity_baseline: float | None


@dataclass(frozen=True)
class TransportStatus:
    connected: bool
    dropped_messages: int
    last_error: str | None
    last_success_tick: int | None
    last_failure_tick: int | None


@dataclass(frozen=True)
class StabilitySnapshot:
    alerts: tuple[str, ...]
    metrics: Mapping[str, Any]


@dataclass(frozen=True)
class TelemetrySnapshot:
    schema_version: str
    schema_warning: str | None
    employment: EmploymentMetrics
    conflict: ConflictMetrics
    narrations: list[NarrationEntry]
    narration_state: Mapping[str, Any]
    relationships: RelationshipChurn | None
    relationship_snapshot: Mapping[str, Mapping[str, Mapping[str, float]]]
    relationship_updates: list[RelationshipUpdate]
    relationship_overlay: Mapping[str, list[RelationshipOverlayEntry]]
    agents: list[AgentSummary]
    anneal: AnnealStatus | None
    policy_inspector: list[PolicyInspectorEntry]
    stability: StabilitySnapshot
    kpis: Mapping[str, list[float]]
    transport: TransportStatus
    raw: Mapping[str, Any]


class SchemaMismatchError(RuntimeError):
    """Raised when telemetry schema is newer than the client supports."""


class TelemetryClient:
    """Lightweight helper to parse telemetry payloads for the observer UI."""

    def __init__(
        self, *, expected_schema_prefix: str = SUPPORTED_SCHEMA_PREFIX
    ) -> None:
        self.expected_schema_prefix = expected_schema_prefix

    def parse_snapshot(self, payload: Mapping[str, Any]) -> TelemetrySnapshot:
        """Validate and convert a telemetry payload into dataclasses."""

        def _maybe_int(value: object) -> int | None:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                candidate = value.strip()
                if not candidate:
                    return None
                try:
                    return int(candidate)
                except ValueError:
                    return None
            return None

        def _coerce_int(value: object) -> int:
            maybe = _maybe_int(value)
            return maybe if maybe is not None else 0

        schema_version = str(payload.get("schema_version", ""))
        if not schema_version:
            raise SchemaMismatchError("Telemetry payload missing schema_version")

        schema_warning = self._check_schema(schema_version)
        employment_payload = self._get_section(payload, "employment", dict)
        jobs_payload = self._get_section(payload, "jobs", dict)
        conflict_payload = self._get_section(payload, "conflict", Mapping)
        relationships_payload = payload.get("relationships")
        relationship_snapshot_payload = payload.get("relationship_snapshot", {})
        relationship_updates_payload = payload.get("relationship_updates", [])
        narrations_payload = payload.get("narrations", [])
        narration_state_payload = payload.get("narration_state", {})

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
        queue_history_payload = conflict_payload.get("queue_history", [])
        rivalry_events_payload = conflict_payload.get("rivalry_events", [])

        queue_cooldowns = 0
        queue_ghost_steps = 0
        queue_rotations = 0
        rivalry_agents = 0
        queue_history: list[QueueHistoryEntry] = []
        rivalry_events: list[RivalryEventEntry] = []

        if isinstance(queue_metrics, Mapping):
            queue_cooldowns = _coerce_int(queue_metrics.get("cooldown_events"))
            queue_ghost_steps = _coerce_int(queue_metrics.get("ghost_step_events"))
            queue_rotations = _coerce_int(queue_metrics.get("rotation_events"))
        if isinstance(rivalry_metrics, Mapping):
            rivalry_agents = len(rivalry_metrics)

        if isinstance(queue_history_payload, list):
            for entry in queue_history_payload:
                if not isinstance(entry, Mapping):
                    continue
                delta_payload = entry.get("delta")
                if not isinstance(delta_payload, Mapping):
                    delta_payload = {}
                totals_payload = entry.get("totals")
                if not isinstance(totals_payload, Mapping):
                    totals_payload = {}
                queue_history.append(
                    QueueHistoryEntry(
                        tick=_coerce_int(entry.get("tick")),
                        cooldown_delta=_coerce_int(delta_payload.get("cooldown_events")),
                        ghost_step_delta=_coerce_int(delta_payload.get("ghost_step_events")),
                        rotation_delta=_coerce_int(delta_payload.get("rotation_events")),
                        totals={
                            str(key): _coerce_int(value)
                            for key, value in totals_payload.items()
                        },
                    )
                )

        if isinstance(rivalry_events_payload, list):
            for event in rivalry_events_payload:
                if not isinstance(event, Mapping):
                    continue
                rivalry_events.append(
                    RivalryEventEntry(
                        tick=_coerce_int(event.get("tick")),
                        agent_a=str(event.get("agent_a", "")),
                        agent_b=str(event.get("agent_b", "")),
                        intensity=float(event.get("intensity", 0.0)),
                        reason=str(event.get("reason", "unknown")),
                    )
                )

        conflict = ConflictMetrics(
            queue_cooldown_events=queue_cooldowns,
            queue_ghost_step_events=queue_ghost_steps,
            queue_rotation_events=queue_rotations,
            queue_history=tuple(queue_history),
            rivalry_agents=rivalry_agents,
            rivalry_events=tuple(rivalry_events),
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
                    for owner, count in (
                        relationships_payload.get("owners", {}) or {}
                    ).items()
                },
                per_reason={
                    str(reason): int(count)
                    for reason, count in (
                        relationships_payload.get("reasons", {}) or {}
                    ).items()
                },
            )

        relationship_snapshot: dict[str, dict[str, dict[str, float]]] = {}
        if isinstance(relationship_snapshot_payload, Mapping):
            for owner, ties in relationship_snapshot_payload.items():
                if not isinstance(ties, Mapping):
                    continue
                relationship_snapshot[str(owner)] = {
                    str(other): {
                        "trust": (
                            float(values.get("trust", 0.0))
                            if isinstance(values, Mapping)
                            else 0.0
                        ),
                        "familiarity": (
                            float(values.get("familiarity", 0.0))
                            if isinstance(values, Mapping)
                            else 0.0
                        ),
                        "rivalry": (
                            float(values.get("rivalry", 0.0))
                            if isinstance(values, Mapping)
                            else 0.0
                        ),
                    }
                    for other, values in ties.items()
                    if isinstance(values, Mapping)
                }

        relationship_updates: list[RelationshipUpdate] = []
        if isinstance(relationship_updates_payload, list):
            for entry in relationship_updates_payload:
                if not isinstance(entry, Mapping):
                    continue
                delta = entry.get("delta", {})
                if not isinstance(delta, Mapping):
                    delta = {}
                relationship_updates.append(
                    RelationshipUpdate(
                        owner=str(entry.get("owner", "")),
                        other=str(entry.get("other", "")),
                        status=str(entry.get("status", "")),
                        trust=float(entry.get("trust", 0.0)),
                        familiarity=float(entry.get("familiarity", 0.0)),
                        rivalry=float(entry.get("rivalry", 0.0)),
                        delta_trust=float(delta.get("trust", 0.0)),
                        delta_familiarity=float(delta.get("familiarity", 0.0)),
                        delta_rivalry=float(delta.get("rivalry", 0.0)),
                    )
                )

        agents: list[AgentSummary] = []
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

        overlay_payload = payload.get("relationship_overlay")
        relationship_overlay: dict[str, list[RelationshipOverlayEntry]] = {}
        if isinstance(overlay_payload, Mapping):
            for owner, ties in overlay_payload.items():
                if not isinstance(ties, list):
                    continue
                entries: list[RelationshipOverlayEntry] = []
                for tie in ties:
                    if not isinstance(tie, Mapping):
                        continue
                    entries.append(
                        RelationshipOverlayEntry(
                            other=str(tie.get("other", "")),
                            trust=float(tie.get("trust", 0.0)),
                            familiarity=float(tie.get("familiarity", 0.0)),
                            rivalry=float(tie.get("rivalry", 0.0)),
                            delta_trust=float(tie.get("delta_trust", 0.0)),
                            delta_familiarity=float(tie.get("delta_familiarity", 0.0)),
                            delta_rivalry=float(tie.get("delta_rivalry", 0.0)),
                        )
                    )
                relationship_overlay[str(owner)] = entries

        narrations: list[NarrationEntry] = []
        if isinstance(narrations_payload, list):
            for entry in narrations_payload:
                if not isinstance(entry, Mapping):
                    continue
                data = entry.get("data")
                if not isinstance(data, Mapping):
                    data = {}
                narrations.append(
                    NarrationEntry(
                        tick=int(entry.get("tick", 0)),
                        category=str(entry.get("category", "")),
                        message=str(entry.get("message", "")),
                        priority=bool(entry.get("priority", False)),
                        data=dict(data),
                    )
                )

        narration_state: Mapping[str, Any]
        if isinstance(narration_state_payload, Mapping):
            narration_state = dict(narration_state_payload)
        else:
            narration_state = {}

        agents.sort(key=lambda summary: summary.agent_id)

        anneal_status: AnnealStatus | None = None
        anneal_payload = payload.get("anneal_status")
        if isinstance(anneal_payload, Mapping) and anneal_payload:
            anneal_status = AnnealStatus(
                stage=str(anneal_payload.get("anneal_stage", "")),
                cycle=_maybe_float(anneal_payload.get("anneal_cycle")),
                dataset=str(anneal_payload.get("anneal_dataset", "")),
                bc_accuracy=_maybe_float(anneal_payload.get("anneal_bc_accuracy")),
                bc_threshold=_maybe_float(anneal_payload.get("anneal_bc_threshold")),
                bc_passed=bool(anneal_payload.get("anneal_bc_passed", False)),
                loss_flag=bool(anneal_payload.get("anneal_loss_flag", False)),
                queue_flag=bool(anneal_payload.get("anneal_queue_flag", False)),
                intensity_flag=bool(anneal_payload.get("anneal_intensity_flag", False)),
                loss_baseline=_maybe_float(anneal_payload.get("anneal_loss_baseline")),
                queue_baseline=_maybe_float(anneal_payload.get("anneal_queue_baseline")),
                intensity_baseline=_maybe_float(anneal_payload.get("anneal_intensity_baseline")),
            )

        kpi_payload = payload.get("kpi_history") or {}
        kpi_history: dict[str, list[float]] = {}
        if isinstance(kpi_payload, Mapping):
            for key, values in kpi_payload.items():
                if isinstance(values, list):
                    kpi_history[str(key)] = [
                        float(v) for v in values if isinstance(v, (int, float))
                    ]

        inspector_entries: list[PolicyInspectorEntry] = []
        policy_snapshot_payload = payload.get("policy_snapshot")
        if isinstance(policy_snapshot_payload, Mapping):
            for agent_id, entry in policy_snapshot_payload.items():
                if not isinstance(entry, Mapping):
                    continue
                top_actions_payload = entry.get("top_actions", [])
                top_actions: list[PolicyInspectorAction] = []
                if isinstance(top_actions_payload, list):
                    for action_entry in top_actions_payload:
                        if not isinstance(action_entry, Mapping):
                            continue
                        action_label = str(action_entry.get("action", ""))
                        probability = _coerce_float(action_entry.get("probability"), 0.0)
                        top_actions.append(
                            PolicyInspectorAction(
                                action=action_label,
                                probability=probability,
                            )
                        )
                inspector_entries.append(
                    PolicyInspectorEntry(
                        agent_id=str(agent_id),
                        tick=int(entry.get("tick", 0)),
                        selected_action=str(entry.get("selected_action", "")),
                        log_prob=_coerce_float(entry.get("log_prob"), 0.0),
                        value_pred=_coerce_float(entry.get("value_pred"), 0.0),
                        top_actions=top_actions,
                    )
                )

        stability_payload = payload.get("stability")
        stability_alerts: tuple[str, ...] = ()
        stability_metrics: Mapping[str, Any] = {}
        if isinstance(stability_payload, Mapping):
            alerts_payload = stability_payload.get("alerts", [])
            if isinstance(alerts_payload, list):
                stability_alerts = tuple(
                    str(alert)
                    for alert in alerts_payload
                    if alert is not None
                )
            metrics_payload = stability_payload.get("metrics")
            if isinstance(metrics_payload, Mapping):
                stability_metrics = dict(metrics_payload)

        stability = StabilitySnapshot(alerts=stability_alerts, metrics=stability_metrics)

        transport_payload = payload.get("transport")
        if not isinstance(transport_payload, Mapping):
            transport_payload = {}
        transport = TransportStatus(
            connected=bool(transport_payload.get("connected", False)),
            dropped_messages=int(_maybe_int(transport_payload.get("dropped_messages")) or 0),
            last_error=(
                str(transport_payload.get("last_error")).strip()
                if transport_payload.get("last_error") not in (None, "")
                else None
            ),
            last_success_tick=_maybe_int(transport_payload.get("last_success_tick")),
            last_failure_tick=_maybe_int(transport_payload.get("last_failure_tick")),
        )

        return TelemetrySnapshot(
            schema_version=schema_version,
            schema_warning=schema_warning,
            employment=employment,
            conflict=conflict,
            narrations=narrations,
            narration_state=narration_state,
            relationships=relationships,
            relationship_snapshot=relationship_snapshot,
            relationship_updates=relationship_updates,
            relationship_overlay=relationship_overlay,
            agents=agents,
            anneal=anneal_status,
            policy_inspector=inspector_entries,
            stability=stability,
            kpis=kpi_history,
            transport=transport,
            raw=dict(payload),
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
    def _check_schema(self, version: str) -> str | None:
        if version.startswith(self.expected_schema_prefix):
            return None
        message = (
            "Client supports schema prefix "
            f"{self.expected_schema_prefix}, but shard reported {version}."
        )
        if version.split(".")[0] != self.expected_schema_prefix.split(".")[0]:
            raise SchemaMismatchError(message)
        return message

    @staticmethod
    def _get_section(
        payload: Mapping[str, Any], key: str, expected: type
    ) -> Mapping[str, Any]:
        value = payload.get(key)
        if not isinstance(value, expected):
            raise SchemaMismatchError(
                f"Telemetry payload missing expected section '{key}'"
            )
        return cast(Mapping[str, Any], value)


def _console_command(name: str) -> Any:
    """Helper to build console command dataclass without importing CLI package."""
    from townlet.console.handlers import ConsoleCommand

    return ConsoleCommand(name=name, args=(), kwargs={})
