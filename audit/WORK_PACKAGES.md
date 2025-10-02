# Work Packages

**Summary Dashboard**
- Priority counts: CRITICAL 1, HIGH 2, MEDIUM 7
- Category coverage: Security 2, Operational 2, CodeQuality 2, Enhancement 1, TechnicalDebt 1, BestPractice 1, Performance 1
- Estimated effort by priority: CRITICAL ≈ L (3-10 days), HIGH ≈ M (1-3 days)+S (2-8hrs), MEDIUM ≈ L (3-10 days)+S (2-8hrs)+M (1-3 days)+M (1-3 days)+S (2-8hrs)+M (1-3 days)+S (2-8hrs)

## Priority: CRITICAL

## WP-101: Secure Console & Telemetry Access Control

**Category**: Security
**Priority**: CRITICAL
**Effort**: L (3-10 days)
**Risk Level**: Critical

### Description
Console and telemetry endpoints trust the client-supplied `mode` flag and expose admin handlers without verifying caller identity.

### Current State
ConsoleCommandEnvelope lowers the `mode` string from payloads without authentication (src/townlet/console/command.py:82-110). `create_console_router` simply registers admin commands when `mode == "admin"` (src/townlet/console/handlers.py:124-911), so any client can invoke destructive operations such as `kill`, `policy_swap`, or `snapshot_migrate`. TelemetryPublisher queues commands with no issuer validation (src/townlet/telemetry/publisher.py:32-120).

### Desired State
Authenticated sessions with role-based access; viewer/admin separation enforced server-side and credentials revocable without restarting the simulator.

### Impact if Not Addressed
Unauthorised users can terminate agents, alter policy promotion, or export snapshots, compromising simulation integrity and downstream analytics.

### Proposed Solution
- Introduce a console auth service that issues signed tokens (e.g. HMAC or mutual TLS) and validate tokens inside `create_console_router` before dispatch.
- Bind transport endpoints to authenticated sessions; require issuer metadata to match the authenticated principal.
- Update `townlet_ui` to perform login/refresh flows and surface auth failures to operators.
- Add regression tests covering unauthenticated, expired, and viewer-mode elevation attempts.

### Affected Components
- src/townlet/console/command.py
- src/townlet/console/handlers.py
- src/townlet/telemetry/publisher.py
- src/townlet_ui/commands.py
- src/townlet_ui/dashboard.py

### Dependencies
- WP-102

### Acceptance Criteria
- [ ] All console commands require authenticated credentials validated server-side.
- [ ] Viewer/admin roles enforced regardless of payload `mode` field.
- [ ] Automated tests cover auth failure paths and admin happy paths.
- [ ] Operator runbooks updated with credential provisioning and rotation.

### Related Issues
- Risk Register: R-101

## Priority: HIGH

## WP-102: Encrypt Telemetry Transport & Add Endpoint Trust

**Category**: Security
**Priority**: HIGH
**Effort**: M (1-3 days)
**Risk Level**: High

### Description
Telemetry TCP transport sends newline-delimited JSON in plaintext with no peer verification.

### Current State
`TcpTransport` opens raw sockets (src/townlet/telemetry/transport.py:56-183); configs cannot supply certificates or shared secrets. Data and credentials traverse the network unencrypted.

### Desired State
TLS-protected transport with optional client certificates or token-based authentication configured through SimulationConfig.

### Impact if Not Addressed
Attackers on the network can read policy snapshots, queue metrics, or inject forged payloads leading to misleading dashboards and decisions.

### Proposed Solution
- Extend `telemetry.transport` config with TLS enable flags, certificate paths, and hostname validation options.
- Wrap TCP sockets with `ssl.SSLContext` (both server and client modes) and fail fast on certificate or hostname mismatch.
- Support pre-shared tokens in payload metadata for stdout/file transports to ease local use.
- Document certificate provisioning and add integration tests covering TLS handshake failures.

### Affected Components
- src/townlet/telemetry/transport.py
- src/townlet/config/loader.py
- docs/ops/

### Dependencies
- None

