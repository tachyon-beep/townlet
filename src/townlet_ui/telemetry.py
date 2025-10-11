"""Schema-aware telemetry client utilities for observer UI components."""

from __future__ import annotations

import copy
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, cast


def _maybe_float(value: object) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _coerce_float(value: object, default: float = 0.0) -> float:
    maybe = _maybe_float(value)
    return maybe if maybe is not None else default


def _coerce_mapping(value: object) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return {str(key): item for key, item in value.items()}
    return None


def _coerce_history_entries(value: object) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, Iterable):
        return ()
    entries: list[Mapping[str, Any]] = []
    for item in value:
        if isinstance(item, Mapping):
            entry = dict(item)
            metadata = entry.get("metadata")
            if isinstance(metadata, Mapping):
                entry["metadata"] = dict(metadata)
            release = entry.get("release")
            if isinstance(release, Mapping):
                entry["release"] = dict(release)
            previous_release = entry.get("previous_release")
            if isinstance(previous_release, Mapping):
                entry["previous_release"] = dict(previous_release)
            entries.append(entry)
    return tuple(entries)


def _coerce_series(value: object) -> tuple[float, ...]:
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray)):
        series: list[float] = []
        for item in value:
            maybe = _maybe_float(item)
            if maybe is not None:
                series.append(maybe)
        return tuple(series)
    return ()


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
class AffordanceRuntimeSnapshot:
    running_count: int
    running: Mapping[str, Mapping[str, Any]]
    active_reservations: Mapping[str, str]
    event_counts: Mapping[str, int]


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
    job_id: str | None
    needs: Mapping[str, float]
    exit_pending: bool
    late_ticks_today: int
    meals_cooked: int
    meals_consumed: int
    basket_cost: float


@dataclass(frozen=True)
class PersonalitySnapshotEntry:
    profile: str
    traits: Mapping[str, float]
    multipliers: Mapping[str, Mapping[str, float]] | None


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
class FriendSummary:
    agent: str
    trust: float
    familiarity: float
    rivalry: float


@dataclass(frozen=True)
class RivalSummary:
    agent: str
    rivalry: float


@dataclass(frozen=True)
class RelationshipSummaryEntry:
    top_friends: tuple[FriendSummary, ...]
    top_rivals: tuple[RivalSummary, ...]


@dataclass(frozen=True)
class RelationshipSummarySnapshot:
    per_agent: Mapping[str, RelationshipSummaryEntry]
    churn_metrics: Mapping[str, Any]


@dataclass(frozen=True)
class SocialEventEntry:
    type: str
    payload: Mapping[str, Any]


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
class PriceSpikeEntry:
    event_id: str
    magnitude: float
    targets: tuple[str, ...]


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
    queue_length: int
    last_flush_duration_ms: float | None


@dataclass(frozen=True)
class StabilitySnapshot:
    alerts: tuple[str, ...]
    metrics: Mapping[str, Any]


@dataclass(frozen=True)
class HealthStatus:
    tick: int
    tick_duration_ms: float
    telemetry_queue: int
    telemetry_dropped: int
    perturbations_pending: int
    perturbations_active: int
    employment_exit_queue: int
    raw: Mapping[str, Any]


@dataclass(frozen=True)
class PromotionSnapshot:
    state: str | None
    pass_streak: int
    required_passes: int
    candidate_ready: bool
    candidate_ready_tick: int | None
    last_result: str | None
    last_evaluated_tick: int | None
    candidate_metadata: Mapping[str, Any] | None
    current_release: Mapping[str, Any] | None
    history: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class PerturbationSnapshot:
    active: Mapping[str, Mapping[str, Any]]
    pending: tuple[Mapping[str, Any], ...]
    cooldowns_spec: Mapping[str, int]
    cooldowns_agents: Mapping[str, Mapping[str, int]]


@dataclass(frozen=True)
class TelemetryHistory:
    needs: Mapping[str, Mapping[str, tuple[float, ...]]]
    wallet: Mapping[str, tuple[float, ...]]
    rivalry: Mapping[str, Mapping[str, tuple[float, ...]]]


