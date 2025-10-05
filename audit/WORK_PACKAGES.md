# Work Packages

## Summary Statistics
- Priorities: CRITICAL=1, HIGH=4, MEDIUM=5, LOW=0
- Categories: Security=2, Operational=2, Performance=1, Quality=1, BestPractice=2, Enhancement=1, TechnicalDebt=1
- Effort totals (approximate):
  - CRITICAL: S (~0.5 day)
  - HIGH: S + 3×M ≈ 2.5 days
  - MEDIUM: L + 3×M + S ≈ 5.5 days


## Priority: CRITICAL

## WP-301: Harden Console Auth Defaults

**Category**: Security
**Priority**: CRITICAL
**Effort**: S (2-8hrs)
**Risk Level**: Critical

### Description
Console authentication was disabled by default and admin callers could set `mode="admin"` without verifying tokens.

### Current State
`ConsoleAuthenticator` now rejects admin requests when auth is disabled, logging `console_admin_request_rejected` and surfacing an unauthorized result. Transport/health status expose `auth_enabled`, and telemetry health payloads report whether console auth is active. Default configs still start with auth disabled but clearly block admin commands and warn operators.

### Desired State
Admin-only actions must be gated by explicit tokens. When auth is disabled, admin commands should be refused with a clear warning while viewer commands continue to work.

### Impact if Not Addressed
Unauthenticated clients can execute admin console commands, undermining safety controls and allowing arbitrary world mutations or promotion triggers.

### Proposed Solution
- Refuse admin commands when auth is disabled; require `console_auth.enabled=true` to expose admin handlers.
- Surface a startup warning when auth is off and record auth status in telemetry.
- Add regression tests for viewer/admin splits and ensure CLI defaults enable auth in non-dev configs.

### Affected Components
- src/townlet/console/auth.py
- src/townlet/telemetry/publisher.py
- src/townlet/core/sim_loop.py
- tests/test_console_auth.py
- tests/test_telemetry_worker_health.py

### Dependencies
- None

### Acceptance Criteria
- [x] Admin-only handlers reject requests unless a valid token is supplied.
- [x] Default configs no longer allow `mode="admin"` without auth.
- [x] Tests cover viewer/admin splits and log emission when auth disabled.

### Progress
- Phase 4 (integration & validation) now removing PolicyRuntime shims; training suites passing with the new orchestrator surface.
- Phase 0 (risk prep) complete: baseline console auth tests (`pytest tests/test_console_auth.py`) confirmed prior downgrade behaviour and warning.
- Phase 1 (design) complete: planned admin rejection, structured logging, and telemetry status exposure.
- Phase 2 (implementation) complete: auth rejects admin when disabled, logs `console_admin_request_rejected`, and transport status records `auth_enabled`.
- Phase 3 (validation) complete: console auth tests updated, telemetry health metrics asserted, full pytest suite green (497 passed / 1 skipped).
- Phase 4 (docs & wrap-up) complete: work package updated; operators can inspect `telemetry_console_auth_enabled`.

## WP-302: Require Secure Telemetry Transport Defaults

**Category**: Security
**Priority**: HIGH
**Effort**: M (1-3 days)
**Risk Level**: High

### Description
Telemetry transport defaults to plaintext TCP unless operators opt into TLS, leaving data in transit exposed.

### Current State
`TelemetryTransportConfig` now defaults TCP endpoints to TLS, plaintext overrides demand explicit dev flags and localhost targets, and telemetry publisher logs whenever plaintext is enabled. Documentation and operator guides capture the new safeguards.

### Desired State
TLS should be the default for TCP transport, with plaintext limited to explicit dev overrides that require multiple safeguards. Misconfigurations must surface clear errors/warnings.

### Impact if Not Addressed
Telemetry data and console responses could traverse networks unencrypted, exposing sensitive behavioural metrics and allowing tampering.

### Proposed Solution
- Default TCP transports to TLS unless plaintext is explicitly allowed.
- Tighten validation for plaintext overrides (require dev flag + localhost + explicit opt-in).
- Emit warnings/status flags when running in plaintext.
- Update docs/tests to cover certificate configuration and insecure overrides.

### Affected Components
- src/townlet/config/loader.py
- src/townlet/telemetry/transport.py
- src/townlet/telemetry/publisher.py
- tests/test_telemetry_transport.py
- docs/ops/CONSOLE_ACCESS.md

### Dependencies
- None

### Acceptance Criteria
- [x] TLS-enabled TCP transport works out of the box with sample certs.
- [x] Plaintext overrides require explicit dev flags and localhost targets.
- [x] Tests/documentation updated to reflect secure defaults.