### Acceptance Criteria
- [ ] TLS-enabled TCP transport configurable via SimulationConfig.
- [ ] Unit tests assert handshake failure on invalid certs/hostnames.
- [ ] Documentation covers certificate management and fallback options.

### Related Issues
- Risk Register: R-102
- WP-101

## WP-103: Expose Telemetry Buffer Health & Dropped Payload Alerts

**Category**: Operational
**Priority**: HIGH
**Effort**: S (2-8hrs)
**Risk Level**: Medium

### Description
Telemetry buffer drops payloads silently after repeated send failures; operators only see debug logging.

### Current State
`_flush_transport_buffer` increments `dropped_messages` and clears the queue without emitting alerts or telemetry (src/townlet/telemetry/publisher.py:430-520). `latest_health_status()` omits queue saturation, so dashboards cannot alarm on sustained loss.

### Desired State
Telemetry health payload includes queue depth, drop counts, and retry streak metrics with configurable alert thresholds.

### Impact if Not Addressed
Missed payloads hide stability regressions and render dashboards inaccurate, delaying incident response during promotions or soak tests.

### Proposed Solution
- Publish `dropped_messages`, queue depth, and last error fields into the health snapshot (src/townlet/telemetry/publisher.py:581-620).
- Add warning log + console notification when drops exceed configurable per-minute thresholds.
- Extend tests (`tests/test_telemetry_transport.py`) to assert alert emission when backpressure triggers.
- Document operational runbook for interpreting transport health metrics.

### Affected Components
- src/townlet/telemetry/publisher.py
- src/townlet/telemetry/transport.py
- tests/test_telemetry_transport.py

### Dependencies
- None

### Acceptance Criteria
- [ ] Health snapshots expose queue depth and cumulative drop counters.
- [ ] Drop threshold triggers warning log and console event.
- [ ] Tests assert alert path when mock transport repeatedly fails.
- [ ] Operations guide updated with troubleshooting steps.

### Related Issues
- Risk Register: R-103

## Priority: MEDIUM

## WP-104: Decompose WorldState Into Focused Modules

**Category**: CodeQuality
**Priority**: MEDIUM
**Effort**: L (3-10 days)
**Risk Level**: High

### Description
`WorldState` mixes agent lifecycle, queue fairness, economy, rivalry, console hooks, and affordance execution inside a 2700-line module, complicating fixes and reviews.

### Current State
`src/townlet/world/grid.py` defines seven classes and 104 WorldState methods spanning employment, rivalry, perturbations, and telemetry glue, with multiple TODO markers (lines 1297 and 1329).

### Desired State
Modularised world subsystem with dedicated components for affordance execution, employment queues, rivalry ledger interaction, and console integration.

### Impact if Not Addressed
High complexity raises regression risk and slows onboarding; observers cannot reason about world state transitions without tracing thousands of lines.

### Proposed Solution
- Extract employment queue logic into `world/employment.py` with a clear API consumed by WorldState.
- Move affordance execution & hooks into `world/affordances.py`, enabling targeted tests.
- Introduce interfaces for rivalry/relationship mutations so telemetry and stability layers depend on explicit contracts.
- Add module-level documentation and unit tests per new component.

### Affected Components
- src/townlet/world/grid.py
- src/townlet/world/queue_manager.py
- src/townlet/world/relationships.py
- tests/test_world_*

### Dependencies
- None

### Acceptance Criteria
- [ ] WorldState drops below 800 lines with cohesive responsibilities.
- [ ] New submodules expose documented interfaces with dedicated tests.
- [ ] Existing test suite passes without behavioural regressions.
- [ ] Module documentation updated to reflect new structure.

### Related Issues
- Risk Register: R-104

## WP-110: Raise Documentation & Docstring Coverage

**Category**: CodeQuality
**Priority**: MEDIUM
**Effort**: S (2-8hrs)
**Risk Level**: Low

### Description
Only ~11% of functions/methods carry docstrings, making onboarding and API usage error-prone.

