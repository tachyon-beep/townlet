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
- [x] Implement an event dispatcher inside the telemetry package that:
  - Persists minimal caches for downstream APIs (queue history, rivalry history, possessed agents) with bounded retention.
  - Applies transform pipelines (schema validation, fan-out) before handing payloads to transports.
  - Exposes subscription hooks for observers (replacing the current `register_event_subscriber` pattern).

### 1.2 Adapter updates
- [x] Introduced `TelemetryEventDispatcher` with bounded queue/rivalry caches (`telemetry/event_dispatcher.py`) and registered it within `TelemetryPublisher`.
- [x] `StdoutTelemetryAdapter` now relays events through the dispatcher (legacy writers removed).
- [x] Stub telemetry accepts events/metrics and logs them for diagnostics.
- [~] HTTP/streaming transports – HTTP transport now posts dispatcher events; streaming/WebSocket support remains to be implemented when required.

### 1.3 Legacy API sunset
- [x] Provide compatibility wrappers that convert legacy writer calls into events (used only during migration).
- [x] Remove `publish_tick`, `record_console_results`, `record_health_metrics`, and `record_loop_failure` once WP1/WP2 call sites are migrated.
- [ ] Retire remaining `latest_*` compatibility getters after downstream consumers switch to event-driven caches.
- [x] Update `TelemetrySinkProtocol` to reflect the event-only surface.
  - Plan: once HTTP/other transports are event-backed, prune unused caches from `TelemetryPublisher`.

### 1.4 WP1 / WP2 Link
- WP1 Step 8 requires the event dispatcher before its checklist can be closed.
- WP2 adapters should switch to emitting rivalry/queue events through the new sink.

## 2. Policy Observation & Metadata Streaming

### 2.1 Observation DTOs
- [x] **Observation inventory & schema prototype**
  - **Collect callers:** trace every `WorldState` access under `policy/`, `core/sim_loop.py`, training orchestrator, CLI tools; record attribute/method usage with file:line references. *(Captured in `dto_observation_inventory.md`.)*
  - **Capture sample data:** run a short simulation/training smoke (baseline config) and persist representative tick payloads (observations, rewards, queue metrics, rivalry events) for analysis. *(See `dto_sample_tick.json` / `dto_example_tick.json`.)*
  - **Gap analysis:** compare required fields with what `WorldContext`/observation builder currently expose; flag missing elements (agent ordering, RNG seeds, historical metrics).
  - **Schema draft:** propose DTO structure (per-agent + global envelope) and document field definitions, types, and provenance; circulate for review with policy/training owners.
  - **Parity notes:** highlight metrics that cannot yet be satisfied, plus risk mitigations/owners before moving to adapter work.

- [~] **DTO dataclasses & validation helpers**
  - **Surface defined:** DTO models live in `src/townlet/world/dto/observation.py` and export via `townlet.world.dto`; `DTO_SCHEMA_VERSION` anchored at `0.1.0`.
  - **Converter inputs:** Simulation loop already produces the required artefacts — `observations` (numpy-backed tensors), `RuntimeStepResult.actions`, `terminated`/`termination_reasons`, reward totals + breakdown, queue metrics, perturbation state, policy snapshot/identity (hash, provider, anneal), possessed agents, rivalry/stability metrics, and the world RNG seed via `WorldRuntimeAdapter`. The converter will consume these and emit JSON-friendly payloads with deterministic agent ordering.
  - **Factory implemented:** `src/townlet/world/dto/factory.py::build_observation_envelope` builds immutable envelopes (numpy → lists, dataclass/action coercion, deterministic ordering).
  - **Loop integration:** `SimulationLoop` now assembles DTO envelopes each tick, caches them for the next decision, and emits them alongside `loop.tick` telemetry as `observations_dto`.
  - **Controller/port wiring:** `PolicyController` and policy ports accept DTO envelopes + observation batches; `ScriptedPolicyAdapter` forwards cached DTOs to the backend for action selection while retaining world fallbacks.
  - **Schema enrichment:** DTO global context now carries queue rosters, running affordances, and relationship metrics populated by the loop; fixtures/tests updated (`docs/.../dto_example_tick.json`, `tests/world/test_observation_dto_factory.py`, `tests/core/test_sim_loop_dto_parity.py`).
  - **Parity harness:** `tests/core/test_sim_loop_dto_parity.py` runs a stubbed simulation loop for several ticks and asserts that DTO tensors match the legacy observation batch.
  - Implement immutable DTO structures and converters inside `WorldContext` / observation builder. *(Converter available; integration pending.)*
  - Add validation utilities (e.g., schema checks) and parity harness comparing legacy observations to DTO payloads. *(Smoke tests live in `tests/world/test_observation_dto_factory.py`; full parity harness still to do.)*