### Progress
- Phase 0 (risk prep) complete: baseline transport tests (`pytest tests/test_telemetry_transport.py`) and default config inspection confirmed the insecure defaults.
- Phase 1 (design) complete: planned TLS-by-default, dev-only plaintext overrides, structured warnings/status flags, and documentation updates.
- Phase 2 (implementation) complete: validator now defaults TCP transports to TLS, restricts plaintext to localhost dev overrides, and telemetry publisher logs plaintext usage.
- Phase 3 (validation) complete: targeted tests (`tests/test_telemetry_transport.py`, `tests/test_console_auth.py`, `tests/test_telemetry_worker_health.py`) passed; simulation smoke (`scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 200`) captured in `tmp/wp302_phase3/` with plaintext warning evidence.
- Phase 4 (docs & wrap-up) complete: updated `docs/ops/CONSOLE_ACCESS.md`, `docs/audit/M4_ROLLOUT_PLAN.md`, and checked acceptance criteria into this audit log.

### Related Issues
- Ties to WP-302 for secure transport guidance.


## Priority: HIGH

## WP-303: Guard Telemetry Flush Worker Failures

**Category**: Operational
**Priority**: HIGH
**Effort**: S (2-8hrs)
**Risk Level**: High

### Description
The telemetry flush thread runs without exception guards or liveness checks; any runtime error silently kills telemetry streaming.

### Current State
`TelemetryPublisher` now captures flush-loop exceptions, records `last_worker_error`, and attempts bounded auto-restarts (default 3) before halting. Transport status exposes `worker_alive`, restart counts, and the last failure message, and the stop path clears pending restarts.

### Desired State
Flush worker failures should be caught, surfaced via state, and optionally retried/restarted so operators can react.

### Impact if Not Addressed
Telemetry and console command delivery can halt silently, eroding observability and promotion readiness.

### Proposed Solution
- Wrap the flush loop with exception handling that records failure state and triggers a restart or fails fast.
- Expose a heartbeat flag via `export_state()` and log CRITICAL errors when the worker dies.
- Add unit tests simulating flush exceptions.

### Affected Components
- src/townlet/telemetry/publisher.py
- tests/test_telemetry_stream_smoke.py
- tests/test_telemetry_worker_health.py

### Dependencies
- None, though complements WP-304 for broader health coverage.

### Acceptance Criteria
- [x] Flush thread failures set a health flag and produce structured logs.
- [x] Optional auto-restart or explicit shutdown path implemented.
- [x] Tests assert health flag toggling on simulated failure.

### Progress
- Phase 0 (risk prep) complete: baseline smoke tests (`pytest tests/test_telemetry_stream_smoke.py`) confirmed existing worker died silently on errors.
- Phase 1 (design) complete: defined restart strategy (status flags, restart limit, pending restart gate).
- Phase 2 (implementation) complete: added failure handling with restart attempts, `last_worker_error`, and shutdown-aware stop logic.
- Phase 3 (validation) complete: restart/limit tests added (`test_telemetry_stream_smoke.py`, `test_telemetry_worker_health.py`); full pytest run green (495 passed / 1 skipped).
- Phase 4 (docs & wrap-up) complete: work package updated; transport status now documents restart metadata.

### Related Issues
- Feeds into risk R-003 in the risk register.


## WP-305: Introduce Spatial Indexing for Local Views

**Category**: Performance
**Priority**: HIGH
**Effort**: M (1-3 days)
**Risk Level**: High

### Description
`WorldState.local_view` rebuilds agent/object lookups by scanning every agent for each request, leading to O(n²) behaviour as populations grow.

### Current State
`WorldSpatialIndex` now maintains agent buckets and reservation tiles (`src/townlet/world/grid.py`). `local_view` / `build_local_cache` consume the index, observation builders run against the accessor path, and benchmarks with 50 agents (radius 1/3/5) measure ~0.0049/0.0209/0.0465 ms per view. Regression tests cover respawn/move/kill flows plus reservation churn (`tests/test_world_spatial_index.py`).

### Desired State
Maintain spatial indices (per-tile buckets or uniform grid) that can be updated incrementally, reducing local view construction to O(k) for neighbourhood size.

### Impact if Not Addressed
Observation building and policy loops will degrade rapidly as agent counts increase, blocking planned scale-outs.

### Proposed Solution
- Introduce a spatial index maintained during agent/object movement updates.
- Update `local_view` to query the index instead of scanning full collections.
- Add microbenchmarks and regression tests verifying performance at higher agent counts.

### Affected Components
- src/townlet/world/grid.py
- src/townlet/world/observation.py
- tests/test_world_local_view.py
- tests/test_world_observation_helpers.py
- tests/test_world_spatial_index.py

### Dependencies
- Coordinate with WP-306 to avoid duplicate structural work.

