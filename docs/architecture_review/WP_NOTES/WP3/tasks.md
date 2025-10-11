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
- [x] Implement DTO dataclasses/converters plus validation harness comparing legacy observations vs DTO payloads. *(Schema v0.2.0 live: per-agent needs/wallet/job/inventory/personality + global employment/economy/anneal snapshots; parity harness now exercises these fields via recorded world state.)*
- [x] Update `PolicyController` + scripted adapter to consume DTOs and emit `policy.metadata`, `policy.possession`, `policy.anneal.update` events. *(SimulationLoop now streams policy metadata/possession/anneal events from DTO payloads; ML backends continue under WP3C for full parity validation.)*
- [x] Replace transitional bridges (`WorldContext.apply_actions` fallback, queue snapshot normalisation) once modular systems cover the full mutation pipeline. *(`process_actions`/`advance_running_affordances` now own the pipeline; `employment`/`economy`/`relationships` steps run each tick, and `state.resolve_affordances` is no longer invoked by the modular path.)*
- [x] Execute WP3B_plan: reattach modular systems (queues/affordances/employment/economy) and drop the legacy bridge.
- [ ] Execute WP3C_plan: expand DTO parity harness, run ML smoke, and remove legacy observation payloads. *(Stage 5 complete: loop/telemetry emit DTO-only payloads; Stage 6 guardrails/docs landed. Remaining work: ML parity + world adapter cleanup.)*
- [ ] Migrate ML adapters & training orchestrator to DTO flow; update replay/export tooling and run behavioural parity checks.
- [~] Cleanup loop/console interactions (drop `runtime.queue_console`, remove direct `WorldState` mutation, rely on DTO/event caches). *(Console routing now event-only; remaining work is removing direct `WorldState` mutations during guardrail updates.)*
- [x] Document DTO schema, add guard tests, and refresh WP1/WP2 status once DTO rollout completes. *(WP status files + ADR-001/dto_migration updated; guard tests in place.)*

## 3. Simulation Loop Cleanup
- [~] Replace `runtime.queue_console` usage with router-driven action application; ensure no direct `WorldState` mutation. *(Router-only path active; finalize once world mutation cleanup lands.)*
- [x] Emit telemetry via events only (`loop.tick`, `loop.health`, `loop.failure`); remove `record_console_results`, `record_health_metrics`, `record_loop_failure` calls.
- [x] Delete transitional adapter handles (`legacy_runtime`, world provider shims) once WP1/WP2 confirm parity. *(Default world adapter now fronts the runtime; simulation loop no longer reaches through `legacy_runtime`.)*

## 4. Testing & Parity
- [x] Add guard tests preventing reintroduction of telemetry getters/writers.
- [x] Add event-driven loop smoke tests covering stdout adapter and stub sink.
- [ ] Run parity comparison (queue fairness, rivalry counts, promotion triggers) between legacy writer path and new events. *(Queued under WP3C once DTO parity harness expands.)*
- [~] CI: ensure `pytest`, `ruff`, `mypy` pass with the new telemetry architecture. *(Targeted pytest suites green; full-project `ruff` sweep deferred to final Stage 6 wrap due to legacy style issues.)*

## 5. Documentation & Coordination
- [x] Update ADRs and WP1/WP2 documentation once events/DTOs land.
- [x] Publish migration notes for downstream consumers (telemetry dashboards, policy trainer, CLI).
- [ ] Verify all WP1/WP2 blockers resolved; mark Step 8 (WP1) and Step 7 (WP2) complete and close work packages.

Keep this checklist synchronised with the implementation plan. Items marked as blocked should reference the relevant dependency or external decision.
