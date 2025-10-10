# WP3 Status

**Current state (2025-10-09)**
- Scoping complete: WP3 owns the telemetry sink rework, policy observation flow, and the final simulation loop cleanup.
- Event schema drafted (`event_schema.md`) covering `loop.tick`, `loop.health`, `loop.failure`, `console.result`, and policy/stability payloads.
- `TelemetryEventDispatcher` implemented with bounded queue/rivalry caches and subscriber hooks; Stdout adapter now routes lifecycle events through the dispatcher, and the stub sink logs events via the same path.
- Legacy writer shims removed from `TelemetryPublisher`; the loop emits `loop.tick`/`loop.health`/`loop.failure`/`stability.metrics`/`console.result` events exclusively. HTTP transport posts dispatcher events; streaming transport remains a TODO once external consumers require it. Guard tests cover the event-only surface.
- DTO Step 1 complete: `dto_observation_inventory.md` maps consumers → fields, `dto_example_tick.json`/`dto_sample_tick.json` capture the baseline envelope (schema **v0.2.0**), and converters/tests exist in `src/townlet/world/dto`. The envelope now exposes queue rosters, running affordances, relationship metrics, enriched per-agent context (position/needs/job/inventory/personality), and global employment/economy/anneal snapshots; `SimulationLoop` emits DTO payloads alongside events.
- Scripted behaviour path consumes DTO-backed views via `DTOWorldView`, emitting guardrail events while maintaining legacy fallbacks for missing envelopes.
- **WP3B complete:** queue/affordance/employment/economy/relationship systems now run entirely through modular services. `WorldContext.tick` no longer calls legacy apply/resolve helpers, `_apply_need_decay` only invokes employment/economy fallbacks when services are absent, and targeted system tests (`tests/world/test_systems_*.py`) lock the behaviour. World-level smokes (`pytest tests/world -q`) pass with the bridge removed.
- Behaviour parity smokes (`tests/test_behavior_personality_bias.py`) remain green; DTO parity harness awaits reward/ML scenarios under WP3C.
- Remaining work packages:
  - **WP3C – DTO Parity Expansion & ML Validation**: expand the parity harness, migrate ML adapters, retire legacy observation payloads.
- WP1 telemetry blockers cleared; the remaining dependency is removing `runtime.queue_console` once policy DTO flow is finished. WP2 still depends on DTO-only policy adapters before default providers can drop legacy handles.

**Dependencies**
- Unblocks WP1 Step 8 (removal of legacy telemetry writers and `runtime.queue_console` usage).
- Unblocks WP2 Step 7 (policy/world adapters still exposing legacy handles until observation-first DTOs are available).

**Upcoming Milestones**
1. Telemetry event API & sink refactor.
2. Policy observation/controller update (port-driven decisions, metadata streaming).
3. Loop finalisation & documentation sweep (complete WP1/WP2 blockers).

Update this file as WP3 tasks progress.
