# WP3 Implementation Plan — Event-First Telemetry & Policy DTOs

This plan enumerates the concrete steps required to deliver Work Package 3. Update the checklist as each task progresses.

## 0. Foundations & Design (✔ planned)
- Finalise telemetry event schema (`loop.tick`, `loop.health`, `loop.failure`, policy-related events).
- Define observation DTO surfaces for policy adapters (scripted + ML backends).
- Agree on compatibility strategy for legacy transports (stdout, HTTP) and stubs.

## 1. Telemetry Sink Refactor

### 1.1 Event schema & core sink
- [x] Finalise payload schemas (see `event_schema.md`) for:
  - `loop.tick` (world snapshot reference, rewards, policy snapshot, stability inputs, perturbations, metadata).
  - `loop.health` (duration, queue depth, transport status, promotion snapshot, stability metrics summary).
  - `loop.failure` (tick, error, snapshot path, transport status).
  - `console.result`, `policy.metadata`, `stability.metrics`, `rivalry.events`.
- [ ] Implement an event dispatcher inside the telemetry package that:
  - Persists minimal caches for downstream APIs (queue history, rivalry history, possessed agents) with bounded retention.
  - Applies transform pipelines (schema validation, fan-out) before handing payloads to transports.
  - Exposes subscription hooks for observers (replacing the current `register_event_subscriber` pattern).

### 1.2 Adapter updates
- [ ] `StdoutTelemetryAdapter` – translate new events into the legacy publisher interface (temporary shim) and log non-loop events for debugging.
- [ ] HTTP/streaming transports – define JSON payload shapes and update clients accordingly.
- [ ] Stub telemetry – accept all events/metrics and retain lightweight caches for testing purposes.

### 1.3 Legacy API sunset
- [ ] Provide compatibility wrappers that convert legacy writer calls into events (used only during migration).
- [ ] Remove `publish_tick`, `record_console_results`, `record_health_metrics`, `record_loop_failure`, and all `latest_*` getters once WP1/WP2 call sites are migrated.
- [ ] Update `TelemetrySinkProtocol` to mark removed methods as deprecated (retained temporarily for type-checkers until call sites are cleaned).

### 1.4 WP1 / WP2 Link
- WP1 Step 8 requires the event dispatcher before its checklist can be closed.
- WP2 adapters should switch to emitting rivalry/queue events through the new sink.

## 2. Policy Observation & Metadata Streaming

### 2.1 Observation DTOs
- [ ] Define canonical observation structures (per-agent dict) and export them from `WorldContext` / observation builder.
- [ ] Update policy ports & adapters to accept observation batches instead of a `WorldState` reference (scripted backend may still peek at `WorldRuntimeAdapter` through a transitional hook).
- [ ] Provide helper functions for deterministic ordering and validation (re-usable by trainers).

### 2.2 Metadata events
- [ ] Extend `PolicyController` to emit:
  - `policy.metadata` (hash, anneal ratio, provider name, tick).
  - `policy.possession` (list of possessed agents and change events).
  - `policy.anneal.update` (ratio changes, enabling WP1 to drop `set_anneal_ratio` direct calls).
- [ ] Update loop to consume these events and remove direct metadata queries.

### 2.3 Training integration
- [ ] Audit training harness for dependencies on legacy getters; provide adapters or migrations.
- [ ] Update documentation for policy DTO consumers.

## 3. Simulation Loop Finalisation

### 3.1 Console & world interactions
- [ ] Replace `runtime.queue_console` usage with a router-driven flow:
  - Router translates incoming commands to world actions.
  - Loop applies actions via `world_port.apply_actions` and `world_port.tick`.
- [ ] Remove direct mutation of `WorldState` (`world.agents` iteration should happen through views/DTOs).

### 3.2 Telemetry cleanup
- [ ] Swap remaining `telemetry.record_*` invocations for event emissions (`loop.health`, `loop.failure`).
- [ ] Remove the fallback transport status cache once the sink provides a live feed.

### 3.3 Closure steps
- [ ] Update WP1/WP2 docs to mark Step 8 complete.
- [ ] Remove transitional handles from adapters (`legacy_runtime`, world provider shims).
- [ ] Archive legacy factory registry (`core/factory_registry.py`) once all entry points use the new factories.

## 4. Testing & Validation

### 4.1 Unit & integration tests
- [ ] Guard test ensuring `latest_*` identifiers (`telemetry.latest_`) are absent from source tree.
- [ ] Event-driven smoke test exercising `SimulationLoop` with stdout telemetry.
- [ ] Telemetry sink unit tests verifying retention bounds, subscriber hooks, and transform pipeline.

### 4.2 Regression / parity checks
- [ ] Compare key metrics (queue fairness, rivalry counts, promotion triggers) between legacy and new pipelines.
- [ ] Validate console command behaviour via `ConsoleRouter` integration tests.

## 5. Rollout & Documentation

### 5.1 Documentation
- [ ] Update ADR-001 (ports) and add a new ADR for event-driven telemetry.
- [ ] Document policy DTO schema and sample payloads for training pipelines.

### 5.2 Migration guidance
- [ ] Publish a migration checklist for downstream teams (telemetry dashboards, policy trainer, CLI).
- [ ] Coordinate release notes with WP1/WP2 completion announcements.

### 5.3 Cross-package closure
- [ ] Confirm WP1 Step 8 tasks marked complete after telemetry/policy migrations.
- [ ] Confirm WP2 Step 7 tasks marked complete once observation DTOs land.

## 4. Testing & Validation
4.1 Add guard tests to confirm writer/getter APIs are unused (`tests/test_telemetry_getters_removed.py`).
4.2 Provide event-driven integration smoke tests (loop + stdout adapter).
4.3 Run full suite (`pytest`, `ruff`, `mypy`) and targeted e2e scripts.

## 5. Rollout & Documentation
5.1 Document the new telemetry event schema and policy DTOs (README, ADR updates).
5.2 Communicate migration notes for downstream consumers (telemetry pipeline, training harness).
5.3 Coordinate with WP1/WP2 owners to close out their remaining checklist items.

## Blockers & Risks
- Telemetry transports must accept the new event format; rollout requires coordination to avoid breaking downstream tools.
- Policy adapters need deterministic DTOs; any deviation from legacy `WorldState` access requires thorough parity testing.

Track progress alongside `tasks.md` so remaining work is visible to WP1/WP2 stakeholders.
