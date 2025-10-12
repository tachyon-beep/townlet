# WP3B – Legacy Bridge Trace (Demo Story Arc, ticks 0–10)

This note captures the behaviours that still rely on the legacy world helpers after the DTO
refactor. The trace was generated from the demo story arc scenario (`configs/scenarios/demo_story_arc.yaml`)
with the personality features disabled (default scripted controller). The raw data lives at
`data/demo_trace_tick0-10.json` and records per-tick actions, emitted events, queue state, and
post-tick need levels.

## Observed Call Flow (WorldContext.tick)

1. **Respawn & Console Processing**
   - `lifecycle.process_respawns` → `WorldState.apply_console` (returns command results for router).
2. **Perturbations**
   - `perturbations.tick` (unchanged from legacy flow).
3. **Action Application (Transitional Bridge)**
   - Modular path: `_coerce_actions` → `townlet.world.actions.apply_actions`.
     - Emits `action.move`/`action.invalid` events but only handles `move`/`noop`.
   - Legacy bridge: `WorldState.apply_actions` replays the full pipeline
     (`queue_system.request_access`, `affordance_system.start/release`, chat guards, etc.).
4. **System Steps**
   - `SystemContext` constructed with dispatcher + RNG stream.
   - `queues.step` is still a no-op; queue mutations occur during the legacy bridge.
   - `affordances.step` currently delegates to `WorldState.resolve_affordances` (legacy runtime).
   - `employment`, `relationships`, `economy`, `perturbations` steps run but rely on internal
     services seeded during bridge execution.
5. **Nightly Reset / Lifecycle**
   - `NightlyResetService.apply` (when `tick % ticks_per_day == 0`).
   - `lifecycle.evaluate` and `lifecycle.termination_reasons`.
6. **Event Drain**
   - `WorldState.drain_events` returns a mix of DTO-generated `action.*` events and the legacy
     mutations; duplicate `action.invalid` entries in the trace highlight the dual pathways.

## Key Findings

- **Queue state**: After 10 ticks the queue manager still reports empty active/queued slots, but the
  trace shows `action.invalid` events for each `wait` intent because the modular action pipeline
  does not implement `wait`. The behaviour guard rails rely on the legacy bridge to ignore these
  failures.
- **Needs decay**: Hunger/hygiene/energy dropped from the seeded values (e.g. demo_1 hunger
  `0.45 → 0.40`), confirming `_apply_need_decay` executes via
  `AffordanceRuntimeService.resolve → ctx.apply_need_decay`.
- **Relationship ledger**: Trust/familiarity values remain populated via the legacy chat events; no
  rivalry is introduced in the first 10 ticks.
- **Duplicate events**: Each tick records duplicate `chat_success` and `action.invalid` events
  because both the modular dispatcher and the legacy bridge emit them. This is safe short-term but
  will inflate telemetry until the bridge is removed.

## Next Actions (feeds WP3B plan)

1. **Queues**: Populate `townlet.world.systems.queues.step` with reservation/rotation/blocked logic,
   then stop calling `WorldState.apply_actions` for queue mutations. *(Ghost-step handling now
   resides in `queues.step`; promotion/handover logic still needs to migrate.)*
2. **Affordances**: Route modular actions through `AffordanceRuntimeService` directly and delete the
   `state.resolve_affordances` fallback.
3. **Need decay**: Expose `ctx.apply_need_decay` as a dedicated system (or keep it inside the
   affordance step once modularised).
4. **Instrumentation**: Once the bridge is gone, reproduce this trace and ensure no duplicate
   `action.*` events remain.

## Stage 3A – Direct `WorldState` reads (2025-10-10)

Initial audit of the policy layer highlighted the last pockets of legacy world access.
Stage 3B executes the remediation plan summarised below.

## Stage 3B Summary (2025-10-10)

- `DTOWorldView` now materialises per-agent snapshots (needs, job, personality, pending intent) and
  exposes iterator helpers plus queue affinity metrics. Legacy fallbacks log once when invoked.
