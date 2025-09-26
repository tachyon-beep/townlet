# Attendance & Wage Design Brief (Employment Loop Hardening)

_Last reviewed: 2025-09-25_

## 1. Context & Goals
- Milestone M2 requires ≥70% on-time shift attendance and stability alerts on lateness spikes.
- Current prototype grants wages whenever the agent stands at the job location during the scheduled window and applies a single lateness penalty at shift start.
- We need explicit shift states, wage gating, and telemetry so scripted controllers and future RL policies can reason about employment pressure.

## 2. Proposed Shift State Machine
| State | Entry Criteria | Exit Criteria | Notes |
| --- | --- | --- | --- |
| `pre_shift` | Tick < `start_tick - arrival_buffer` | Reaches buffer window | Idle/commuting period; no accounting. |
| `await_start` | `start_tick - arrival_buffer` ≤ tick < `start_tick` | Shift begins | Telemetry logs "on_time_window"; scripted behavior should target job tile during this window. |
| `on_time` | Agent at required location at `start_tick` or arrives within `grace_ticks` (default 5) | Leaves required location or shift ends | Wages accrue; lateness counter not incremented. |
| `late` | Arrives after `grace_ticks` but before `absent_cutoff` (default 30) | Reaches required location or shift ends | Wage accrual starts only when present; lateness penalty applied once upon entry; telemetry records late duration. |
| `absent` | Fails to arrive by `absent_cutoff` or leaves for more than `absence_slack` consecutive ticks (default 20) | Shift ends | Wages withheld; absent counter increments; triggers unemployment risk after configurable limit. |
| `post_shift` | Tick > `end_tick` | Next shift window | Reset state machine; apply recap metrics.

### Tunable Parameters
- `arrival_buffer` (existing): default 20 ticks before start.
- `grace_ticks`: default 5 ticks after start to still count on-time.
- `absent_cutoff`: default 30 ticks after start before marking absent.
- `absence_slack`: consecutive ticks allowed off location before flipping to absent mid-shift (default 20).
- `max_absent_shifts`: number of absences in rolling 7-day window before lifecycle exit (default 3).

## 3. Wage & Penalty Rules
- Wage accrues per tick **only** in `on_time` or `late` states while present at location; no accrual in `pre_shift`, `await_start`, or `absent`.
- Lateness penalties:
  - Immediate deduction `lateness_penalty` when entering `late` at shift start.
  - Additional micro-penalty `late_tick_penalty` (default 0.005) for each tick spent late but not yet at location.
- Absence penalties:
  - For each `absent` shift, apply `absence_penalty` (default 0.2) and increment `absent_count` telemetry.
  - After `max_absent_shifts`, lifecycle queues unemployment exit with warning event.
- Early departure (leaving location before end) counts as absence if away longer than `absence_slack` within the same shift; wages halt immediately.

## 4. Telemetry & State Changes
New per-agent fields (`TelemetryPublisher.latest_job_snapshot`):
- `shift_state`: enum string (`on_time`, `late`, `absent`, etc.).
- `attendance_ratio`: rolling on-time ticks / scheduled ticks (window configurable, default last 3 shifts).
- `late_ticks_today`: cumulative late ticks for current day.
- `absent_shifts_7d`: rolling counter.
- `wages_withheld`: cumulative wages not paid due to absence.

Events emitted via `WorldState._emit_event`:
- `shift_late_start` with reason + ticks late.
- `shift_absent` once cutoff reached.
- `shift_departed_early` when leaving mid-shift.
- `employment_warning` when absences approach exit threshold.

Stability monitor ingestion:
- Calculate lateness ratio = `late_ticks_today / scheduled_ticks_today`.
- Alert `lateness_spike` when ratio exceeds config threshold (default 0.3).
- Alert `absence_cluster` when `absent_shifts_7d` crosses threshold.

## 5. Configuration Surface
Extend `SimulationConfig.jobs[job_id]` with optional overrides:
- `grace_ticks`, `absent_cutoff`, `absence_slack`, `late_tick_penalty`, `absence_penalty`.
Global defaults live under new `employment` config node:
```yaml
employment:
  grace_ticks: 5
  absent_cutoff: 30
  absence_slack: 20
  late_tick_penalty: 0.005
  absence_penalty: 0.2
  max_absent_shifts: 3
  attendance_window: 3  # number of shifts for rolling ratio
```

## 6. Required Code Touchpoints
- `WorldState._apply_job_state`: refactor into state machine with per-agent shift context.
- `AgentSnapshot`: add fields `shift_state`, `attendance_ratio`, `late_ticks_today`, `absent_shifts_7d`, `wages_withheld`.
- `LifecycleManager`: consume `absent_shifts_7d` and queue exits.
- `TelemetryPublisher`: serialize new fields.
- `StabilityMonitor`: compute new alerts, respect config thresholds.

## 7. Test & Validation Plan
- Unit tests for state transitions under combinations of arrival timing and mid-shift departures.
- Property test ensuring attendance ratio stays within [0,1] and matches tick counts.
- Simulation integration test verifying unemployment exit triggers after configured absences.
- Console serialization test covering new telemetry schema.

## 8. Approvals Needed
- Architecture lead: confirm state machine and parameter defaults. ✅ (2025-09-25, A. Director)
- Product/PM: sign off on penalties and unemployment thresholds. ✅ (2025-09-25, P. Lead)
- Ops lead: validate telemetry fields and event names. _(Not applicable; ops function not yet staffed.)_

_Once approvals are logged, update `docs/engineering/IMPLEMENTATION_NOTES.md` and mark Risk R1 as mitigated._