### Current State
Automated scan shows 1090 of 1225 callable definitions lack docstrings (audit/module_metadata.json). Critical modules such as `SimulationLoop` and `WorldState` have undocumented methods.

### Desired State
Docstring coverage for public APIs and complex helpers, with developer guide referencing the new documentation.

### Impact if Not Addressed
Low discoverability increases review time and risk of misuse when extending policies or telemetry.

### Proposed Solution
- Prioritise docstrings for exported classes/functions in `src/townlet` and CLI entry points.
- Add `pydocstyle` (or Ruff D rules) gating to CI to keep coverage high.
- Update contributor guide describing documentation expectations.

### Affected Components
- src/townlet/core/sim_loop.py
- src/townlet/world/grid.py
- scripts/*.py
- CONTRIBUTING.md

### Dependencies
- None

### Acceptance Criteria
- [ ] Docstring coverage raised above 60% for callable definitions in src.
- [ ] CI fails when new public functions lack docstrings.
- [ ] Contributor guide updated with docstring checklist.

### Related Issues
- None

## WP-106: Wire Affordance Hooks Into World Execution

**Category**: TechnicalDebt
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
Affordance hook registry is defined but never invoked when actions complete, leaving TODO markers and missing extension points.

### Current State
WorldState.resolve_affordances leaves TODO for hook dispatch (src/townlet/world/grid.py:1329) and agent snapshot updates (line 1297).

### Desired State
Actions trigger registered before/after hooks with well-defined payloads, enabling scripted side effects and telemetry enrichment.

### Impact if Not Addressed
Feature teams cannot extend affordances (e.g., economy or narrative triggers) without editing core logic.

### Proposed Solution
- Define hook payload schema and invoke `HookRegistry.handlers_for` before/after affordance execution.
- Update agent snapshots (energy, inventory) inside `_apply_affordance_effects`.
- Provide tests covering custom hook modules under `world/hooks/`.
- Document hook lifecycle in `docs/design/affordances.md`.

### Affected Components
- src/townlet/world/grid.py
- src/townlet/world/hooks/default.py
- docs/design/affordances.md

### Dependencies
- WP-104

### Acceptance Criteria
- [ ] Hooks execute for affordance begin/after with deterministic payloads.
- [ ] Agent snapshots reflect affordance outcomes without manual patching.
- [ ] Test suite includes custom hook integration case.

### Related Issues
- Risk Register: R-104

## WP-107: Add Container & Deployment Tooling

**Category**: BestPractice
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
Repository lacks Docker images, compose manifests, or deployment runbooks, making environment parity hard to guarantee.

### Current State
There is no Dockerfile or orchestration config in the repo; docs assume local venv only. Telemetry paths use local filesystem relative to repo.

### Desired State
Reproducible container image with entrypoints for simulation and training plus documentation for running under Compose or Kubernetes.

### Impact if Not Addressed
Operational rollout to staging/prod environments is manual and error-prone, limiting collaboration and infra automation.

### Proposed Solution
- Create multi-stage Dockerfile bundling runtime dependencies and optional GPU torch layer.
- Supply docker-compose example wiring telemetry output volume and config mounts.
- Document environment variables, secrets, and persistent volume expectations.
- Integrate container build into CI to catch dependency regressions.

### Affected Components
- Dockerfile (new)
- docker-compose.yml (new)
- docs/ops/DEPLOYMENT.md

### Dependencies
- WP-102

### Acceptance Criteria
- [ ] Docker image builds cleanly with `pip install -e .` and runs `scripts/run_simulation.py`.
- [ ] Compose example starts telemetry + UI stack with mounted config.
- [ ] Ops documentation lists env vars and secrets handling.
- [ ] CI publishes image artifact on main branch.

### Related Issues
- Risk Register: R-106

## WP-109: Profile Tick Loop & Optimise Hot Paths

**Category**: Performance
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
Tick loop iterates over large agent dictionaries multiple times per tick without caching, risking slowdowns as population scales.

### Current State
`SimulationLoop.step` and `WorldState.resolve_affordances` perform repeated full-agent scans (src/townlet/core/sim_loop.py:167-266, src/townlet/world/grid.py:1200-1500). No profiling harness exists.

### Desired State
Profiling data and targeted optimisations (e.g., memoised neighbourhood queries, batched updates) to keep tick duration within budget.

### Impact if Not Addressed
Without optimisation, tick duration grows superlinearly, undermining soak tests and real-time dashboards.

### Proposed Solution
- Instrument tick loop with timing hooks (per phase) and emit metrics via telemetry health payload.
- Use profiling runs (scripts/benchmark_tick.py) on representative configs to identify hotspots.
- Optimise critical sections (e.g., precompute queue snapshots, cache rivalry lookups) and add regression tests for tick duration thresholds.

### Affected Components
- src/townlet/core/sim_loop.py
- src/townlet/world/grid.py
- scripts/benchmark_tick.py
- tests/test_sim_loop_snapshot.py

### Dependencies
- WP-104

### Acceptance Criteria
- [ ] Benchmark script records target tick duration (document target threshold).
- [ ] Telemetry health payload exposes phase timings for monitoring.
- [ ] Optimised code paths covered by unit/integration tests.

### Related Issues
- Risk Register: R-103
- Risk Register: R-104

## WP-105: Implement Compact Observation Variant

**Category**: Enhancement
**Priority**: MEDIUM
**Effort**: S (2-8hrs)
**Risk Level**: Medium

### Description
Observation builder lacks the compact variant promised by feature flags, blocking downstream experiments that rely on reduced tensors.

### Current State
`ObservationBuilder._build_single` falls back to zero tensors and TODO marker when `variant == "compact"` (src/townlet/observations/builder.py:285-303).

### Desired State
Compact variant that emits feature-complete but size-optimised tensors with parity to hybrid/full variants.

### Impact if Not Addressed
Agents configured for compact observations receive empty inputs, leading to undefined behaviour and invalid training runs.

### Proposed Solution
- Define compact channel layout in config (map window, feature vector length).
- Implement `_build_compact` to reuse hybrid map extraction with reduced channels and normalise feature scaling.
- Add regression tests in `tests/test_observation_builder_compact.py` and update docs describing variant trade-offs.

### Affected Components
- src/townlet/observations/builder.py
- tests/test_observation_builder_compact.py
- docs/guides/observations.md

### Dependencies
- None

### Acceptance Criteria
- [ ] Compact variant produces non-zero tensors matching schema.
- [ ] Hybrid/full regression tests unaffected.
- [ ] Documentation lists compact feature dimensions and activation flag.

### Related Issues
- Risk Register: R-105

## WP-108: Adopt Structured Logging for Stability & Telemetry

**Category**: Operational
**Priority**: MEDIUM
**Effort**: S (2-8hrs)
**Risk Level**: Medium

### Description
Logging relies on free-form strings, making it difficult to ingest metrics or correlate events across subsystems.

### Current State
TelemetryPublisher logs string messages (`logger.info`, `logger.warning`) without structured context (src/townlet/telemetry/publisher.py:243-265, 448-519). Stability monitor emits minimal logging.

### Desired State
Structured logs (JSON or key/value) for tick health, transport status, and promotion updates, with integration guidance for log aggregation.

### Impact if Not Addressed
Operators cannot create alerts or dashboards from unstructured logs; incident triage remains manual.

### Proposed Solution
- Introduce logging helpers that emit key/value pairs (tick, duration, queue depth, drop count).
- Update promotion/stability logging to share structure across INFO/WARN levels.
- Adjust tests to assert structured output where applicable.
- Extend docs with guidance on parsing structured logs.

### Affected Components
- src/townlet/telemetry/publisher.py
- src/townlet/stability/monitor.py
- docs/ops/observability.md

### Dependencies
- WP-103

### Acceptance Criteria
- [ ] Tick health logs emit structured payloads referencing queue depth/drop counts.
- [ ] Stability monitor logs include promotion_state fields.
- [ ] Tests verify structured logging helper output.
- [ ] Operations documentation updated with log parsing examples.

### Related Issues
- Risk Register: R-103