- `ScriptedBehavior` routes all decision logic (`decide`, `_satisfy_needs`, `_maybe_chat`,
  `_avoid_rivals`, `_rivals_in_queue`, `should_avoid`) through the DTO façade; tests guard the
  DTO-only path (`tests/policy/test_scripted_behavior_dto.py`).
- `BehaviorBridge.decide_agent` requires a DTO view; policy runtime already guarantees this after Stage 3A.
  TODO marker remains on `_find_object_of_type` until DTOs export object rosters (Stage 5).
- Remaining legacy reads: scripted CLI adapters (`policy/scripted.py`) and scenario seed helpers still
  touch `loop.world.agents` by design; they will migrate once DTO-capable capture tooling lands.

### Stage 3C (Policy DTO Path Cleanup – 2025-10-10)

- `SimulationLoop` no longer caches `_policy_observation_batch` or forwards legacy observations to
  policy providers; action providers require DTO envelopes and raise immediately if a backend refuses them.
- `PolicyController`/`ScriptedPolicyAdapter`/`PolicyRuntime` now expose DTO-only signatures while
  keeping telemetry/TickArtifacts legacy-compatible until Stage 5.
- `TrajectoryService.flush_transitions` consumes DTO envelopes exclusively; the mapping fallback has
  been removed.

## Stage 3C Audit – Legacy Consumer Follow-up (2025-10-10)

- **SimulationLoop**
  - Legacy `_policy_observation_batch` cache has been removed; DTO envelopes are now the sole
    payload delivered to policy providers.
  - `TickArtifacts` still surface `observations` for compatibility; this flag is tracked for removal
    under WP3 Stage 5.
- **Policy façade**
  - `PolicyController`, `PolicyRuntime`, and scripted adapters require DTO envelopes. Optional
    `observations` kwargs were removed; guard tests cover the DTO-only path.
- **TelemetryPublisher**
  - `loop.tick` events continue to include the legacy `observations` blob for downstream consumers.
    `_handle_event` tolerance remains until Stage 5 replaces external consumers.
- **Training/Trajectory tooling**
  - Trajectory service and orchestrator run purely on DTO frames; remaining translator helper
    (`frames_to_replay_sample`) is earmarked for Stage 5 once export artefacts adopt DTO-native
    schemas.
- **World access**
  - Behaviour bridge still touches `world.objects` for object lookups; TODO markers persist for
    Stage 5 when DTO rosters land.

These residual touchpoints define the Stage 5 scope to finish deprecating the legacy observation
payload after the DTO rollout ships.

## Stage 3C Training Adapter Audit (2025-10-10)

- **PolicyTrainingOrchestrator**
  - `capture_rollout`, `run_rollout_ppo`, and anneal helpers no longer touch `loop.observations`;
    trajectory frames flow exclusively from `PolicyRuntime.collect_trajectory`, which already emits
    DTO-backed `map`/`features` tensors and anneal context.
  - Telemetry emissions still rely on DTO-derived metadata (`policy.metadata`, `policy.possession`,
    `policy.anneal.update`), so no legacy getters remain.
- **TrajectoryService**
  - `flush_transitions` requires an `ObservationEnvelope` and builds frames directly from DTO agents.
    The old observation batch fallback has been removed.
- **Replay tooling**
  - `build_batch` / `ReplayDataset` operate on DTO-generated frames; no calls to ObservationBuilder.
  - `frames_to_replay_sample` persists as a translator for external replay artefacts. It consumes
    DTO frame fields (`map`, `features`, rewards, dones) and is already flagged for retirement in
    WP3 Stage 5 once downstream exporters accept DTO-native payloads.
- **PPO / BC adapters**
  - `policy/models.py` and `policy/backends/pytorch/*` consume the stacked DTO tensors provided by
    replay batches; no direct world or legacy observation access remains.

**Next steps:** migrate the residual translator helpers and replay exporters to emit DTO-native
datasets (WP3C Stage 3D/Stage 5), then drop the compatibility layer.