### Acceptance Criteria
- [x] Benchmarks show near-linear behaviour in radius instead of agent count.
- [x] Tests cover index updates during moves/spawns/despawns.
- [x] Observation builders consume the new index without regressions.

### Related Issues
- Mitigates performance risk R-004.


## WP-309: Complete Compact Observation Variant

**Category**: Enhancement
**Priority**: HIGH
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
The compact observation variant returned zero tensors, preventing configs marked `observations: compact` from functioning.

### Current State
Compact observations now emit a populated map tensor (configurable window/channels) backed by the spatial index, with metadata documenting channel layout and compact settings. Policy/runtime consumers accept the schema, tests cover occupancy semantics, and documentation describes the contract.

### Desired State
Compact observations should include a reduced feature vector and minimal spatial map consistent with network expectations.

### Impact if Not Addressed
Compact-mode experiments and documentation remain blocked, reducing flexibility for scale testing.

### Proposed Solution
- Define the compact schema (channels, feature ordering) aligned with policy models.
- Implement tensor population and update UI/telemetry validation tests.
- Extend tests in `tests/test_observation_builder_compact.py` to assert contents.

### Affected Components
- src/townlet/observations/builder.py
- tests/test_observation_builder_compact.py
- tests/test_observation_baselines.py
- docs/design/OBSERVATION_TENSOR_SPEC.md

### Dependencies
- None, though coordination with WP-305 ensured shared spatial index usage.

### Acceptance Criteria
- [x] Compact builder returns populated tensors matching design spec.
- [x] Policy runners accept compact observations without requiring hybrid/full.
- [x] Documentation updated for compact feature availability.

### Progress
- Phase 0 (risk prep) complete: baseline compact tests (`pytest tests/test_observation_builder_compact.py`) and dependency review.
- Phase 1 (config scaffolding) complete: introduced `CompactObservationConfig` and builder wiring.
- Phase 2 (builder implementation) complete: generated compact map tensor with configurable normalization and metadata.
- Phase 3 (runtime alignment) complete: verified metadata/channel consumption by downstream pipelines.
- Phase 4 (validation) complete: updated tests/baselines, perf spot-check (~3.65 ms per 50-agent build), full pytest green.
- Phase 5 (docs & wrap-up) complete: tensor spec updated, work package closed with acceptance criteria ticked.

### Related Issues
- Eliminates enhancement risk R-005.


## Priority: MEDIUM

## WP-306: Decompose WorldState and PolicyRuntime

**Category**: Quality
**Status**: Complete
**Priority**: MEDIUM
**Effort**: L (3-10 days)
**Risk Level**: High

### Description
`WorldState` and `PolicyRuntime` are monolithic (2700+ and 1400+ lines respectively), mixing console, telemetry, employment, and policy responsibilities.

### Current State
The classes span numerous responsibilities with nested helpers, complicating reviews and increasing regression risk (`src/townlet/world/grid.py:178-2700`, `src/townlet/policy/runner.py:1-1481`).

### Desired State
Extract dedicated modules for console bridge, employment engine, affordance runtime, and policy heads with explicit interfaces.

### Impact if Not Addressed
Future changes risk cross-cutting regressions, slowing development and making bug fixes error-prone.

### Proposed Solution
- Follow the refactor roadmap in `docs/engineering/WORLDSTATE_REFACTOR.md`.
- Stage extraction into discrete modules with targeted unit tests.
- Introduce lightweight context objects to eliminate circular imports.

### Affected Components
- src/townlet/world/grid.py
- src/townlet/world/console_bridge.py
- src/townlet/world/employment.py
- src/townlet/policy/runner.py

### Dependencies
- Coordinate with WP-305 to avoid conflicting structural changes.

### Acceptance Criteria
- [x] Responsibilities distributed across focused modules with matching tests.
- [x] Public APIs documented and consumed by `SimulationLoop` without behavioural drift.
- [x] CI suite extended to guard extracted modules.

### Related Issues
- Mitigates maintainability portion of risk R-004.


## WP-304: Add Simulation Loop Health & Recovery Hooks

**Category**: Operational
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
The main loop lacks panic handling; exceptions propagate and halt the simulation with no structured error reporting.

### Current State
`SimulationLoop.run` simply yields `step()` results (`src/townlet/core/sim_loop.py:181-238`), so runtime errors fail hard without cleanup, snapshotting, or alerts.

### Desired State
Provide error interception that captures snapshots, emits telemetry alerts, and optionally restarts or exits gracefully.

### Impact if Not Addressed
Transient bugs crash long-running runs silently, causing data loss and unobserved outages.

### Proposed Solution
- Wrap loop iterations with try/except, logging structured telemetry alerts and capturing diagnostics.
- Provide hooks for external supervisors (CLI, training harness) to recover or exit with context.
- Add integration tests simulating failures in affordance resolution.