@dataclass(frozen=True)
class TelemetrySnapshot:
    schema_version: str
    schema_warning: str | None
    employment: EmploymentMetrics
    affordance_runtime: AffordanceRuntimeSnapshot
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
    promotion: PromotionSnapshot | None
    stability: StabilitySnapshot
    kpis: Mapping[str, list[float]]
    transport: TransportStatus
    health: HealthStatus | None
    economy_settings: Mapping[str, float]
    price_spikes: tuple[PriceSpikeEntry, ...]
    utilities: Mapping[str, bool]
    relationship_summary: RelationshipSummarySnapshot | None
    social_events: tuple[SocialEventEntry, ...]
    perturbations: PerturbationSnapshot
    console_commands: Mapping[str, Mapping[str, Any]]
    console_results: tuple[Mapping[str, Any], ...]
    history: TelemetryHistory | None
    personalities: Mapping[str, PersonalitySnapshotEntry]
    raw: Mapping[str, Any]


class SchemaMismatchError(RuntimeError):
    """Raised when telemetry schema is newer than the client supports."""


class TelemetryClient:
    """Lightweight helper to parse telemetry payloads for the observer UI."""

    def __init__(
        self,
        *,
        expected_schema_prefix: str = SUPPORTED_SCHEMA_PREFIX,
        history_window: int | None = 30,
    ) -> None:
        self.expected_schema_prefix = expected_schema_prefix
        self.history_window = (
            history_window if history_window is None or history_window > 0 else None
        )
        self._state: dict[str, Any] | None = None

    def _parse_snapshot(self, payload: Mapping[str, Any]) -> TelemetrySnapshot:
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
        relationship_summary_payload = payload.get("relationship_summary")
        relationship_updates_payload = payload.get("relationship_updates", [])
        social_events_payload = payload.get("social_events")
        personalities_payload = payload.get("personalities")
        narrations_payload = payload.get("narrations", [])
        narration_state_payload = payload.get("narration_state", {})
        perturbations_payload = payload.get("perturbations", {})
        console_commands_payload = payload.get("console_commands", {})
        console_results_payload = payload.get("console_results", [])
        history_payload = payload.get("history")

        personalities: dict[str, PersonalitySnapshotEntry] = {}
        if isinstance(personalities_payload, Mapping):
            for raw_agent_id, entry in personalities_payload.items():
                if not isinstance(entry, Mapping):
                    continue
                agent_id = str(raw_agent_id)
                profile = str(entry.get("profile", "")) or "balanced"
                traits_payload = entry.get("traits", {})
                if isinstance(traits_payload, Mapping):
                    traits = {
                        "extroversion": _coerce_float(traits_payload.get("extroversion"), 0.0),
                        "forgiveness": _coerce_float(traits_payload.get("forgiveness"), 0.0),
                        "ambition": _coerce_float(traits_payload.get("ambition"), 0.0),
                    }
                else:
                    traits = {"extroversion": 0.0, "forgiveness": 0.0, "ambition": 0.0}
                multipliers_payload = entry.get("multipliers")
                multipliers: dict[str, Mapping[str, float]] | None = None
                if isinstance(multipliers_payload, Mapping):
                    multipliers = {}
                    for section_name, section_payload in multipliers_payload.items():
                        if not isinstance(section_payload, Mapping):
                            continue
                        multipliers[str(section_name)] = {
                            str(key): _coerce_float(value, 0.0)
                            for key, value in section_payload.items()
                        }
                    if not multipliers:
                        multipliers = None
                personalities[agent_id] = PersonalitySnapshotEntry(
                    profile=profile,
                    traits=traits,
                    multipliers=multipliers,
                )

        economy_settings_payload = payload.get("economy_settings", {})
        if isinstance(economy_settings_payload, Mapping):
            economy_settings = {
                str(key): float(value)
                for key, value in economy_settings_payload.items()
                if isinstance(value, (int, float)) or _maybe_float(value) is not None
            }
            # handle non numeric values gracefully
            for key, value in economy_settings_payload.items():
                if key not in economy_settings:
                    try:
                        economy_settings[str(key)] = float(value)
                    except (TypeError, ValueError):
                        economy_settings[str(key)] = 0.0
        else:
            economy_settings = {}

        utilities_payload = payload.get("utilities", {})
        if isinstance(utilities_payload, Mapping):
            utilities = {str(key): bool(value) for key, value in utilities_payload.items()}
        else:
            utilities = {}

        price_spikes_payload = payload.get("price_spikes", {})
        price_spikes: list[PriceSpikeEntry] = []
        if isinstance(price_spikes_payload, Mapping):
            for event_id, data in price_spikes_payload.items():
                if not isinstance(data, Mapping):
                    continue
                magnitude = float(_maybe_float(data.get("magnitude")) or 0.0)
                targets_field = data.get("targets", ())
                if isinstance(targets_field, (list, tuple)):
                    targets = tuple(str(target) for target in targets_field)
                elif targets_field is None:
                    targets = ()
                else:
                    targets = (str(targets_field),)
                price_spikes.append(
                    PriceSpikeEntry(
                        event_id=str(event_id),
                        magnitude=magnitude,
                        targets=targets,
                    )
                )


        employment = EmploymentMetrics(
            pending=list(employment_payload.get("pending", [])),
            pending_count=int(employment_payload.get("pending_count", 0)),
            exits_today=int(employment_payload.get("exits_today", 0)),
            daily_exit_cap=int(employment_payload.get("daily_exit_cap", 0)),
            queue_limit=int(employment_payload.get("queue_limit", 0)),
            review_window=int(employment_payload.get("review_window", 0)),
        )

        runtime_payload = payload.get("affordance_runtime")
        runtime_running: dict[str, Mapping[str, Any]] = {}
        active_reservations: dict[str, str] = {}
        event_counts: dict[str, int] = {}
        running_count = 0
        if isinstance(runtime_payload, Mapping):
            running_section = runtime_payload.get("running")
            if isinstance(running_section, Mapping):
                runtime_running = {
                    str(object_id): {
                        str(key): value for key, value in entry.items()
                    }
                    for object_id, entry in running_section.items()
                    if isinstance(entry, Mapping)
                }
            running_count = _coerce_int(runtime_payload.get("running_count"))
            if running_count == 0 and runtime_running:
                running_count = len(runtime_running)
            reservations_payload = runtime_payload.get("active_reservations", {})
            if isinstance(reservations_payload, Mapping):
                active_reservations = {
                    str(object_id): str(agent_id)
                    for object_id, agent_id in reservations_payload.items()
                }
            counts_payload = runtime_payload.get("event_counts", {})
            if isinstance(counts_payload, Mapping):
                for key, value in counts_payload.items():
                    event_counts[str(key)] = _coerce_int(value)
        for key in ("start", "finish", "fail", "precondition_fail"):
            event_counts.setdefault(key, 0)
        affordance_runtime = AffordanceRuntimeSnapshot(
            running_count=running_count,
            running=runtime_running,
            active_reservations=active_reservations,
            event_counts=event_counts,
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
                            str(key): _coerce_int(value) for key, value in totals_payload.items()
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
                    for owner, count in (relationships_payload.get("owners", {}) or {}).items()
                },
                per_reason={
                    str(reason): int(count)
                    for reason, count in (relationships_payload.get("reasons", {}) or {}).items()
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
                            float(values.get("trust", 0.0)) if isinstance(values, Mapping) else 0.0
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
            needs_payload = info.get("needs", {})
            needs: dict[str, float] = {}
            if isinstance(needs_payload, Mapping):
                needs = {
                    str(key): _coerce_float(value)
                    for key, value in needs_payload.items()
                }
            agents.append(
                AgentSummary(
                    agent_id=agent_id,
                    wallet=float(info.get("wallet", 0.0)),
                    shift_state=str(info.get("shift_state", "unknown")),
                    attendance_ratio=float(info.get("attendance_ratio", 0.0)),
                    wages_withheld=float(info.get("wages_withheld", 0.0)),
                    lateness_counter=int(info.get("lateness_counter", 0)),
                    on_shift=bool(info.get("on_shift", False)),
                    job_id=str(info.get("job_id")) if info.get("job_id") else None,
                    needs=needs,
                    exit_pending=bool(info.get("exit_pending", False)),
                    late_ticks_today=int(info.get("late_ticks_today", 0)),
                    meals_cooked=int(info.get("meals_cooked", 0)),
                    meals_consumed=int(info.get("meals_consumed", 0)),
                    basket_cost=_coerce_float(info.get("basket_cost", 0.0)),
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

        summary_snapshot: RelationshipSummarySnapshot | None = None
        if isinstance(relationship_summary_payload, Mapping):
            per_agent: dict[str, RelationshipSummaryEntry] = {}
            churn_data: dict[str, Any] = {}
            for owner, entry in relationship_summary_payload.items():
                if owner == "churn":
                    if isinstance(entry, Mapping):
                        churn_data = {str(key): value for key, value in entry.items()}
                    continue
                if not isinstance(entry, Mapping):
                    continue
                friends_payload = entry.get("top_friends", [])
                rivals_payload = entry.get("top_rivals", [])
                friends: list[FriendSummary] = []
                if isinstance(friends_payload, list):
                    for friend in friends_payload:
                        if not isinstance(friend, Mapping):
                            continue
                        friends.append(
                            FriendSummary(
                                agent=str(friend.get("agent", "")),
                                trust=_coerce_float(friend.get("trust")),
                                familiarity=_coerce_float(friend.get("familiarity")),
                                rivalry=_coerce_float(friend.get("rivalry")),
                            )
                        )
                rivals: list[RivalSummary] = []
                if isinstance(rivals_payload, list):
                    for rival in rivals_payload:
                        if not isinstance(rival, Mapping):
                            continue
                        rivals.append(
                            RivalSummary(
                                agent=str(rival.get("agent", "")),
                                rivalry=_coerce_float(rival.get("rivalry")),
                            )
                        )
                per_agent[str(owner)] = RelationshipSummaryEntry(
                    top_friends=tuple(friends),
                    top_rivals=tuple(rivals),
                )
            if per_agent or churn_data:
                summary_snapshot = RelationshipSummarySnapshot(
                    per_agent=per_agent,
                    churn_metrics=churn_data,
                )

        social_events: list[SocialEventEntry] = []
        if isinstance(social_events_payload, list):
            for entry in social_events_payload:
                if not isinstance(entry, Mapping):
                    continue
                event_type = str(entry.get("type", "unknown"))
                payload_copy = {
                    str(key): value for key, value in entry.items() if key != "type"
                }
                social_events.append(
                    SocialEventEntry(type=event_type, payload=payload_copy)
                )

        perturbations = self._parse_perturbations(perturbations_payload)

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
                    str(alert) for alert in alerts_payload if alert is not None
                )
            metrics_payload = stability_payload.get("metrics")
            if isinstance(metrics_payload, Mapping):
                stability_metrics = dict(metrics_payload)

        stability = StabilitySnapshot(alerts=stability_alerts, metrics=stability_metrics)

        promotion_payload = payload.get("promotion")
        if not isinstance(promotion_payload, Mapping) or not promotion_payload:
            promotion_payload = None
        if promotion_payload is None and isinstance(stability_payload, Mapping):
            candidate = stability_payload.get("promotion_state")
            if isinstance(candidate, Mapping):
                promotion_payload = candidate
        promotion_snapshot: PromotionSnapshot | None = None
        if isinstance(promotion_payload, Mapping):
            promotion_snapshot = PromotionSnapshot(
                state=str(promotion_payload.get("state"))
                if promotion_payload.get("state")
                else None,
                pass_streak=_coerce_int(promotion_payload.get("pass_streak")),
                required_passes=_coerce_int(promotion_payload.get("required_passes")),
                candidate_ready=bool(promotion_payload.get("candidate_ready", False)),
                candidate_ready_tick=_maybe_int(promotion_payload.get("candidate_ready_tick")),
                last_result=str(promotion_payload.get("last_result"))
                if promotion_payload.get("last_result")
                else None,
                last_evaluated_tick=_maybe_int(promotion_payload.get("last_evaluated_tick")),
                candidate_metadata=_coerce_mapping(promotion_payload.get("candidate")),
                current_release=_coerce_mapping(promotion_payload.get("current_release")),
                history=_coerce_history_entries(promotion_payload.get("history")),
            )

        transport_payload = payload.get("transport")
        if not isinstance(transport_payload, Mapping):
            transport_payload = {}
        transport_queue = int(_maybe_int(transport_payload.get("queue_length")) or 0)
        transport_dropped = int(_maybe_int(transport_payload.get("dropped_messages")) or 0)
        transport = TransportStatus(
            connected=bool(transport_payload.get("connected", False)),
            dropped_messages=transport_dropped,
            last_error=(
                str(transport_payload.get("last_error")).strip()
                if transport_payload.get("last_error") not in (None, "")
                else None
            ),
            last_success_tick=_maybe_int(transport_payload.get("last_success_tick")),
            last_failure_tick=_maybe_int(transport_payload.get("last_failure_tick")),
            queue_length=transport_queue,
            last_flush_duration_ms=_maybe_float(transport_payload.get("last_flush_duration_ms")),
        )

        health_payload = payload.get("health")
        health_snapshot: HealthStatus | None = None
        if isinstance(health_payload, Mapping) and health_payload:
            context_payload = health_payload.get("global_context")
            if not isinstance(context_payload, Mapping):
                context_payload = {}
            perturbations_alias = int(_maybe_int(health_payload.get("perturbations_pending")) or 0)
            perturbations_active_alias = int(_maybe_int(health_payload.get("perturbations_active")) or 0)
            perturbations_payload = context_payload.get("perturbations")
            if isinstance(perturbations_payload, Mapping):
                pending_section = perturbations_payload.get("pending")
                active_section = perturbations_payload.get("active")

                def _len_or_default(value: object, fallback: int) -> int:
                    if isinstance(value, Mapping):
                        return len(value)
                    if isinstance(value, (list, tuple, set)):
                        return len(value)
                    return fallback

                perturbations_alias = _len_or_default(pending_section, perturbations_alias)
                perturbations_active_alias = _len_or_default(active_section, perturbations_active_alias)
            employment_exit_alias = int(_maybe_int(health_payload.get("employment_exit_queue")) or 0)
            employment_payload = context_payload.get("employment_snapshot")
            if isinstance(employment_payload, Mapping):
                pending_count = employment_payload.get("pending_count")
                if isinstance(pending_count, (int, float)):
                    employment_exit_alias = int(pending_count)
                else:
                    pending_section = employment_payload.get("pending")
                    if isinstance(pending_section, (list, tuple, set)):
                        employment_exit_alias = len(pending_section)
            health_snapshot = HealthStatus(
                tick=_coerce_int(health_payload.get("tick")),
                tick_duration_ms=_coerce_float(health_payload.get("duration_ms"))
                or _coerce_float(health_payload.get("tick_duration_ms")),
                telemetry_queue=transport_queue
                if transport_queue
                else int(_maybe_int(health_payload.get("telemetry_queue")) or 0),
                telemetry_dropped=transport_dropped
                if transport_dropped
                else int(_maybe_int(health_payload.get("telemetry_dropped")) or 0),
                perturbations_pending=perturbations_alias,
                perturbations_active=perturbations_active_alias,
                employment_exit_queue=employment_exit_alias,
                raw=dict(health_payload),
            )

        if isinstance(console_commands_payload, Mapping):
            console_commands = {
                str(name): dict(meta)
                for name, meta in console_commands_payload.items()
                if isinstance(meta, Mapping)
            }
        else:
            console_commands = {}

        console_results: list[Mapping[str, Any]] = []
        if isinstance(console_results_payload, list):
            for entry in console_results_payload:
                if isinstance(entry, Mapping):
                    console_results.append(dict(entry))

        history_snapshot: TelemetryHistory | None = None
        if isinstance(history_payload, Mapping) and history_payload:
            limit = self.history_window

            def _trim(series: tuple[float, ...]) -> tuple[float, ...]:
                if limit is None or len(series) <= limit:
                    return series
                return series[-limit:]

            needs_history: dict[str, Mapping[str, tuple[float, ...]]] = {}
            needs_section = history_payload.get("needs", {})
            if isinstance(needs_section, Mapping):
                for agent_id, values in needs_section.items():
                    agent_key = str(agent_id)
                    if isinstance(values, Mapping):
                        per_need: dict[str, tuple[float, ...]] = {}
                        for need_name, series_values in values.items():
                            series = _trim(_coerce_series(series_values))
                            if series:
                                per_need[str(need_name)] = series
                        if per_need:
                            needs_history[agent_key] = per_need
                    else:
                        series = _trim(_coerce_series(values))
                        if series:
                            needs_history[agent_key] = {"composite": series}

            wallet_history: dict[str, tuple[float, ...]] = {}
            wallet_section = history_payload.get("wallet", {})
            if isinstance(wallet_section, Mapping):
                for agent_id, values in wallet_section.items():
                    series = _trim(_coerce_series(values))
                    if series:
                        wallet_history[str(agent_id)] = series

            rivalry_history: dict[str, dict[str, tuple[float, ...]]] = {}
            rivalry_section = history_payload.get("rivalry", {})
            if isinstance(rivalry_section, Mapping):
                for key, values in rivalry_section.items():
                    series = _trim(_coerce_series(values))
                    if not series:
                        continue
                    if isinstance(key, str) and "|" in key:
                        owner, other = key.split("|", 1)
                    else:
                        owner, other = str(key), ""
                    owner_map = rivalry_history.setdefault(owner, {})
                    owner_map[other or "*"] = series

            if needs_history or wallet_history or rivalry_history:
                history_snapshot = TelemetryHistory(
                    needs=needs_history,
                    wallet=wallet_history,
                    rivalry=rivalry_history,
                )

        return TelemetrySnapshot(
            schema_version=schema_version,
            schema_warning=schema_warning,
            employment=employment,
            affordance_runtime=affordance_runtime,
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
            promotion=promotion_snapshot,
            stability=stability,
            kpis=kpi_history,
            transport=transport,
            health=health_snapshot,
            economy_settings=economy_settings,
            price_spikes=tuple(price_spikes),
            utilities=utilities,
            relationship_summary=summary_snapshot,
            social_events=tuple(social_events),
            perturbations=perturbations,
            console_commands=console_commands,
            console_results=tuple(console_results),
            history=history_snapshot,
            personalities=personalities,
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
        return self.parse_payload(payload)

    def parse_payload(self, payload: Mapping[str, Any]) -> TelemetrySnapshot:
        payload_type = str(payload.get("payload_type", "snapshot") or "snapshot")
        if payload_type == "diff":
            if self._state is None:
                raise SchemaMismatchError("Received telemetry diff before initial snapshot")
            base = copy.deepcopy(self._state)
            schema_version = payload.get("schema_version")
            if schema_version is not None:
                base["schema_version"] = schema_version
            tick = payload.get("tick")
            if tick is not None:
                base["tick"] = tick
            changes = payload.get("changes", {})
            if not isinstance(changes, Mapping):
                raise SchemaMismatchError("Telemetry diff payload missing 'changes' mapping")
            for key, value in changes.items():
                base[str(key)] = value
            removed = payload.get("removed", ())
            if isinstance(removed, Iterable):
                for key in removed:
                    base.pop(str(key), None)
            self._state = base
            return self._parse_snapshot(base)

        if payload_type != "snapshot":
            raise SchemaMismatchError(f"Unsupported telemetry payload_type '{payload_type}'")

        snapshot = {str(key): value for key, value in payload.items() if key != "payload_type"}
        self._state = copy.deepcopy(snapshot)
        return self._parse_snapshot(snapshot)

    def parse_snapshot(self, payload: Mapping[str, Any]) -> TelemetrySnapshot:
        """Backward-compatible wrapper for callers expecting snapshot payloads."""
        return self.parse_payload(payload)

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

    def _parse_perturbations(self, payload: object) -> PerturbationSnapshot:
        if not isinstance(payload, Mapping):
            return PerturbationSnapshot(
                active={},
                pending=(),
                cooldowns_spec={},
                cooldowns_agents={},
            )

        def _to_int(value: object) -> int:
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                candidate = value.strip()
                if not candidate:
                    return 0
                try:
                    return int(candidate)
                except ValueError:
                    return 0
            return 0

        active_payload = payload.get("active", {})
        active: dict[str, Mapping[str, Any]] = {}
        if isinstance(active_payload, Mapping):
            for event_id, data in active_payload.items():
                if isinstance(data, Mapping):
                    active[str(event_id)] = {str(key): value for key, value in data.items()}

        pending_payload = payload.get("pending", [])
        pending: list[Mapping[str, Any]] = []
        if isinstance(pending_payload, Iterable):
            for entry in pending_payload:
                if isinstance(entry, Mapping):
                    pending.append({str(key): value for key, value in entry.items()})

        cooldowns_payload = payload.get("cooldowns", {})
        cooldowns_spec: dict[str, int] = {}
        cooldowns_agents: dict[str, dict[str, int]] = {}
        if isinstance(cooldowns_payload, Mapping):
            spec_section = cooldowns_payload.get("spec", {})
            if isinstance(spec_section, Mapping):
                cooldowns_spec = {
                    str(name): _to_int(value)
                    for name, value in spec_section.items()
                }
            agents_section = cooldowns_payload.get("agents", {})
            if isinstance(agents_section, Mapping):
                for agent_id, entries in agents_section.items():
                    if not isinstance(entries, Mapping):
                        continue
                    cooldowns_agents[str(agent_id)] = {
                        str(key): _to_int(value)
                        for key, value in entries.items()
                    }

        return PerturbationSnapshot(
            active=active,
            pending=tuple(pending),
            cooldowns_spec=cooldowns_spec,
            cooldowns_agents=cooldowns_agents,
        )

    @staticmethod
    def _get_section(payload: Mapping[str, Any], key: str, expected: type) -> Mapping[str, Any]:
        value = payload.get(key)
        if not isinstance(value, expected):
            raise SchemaMismatchError(f"Telemetry payload missing expected section '{key}'")
        return cast(Mapping[str, Any], value)


def _console_command(name: str) -> Any:
    """Helper to build console command dataclass without importing CLI package."""
    from townlet.console.handlers import ConsoleCommand

    return ConsoleCommand(name=name, args=(), kwargs={})