- [ ] **Scripted adapter integration**
  - Update `PolicyController`/scripted adapter to consume DTO batches and emit `policy.metadata`, `policy.possession`, `policy.anneal.update` events.
  - Maintain a transitional adapter that still offers legacy access for ML paths until Step 2.2 completes.

- [ ] **ML/training integration**
  - Migrate ML adapters & training orchestrator to DTO inputs, update replay/export tooling, and run parity evaluation (short training run) to confirm behavioural equivalence.

- [ ] **Loop/console cleanup**
  - Remove residual `WorldState` mutations, replace `runtime.queue_console` usage with router-driven DTO actions, and ensure console handlers read from DTO caches/events.

- [ ] **Documentation & guardrails**
  - Document the DTO schema with examples, add guard tests preventing regression to `WorldState` access, and update WP1/WP2/WP3 docs once the DTO flow is live.

### 2.2 Metadata events
- [ ] Extend `PolicyController` in tandem with DTO rollout so metadata/possession/anneal events are emitted alongside observation batches; remove legacy getter usage once adapters consume the events.

### 2.3 Training integration
- [ ] Audit training harness for dependencies on legacy getters; provide adapters or migrations.
- [ ] Update documentation for policy DTO consumers.

## 3. Simulation Loop Finalisation

### 3.1 Console & world interactions
- [x] Replace `runtime.queue_console` usage with a router-driven flow:
  - Router translates incoming commands to world actions.
  - Loop applies actions via `world_port.apply_actions` and `world_port.tick` (buffered commands dropped with warning if router unavailable).
- [ ] Remove direct mutation of `WorldState` (`world.agents` iteration should happen through views/DTOs).
- [x] Ensure snapshot commands emit serialisable payloads (SnapshotState → dict) so console router remains event-driven.

### 3.2 Telemetry cleanup
- [x] Swap remaining `telemetry.record_*` invocations for event emissions (`loop.health`, `loop.failure`).
- [ ] Remove the fallback transport status cache once the sink provides a live feed.
- [x] Persist context RNG seed in snapshots so resumed runs continue deterministically.

### 3.3 Closure steps
- [ ] Update WP1/WP2 docs to mark Step 8 complete.
- [ ] Remove transitional handles from adapters (`legacy_runtime`, world provider shims).
- [ ] Archive legacy factory registry (`core/factory_registry.py`) once all entry points use the new factories.

## 4. Testing & Validation

### 4.1 Unit & integration tests
- [x] Guard test ensuring legacy writer identifiers remain absent (`tests/test_telemetry_surface_guard.py`).
- [x] Event-driven smoke test exercising `SimulationLoop` with stdout telemetry (`tests/test_telemetry_surface_guard.py`).
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
4.1 Guard tests confirm writer/getter APIs remain unused (`tests/test_telemetry_surface_guard.py`).
4.2 Event-driven integration smoke tests (loop + stdout adapter) continue to run (`tests/test_telemetry_surface_guard.py`).
4.3 Run full suite (`pytest`, `ruff`, `mypy`) and targeted e2e scripts.

## 5. Rollout & Documentation
5.1 Document the new telemetry event schema and policy DTOs (README, ADR updates).
5.2 Communicate migration notes for downstream consumers (telemetry pipeline, training harness).
5.3 Coordinate with WP1/WP2 owners to close out their remaining checklist items.

## Blockers & Risks
- Telemetry transports must accept the new event format; rollout requires coordination to avoid breaking downstream tools.
- Policy adapters need deterministic DTOs; any deviation from legacy `WorldState` access requires thorough parity testing.

Track progress alongside `tasks.md` so remaining work is visible to WP1/WP2 stakeholders.