### Affected Components
- src/townlet/core/sim_loop.py:181-276
- scripts/run_simulation.py

### Dependencies
- Complements WP-303 for holistic health coverage.

### Acceptance Criteria
- [x] Loop surfaces structured failure telemetry and console output.
- [x] Hooks allow CLI to exit gracefully with non-zero status.
- [x] Regression tests verify snapshot capture on crash.

### Related Issues
- Linked to operational risk R-003.

### Progress
- Phase 0 (risk prep) complete: baseline `tests/test_sim_loop_structure.py` run recorded in `tmp/wp304/baseline_tests.log`.
- Phase 1 (design) captured in `tmp/wp304/design.md` outlining health state and failure hooks.
- Phase 2 (implementation) complete: added `SimulationLoopHealth`, failure handler registration, and telemetry failure reporting (`src/townlet/core/sim_loop.py`, `src/townlet/telemetry/publisher.py`).
- Phase 3 (validation) complete: see `tmp/wp304/validation_tests.log` for pytest/ruff commands (all green).
- Phase 4 (docs & integration) complete: CLI failure handling wired in `scripts/run_simulation.py`, policy docs/tests updated, and orchestrator surfaces documented.


## WP-307: Raise API Docstring Coverage & Developer Docs

**Category**: BestPractice
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
Only ~16% of callables carry docstrings, leaving public APIs under-documented.

### Current State
Static analysis shows 267 docstrings across 1,708 callables (`audit/module metadata`).

### Desired State
All exported modules, classes, and public methods should describe behaviour and side effects, with docs summarising module responsibilities.

### Impact if Not Addressed
Onboarding friction remains high; reviewers must infer behaviour from code.

### Proposed Solution
- Prioritise documenting exported classes/functions in `src/townlet` and `src/townlet_ui`.
- Add docstring coverage checks (e.g., `interrogate` or custom pytest plugin).
- Update `docs/` with API reference sections for key services.

### Affected Components
- src/townlet/**
- src/townlet_ui/**
- docs/

### Dependencies
- None

### Acceptance Criteria
- [ ] Docstring coverage exceeds 60% for public APIs.
- [ ] CI fails when new exported functions lack docstrings.
- [ ] Documentation includes updated module overviews.

### Related Issues
- Supports mitigation of knowledge risks in R-006.


## WP-308: Provide Reproducible Container & Secrets Model

**Category**: BestPractice
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
There is no Dockerfile or deployment manifest, complicating reproducibility and secret injection.

### Current State
Project relies on manual virtualenv setup; docs reference TODO for containerization.

### Desired State
Offer a container image (or devcontainer) bundling dependencies with secret management guidance for console tokens and TLS certs.

### Impact if Not Addressed
Environment drift and secret handling remain ad-hoc, increasing operational risk during rollout.

### Proposed Solution
- Create Dockerfile/devcontainer configs with multi-stage build.
- Document env var injection for console auth and TLS assets.
- Update CI to build image for smoke testing if feasible.

### Affected Components
- New Dockerfile/devcontainer files
- docs/ops/CONTAINER_GUIDE.md (new)

### Dependencies
- Builds on WP-302 for TLS documentation.

### Acceptance Criteria
- [ ] Container builds and runs `scripts/run_simulation.py` with sample config.
- [ ] Documentation explains secrets mounting and volume layout.
- [ ] Optional CI job validates image build.

### Related Issues
- Addresses deployment readiness noted in risk R-002.


## WP-310: Persist Affordance Outcome Metadata

**Category**: TechnicalDebt
**Priority**: MEDIUM
**Effort**: S (2-8hrs)
**Risk Level**: Medium

### Description
Affordance outcomes drop affordance/object IDs, limiting debugging after actions complete.

### Current State
`apply_affordance_outcome` logs metadata in an ad-hoc list with a TODO for richer fields (`src/townlet/world/affordances.py:120-156`).

### Desired State
Include affordance/object identifiers and timestamps in agent snapshots or structured telemetry without relying on metadata lists.

### Impact if Not Addressed
Operators lack context for recent actions, hampering post-incident analysis and delaying validation of affordance tweaks.

### Proposed Solution
- Extend `AgentSnapshot` to carry recent affordance summary with IDs.
- Update telemetry and UI overlays to display the enriched metadata.
- Add tests covering affordance completion paths.

### Affected Components
- src/townlet/world/affordances.py:120-156
- src/townlet/world/grid.py
- tests/test_affordance_hooks.py

### Dependencies
- None

### Acceptance Criteria
- [ ] Snapshot includes affordance/object IDs without relying on TODO metadata.
- [ ] Telemetry exposes the richer data and UI renders it.
- [ ] Tests validate metadata persistence.

### Related Issues
- Closes technical debt risk R-007.

