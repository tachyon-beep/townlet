# WP3 Status

**Current state (2025-10-10)**
- Scoping complete: WP3 owns the telemetry sink rework, policy observation flow, and the final simulation loop cleanup.
- Event schema drafted (`event_schema.md`) covering `loop.tick`, `loop.health`, `loop.failure`, `console.result`, and policy/stability payloads.
- `TelemetryEventDispatcher` implemented with bounded queue/rivalry caches and subscriber hooks; Stdout adapter now routes lifecycle events through the dispatcher, and the stub sink logs events via the same path.
- Legacy writer shims removed from `TelemetryPublisher`; the loop emits `loop.tick`/`loop.health`/`loop.failure`/`stability.metrics`/`console.result` events exclusively. HTTP transport posts dispatcher events; streaming transport remains a TODO once external consumers require it. Guard tests cover the event-only surface.
- DTO Step 1 complete: `dto_observation_inventory.md` maps consumers → fields, `dto_example_tick.json`/`dto_sample_tick.json` capture the baseline envelope (schema **v0.2.0**), and converters/tests exist in `src/townlet/world/dto`. The envelope now exposes queue rosters, running affordances, relationship metrics, enriched per-agent context (position/needs/job/inventory/personality), and global employment/economy/anneal snapshots; `SimulationLoop` emits DTO payloads alongside events.
- DTO parity harness expanded (`tests/core/test_sim_loop_dto_parity.py`) to assert DTO vs legacy values for rewards, needs, wallets, job snapshots, economy metrics, queue affinity, and anneal context using baselines captured in `docs/architecture_review/WP_NOTES/WP3/dto_parity/`.
- Scripted behaviour path consumes DTO-backed views via `DTOWorldView`, emitting guardrail events while maintaining legacy fallbacks for missing envelopes.
- **Stage 3A (DTO wiring)** complete: `SimulationLoop` now requires DTO envelopes before delegating to policy providers, logs when legacy observation batches are used, and bootstraps the envelope on reset. `PolicyRuntime` caches envelopes via `ObservationEnvelopeCache`, and `PolicyController` enforces DTO-aware backends (raising when providers reject the envelope). Legacy observation batches remain available temporarily but emit warnings.
- **Stage 3B (DTO behaviour parity)** complete: `DTOWorldView` exposes per-agent snapshots/iterators, `ScriptedBehavior` and `BehaviorBridge.decide_agent` consume DTO data end-to-end, and guard tests (`tests/policy/test_scripted_behavior_dto.py`) ensure queue/chat/guardrail flows stay DTO-first (legacy fallbacks now log once when exercised).
- Stage 3C in progress: `TrajectoryService` consumes DTO envelopes (`tests/policy/test_trajectory_service_dto.py`) and the training orchestrator captures DTO-backed rollouts (`tests/policy/test_training_orchestrator_capture.py`); replay pipelines no longer touch `loop.observations`.
- **Stage 3D**: policy ports/backends now advertise DTO envelope support, `resolve_policy_backend` enforces the capability check, `StubPolicyBackend` emits a `DeprecationWarning` for legacy observation batches, and `SimulationLoop` streams `policy.metadata` / `policy.possession` / `policy.anneal.update` events through the dispatcher.
- **Stage 3E**: regression guards in place—DTO parity harness re-run, `PolicyController` raises when DTO envelopes are absent, telemetry policy events are covered by new smokes, and rollout capture tests continue to verify DTO trajectory plumbing.
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
