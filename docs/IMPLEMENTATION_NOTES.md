# Implementation Notes

## 2025-09-24 — Queue & Affordance Integration
- Added `QueueManager`-driven affordance execution in `WorldState`; actions now request/start/release objects and ghost-step failures clear running affordances.
- Introduced lightweight `AffordanceSpec` and `InteractiveObject` tracking for tests; effects apply to agent needs and wallet when duration completes.
- Telemetry already captures queue + embedding metrics; stability monitor now consumes embedding warnings.
- Next: flesh out affordance registry loading from YAML and propagate object/affordance hooks to console + telemetry observers.

## 2025-09-24 — Affordance YAML Loader
- `SimulationConfig` now points at `affordances.affordances_file`; `WorldState` loads specs on init via embedded YAML reader.
- Tests updated to confirm default `use_shower` affordance exists and to override effects for deterministic assertions.
- Affordance YAML now supports object definitions (`type: object`), automatically registering interactive objects.
- Remaining work: extend schema with queue node positions and wire hook events into telemetry.

## 2025-09-24 — Affordance Events & Telemetry
- World emits `affordance_start` / `affordance_finish` / `affordance_fail` events when reservations change state.
- Telemetry publisher captures the event batch each tick; stability monitor can inspect them via `latest_events`.
- Event stream subscriber added for console/ops surfaces so handlers can poll latest events.
- Stability monitor now raises `affordance_failures_exceeded` when event count exceeds `stability.affordance_fail_threshold`.
- Next: expose streaming over CLI and log event-derived alerts in ops handbook.

## 2025-09-24 — Needs Loop & Reward Engine
- Added per-tick need decay driven by `rewards.decay_rates`, applied after affordance resolution.
- Replaced reward stub with homeostasis + survival tick, including clip enforcement and termination guard.
- Lifecycle manager now terminates agents when hunger collapses, enabling M0 exit checks.
- Tests cover decay, reward maths, and stability alerts for affordance failures.
- Introduced basic economy parameters (`economy.*`), deducting meal costs and fridge stock on `eat_meal` affordances.
- Job scheduler assigns agents round-robin across `jobs.*`, tracks shift windows, applies wage income, and enforces location-based punctuality with lateness penalties/events.
