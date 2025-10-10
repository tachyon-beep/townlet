# WP3 Working Tasks

## 1. Telemetry Event Pipeline
- [x] Finalise event schemas (`loop.tick`, `loop.health`, `loop.failure`, `console.result`, `policy.metadata`, `stability.metrics`, `rivalry.events`) and document payload contracts (`event_schema.md`).
- [x] Implement event dispatcher & minimal cache in telemetry core; ensure retention bounds (queue history, rivalry history, possessed agents).
- [~] Update transports:
- [x] Stdout adapter emits events via the dispatcher (legacy writers removed).
  - [x] HTTP transport posts dispatcher events for JSON payloads.
  - [ ] Streaming transport emits new JSON payloads.
  - [x] Stub sink logs events without writer methods.
- [x] Provide compatibility wrappers, then remove writer/getter APIs once WP1 call sites are migrated.

## 2. Policy DTO & Controller Update
- [x] Observation inventory & schema prototype
  - Map every `WorldState` consumer (policy runtime, training orchestrator, loop, CLI) with file:line references and required fields.
  - Capture representative tick dumps from a baseline simulation/training run for analysis.
  - Produce a draft DTO envelope (per-agent + global) and document outstanding gaps / risks prior to adapter changes.
- [~] Implement DTO dataclasses/converters plus validation harness comparing legacy observations vs DTO payloads. *(DTO models + `build_observation_envelope` landed; `SimulationLoop` caches/emits `observations_dto` with queue/running-affordance/relationship data; policy controller/ports accept DTOs. Harness `tests/core/test_sim_loop_dto_parity.py` compares DTO tensors vs legacy observations; world detachment still pending.)*
- [ ] Update `PolicyController` + scripted adapter to consume DTOs and emit `policy.metadata`, `policy.possession`, `policy.anneal.update` events (temporary legacy bridge for ML paths).
- [ ] Migrate ML adapters & training orchestrator to DTO flow; update replay/export tooling and run behavioural parity checks.
- [ ] Cleanup loop/console interactions (drop `runtime.queue_console`, remove direct `WorldState` mutation, rely on DTO/event caches).
- [ ] Document DTO schema, add guard tests, and refresh WP1/WP2 status once DTO rollout completes.

## 3. Simulation Loop Cleanup
- [ ] Replace `runtime.queue_console` usage with router-driven action application; ensure no direct `WorldState` mutation.
- [x] Emit telemetry via events only (`loop.tick`, `loop.health`, `loop.failure`); remove `record_console_results`, `record_health_metrics`, `record_loop_failure` calls.
- [ ] Delete transitional adapter handles (`legacy_runtime`, world provider shims) once WP1/WP2 confirm parity.

## 4. Testing & Parity
- [x] Add guard tests preventing reintroduction of telemetry getters/writers.
- [x] Add event-driven loop smoke tests covering stdout adapter and stub sink.
- [ ] Run parity comparison (queue fairness, rivalry counts, promotion triggers) between legacy writer path and new events.
- [ ] CI: ensure `pytest`, `ruff`, `mypy` pass with the new telemetry architecture.

## 5. Documentation & Coordination
- [ ] Update ADRs and WP1/WP2 documentation once events/DTOs land.
- [ ] Publish migration notes for downstream consumers (telemetry dashboards, policy trainer, CLI).
- [ ] Verify all WP1/WP2 blockers resolved; mark Step 8 (WP1) and Step 7 (WP2) complete and close work packages.

Keep this checklist synchronised with the implementation plan. Items marked as blocked should reference the relevant dependency or external decision.
