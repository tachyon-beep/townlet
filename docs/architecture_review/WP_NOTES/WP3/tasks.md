# WP3 Working Tasks

## 1. Telemetry Event Pipeline
- [x] Finalise event schemas (`loop.tick`, `loop.health`, `loop.failure`, `console.result`, `policy.metadata`, `stability.metrics`, `rivalry.events`) and document payload contracts (`event_schema.md`).
- [ ] Implement event dispatcher & minimal cache in telemetry core; ensure retention bounds (queue history, rivalry history, possessed agents).
- [ ] Update transports:
  - [ ] Stdout adapter shims events into `TelemetryPublisher`.
  - [ ] HTTP/streaming transport emits new JSON payloads.
  - [ ] Stub sink logs events without writer methods.
- [ ] Provide compatibility wrappers, then remove writer/getter APIs once WP1 call sites are migrated.

## 2. Policy DTO & Controller Update
- [ ] Define observation DTOs exported from `WorldContext` (ordered per-agent payloads).
- [ ] Update policy adapters (`ScriptedPolicyAdapter`, ML adapters) to consume observation DTO batches.
- [ ] Extend `PolicyController` to emit `policy.metadata`, `policy.possession`, `policy.anneal.update` events; drop loop getters.
- [ ] Migrate training/orchestrator code paths using the new DTOs; update docs/examples.

## 3. Simulation Loop Cleanup
- [ ] Replace `runtime.queue_console` usage with router-driven action application; ensure no direct `WorldState` mutation.
- [ ] Emit telemetry via events only (`loop.tick`, `loop.health`, `loop.failure`); remove `record_console_results`, `record_health_metrics`, `record_loop_failure` calls.
- [ ] Delete transitional adapter handles (`legacy_runtime`, world provider shims) once WP1/WP2 confirm parity.

## 4. Testing & Parity
- [ ] Add guard tests preventing reintroduction of telemetry getters/writers.
- [ ] Add event-driven loop smoke tests covering stdout adapter and stub sink.
- [ ] Run parity comparison (queue fairness, rivalry counts, promotion triggers) between legacy writer path and new events.
- [ ] CI: ensure `pytest`, `ruff`, `mypy` pass with the new telemetry architecture.

## 5. Documentation & Coordination
- [ ] Update ADRs and WP1/WP2 documentation once events/DTOs land.
- [ ] Publish migration notes for downstream consumers (telemetry dashboards, policy trainer, CLI).
- [ ] Verify all WP1/WP2 blockers resolved; mark Step 8 (WP1) and Step 7 (WP2) complete and close work packages.

Keep this checklist synchronised with the implementation plan. Items marked as blocked should reference the relevant dependency or external decision.
