# Work Packages

**Summary Dashboard**
- Priority counts: CRITICAL 1, HIGH 3, MEDIUM 6
- Category coverage: Security 3, Operational 2, Performance 1, CodeQuality 1, BestPractice 1, Enhancement 1, TechnicalDebt 1
- Estimated effort by priority: CRITICAL ≈ L, HIGH ≈ XS+M+M, MEDIUM ≈ S+S+M+M+M+L

## Priority: CRITICAL

## WP-001: Harden Console & Telemetry Access Control

**Category**: Security
**Priority**: CRITICAL
**Effort**: L (3-10 days)
**Risk Level**: Critical

### Description
Console commands and telemetry snapshot endpoints run without any authentication or session management, allowing any connected client to invoke admin-only operations.

### Current State
`create_console_router` simply toggles handler registration on the `mode` flag without verifying caller identity (`src/townlet/console/handlers.py:832`). The UI (`townlet_ui`) assumes trusted access, so hostile actors can issue `kill`, `policy_swap`, or `snapshot_migrate` commands.

### Desired State
Require authenticated sessions and role-based authorization for console and telemetry interactions, enforcing viewer/admin separation and revocable tokens.

### Impact if Not Addressed
Unprivileged users can terminate agents, exfiltrate snapshots, or tamper with policy promotion, undermining simulation integrity and any downstream analytics.

### Proposed Solution
Implement an authentication layer (e.g. signed API tokens or mutual TLS) for console and telemetry RPCs, issue short-lived admin credentials, validate issuer metadata in `_attach_metadata`, and update `townlet_ui` to perform login/refresh flows.

### Affected Components
- `src/townlet/console/handlers.py`
- `src/townlet/telemetry/publisher.py`
- `src/townlet_ui/commands.py`
- `src/townlet_ui/dashboard.py`

### Dependencies
- Coordinates with WP-003 to secure the transport channel.

### Acceptance Criteria
- [ ] Console requests require authenticated credentials before executing handlers.
- [ ] Viewer/admin roles enforced server-side regardless of client UI state.
- [ ] Integration tests cover unauthenticated and expired-session failures.
- [ ] Documentation updated with credential provisioning and rotation procedures.

### Related Issues
- Risk Register: R-01

## Priority: HIGH

## WP-002: Sandbox Snapshot & Console File Operations

**Category**: Security
**Priority**: HIGH
**Effort**: XS (< 2hrs)
**Risk Level**: High

### Description
Console handlers resolve user-supplied paths with `Path.resolve()` and read arbitrary files, permitting data exfiltration outside designated snapshot roots.

### Current State
`_parse_snapshot_path` accepts any resolved filesystem path (`src/townlet/console/handlers.py:180`), so a viewer can read `/etc/passwd` or clobber directories via `snapshot_migrate` output.

### Desired State
Restrict console file operations to configured snapshot directories and refuse paths that escape the allowlisted roots.

### Impact if Not Addressed
Attackers can browse host files, leak credentials, or overwrite production artefacts even when restricted to viewer mode.

### Proposed Solution
Add root allowlist derived from `SimulationConfig.snapshot_root`, validate `path.is_relative_to(root)` before proceeding, and harden output directory handling. Provide configurable read-only mode for non-admin sessions.

### Affected Components
- `src/townlet/console/handlers.py`
- `src/townlet/snapshots/state.py`

### Dependencies
- Complements WP-001 but can ship independently.

### Acceptance Criteria
- [ ] Path validation rejects inputs outside configured snapshot directories.
- [ ] Unit tests cover traversal attempts and honest paths.
- [ ] Console returns explicit authorization error for forbidden paths.

### Related Issues
- Risk Register: R-02

## WP-003: Secure Telemetry Transport & Authentication

**Category**: Security
**Priority**: HIGH
**Effort**: M (1-3 days)
**Risk Level**: High

### Description
Telemetry TCP transport streams unauthenticated JSON over plaintext sockets (`src/townlet/telemetry/transport.py:56`), exposing sensitive state to interception or injection.

### Current State
`TcpTransport` uses `socket.create_connection` without TLS, certificates, or message signing. Clients are assumed to be trusted; there is no capability gating in payload consumers.

### Desired State
Provide encrypted telemetry channels (TLS or mutual TLS) with client authentication and configurable access control lists.

### Impact if Not Addressed
An adversary on the network can read world state snapshots, replay stale payloads, or spoof commands, potentially undermining experimental integrity.

### Proposed Solution
Integrate `ssl.SSLContext` wrapping for TCP sockets, support certificate configuration in `SimulationConfig.telemetry.transport`, and enforce message signing or bearer tokens before accepting telemetry/control messages.

### Affected Components
- `src/townlet/telemetry/transport.py`
- `src/townlet/telemetry/publisher.py`
- `src/townlet_ui/telemetry.py`

### Dependencies
- Should launch alongside WP-001 for end-to-end auth.

### Acceptance Criteria
- [ ] TLS-enabled transport available with configurable certificates.
- [ ] Plaintext TCP disabled or clearly marked for development only.
- [ ] Integration tests confirm handshake failure on bad certificates.
- [ ] Documentation lists operational steps for certificate rotation.

### Related Issues
- Risk Register: R-03

## WP-004: Decouple Telemetry Flush from Simulation Loop

**Category**: Operational
**Priority**: HIGH
**Effort**: M (1-3 days)
**Risk Level**: High

### Description
`TelemetryPublisher._flush_transport_buffer` performs blocking writes (and `time.sleep` retries) on the simulation thread (`src/townlet/telemetry/publisher.py:428`), risking tick stalls under network back-pressure.

### Current State
Payload flushes run synchronously with exponential backoff; persistent failures clear buffers and halt progress until retries complete.

### Desired State
Process telemetry flushes asynchronously with bounded queues so slow transports cannot pause the main tick loop.

### Impact if Not Addressed
Network hiccups or slow sinks will freeze the simulation, dropping telemetry or violating real-time guarantees.

### Proposed Solution
Introduce a background worker thread/process for IO, signal flush failures via metrics, and ensure the simulation thread only enqueues payloads with immediate drop/back-pressure logic.

### Affected Components
- `src/townlet/telemetry/publisher.py`
- `src/townlet/telemetry/transport.py`

### Dependencies
- Coordinates with WP-005 (payload size) for holistic resilience.

### Acceptance Criteria
- [ ] Simulation tick loop remains non-blocking during telemetry outages.
- [ ] Flush worker exposes health/metrics for monitoring.
- [ ] Tests simulate slow transports without tick starvation.

### Related Issues
- Risk Register: R-04

## Priority: MEDIUM

## WP-005: Slim Telemetry Payloads & Add Diff Support

**Category**: Performance
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
Every tick rebuilds full relationship snapshots, KPI histories, and policy state (`src/townlet/telemetry/publisher.py:469`), generating large JSON payloads and redundant copies.

### Current State
`_build_stream_payload` deep-copies nested dictionaries each step; high-frequency runs with >10 agents will strain CPU and transport bandwidth.

### Desired State
Emit incremental updates or configurable sampling, reducing payload size and serialization overhead while preserving fidelity.

### Impact if Not Addressed
Telemetry ingest becomes the primary bottleneck, reducing achievable tick rates and inflating storage costs.

### Proposed Solution
Introduce diff/patch payload mode, configurable sampling windows, and lazy serialization for unchanged sections. Cache relationship snapshots and supply delta arrays to the UI.

### Affected Components
- `src/townlet/telemetry/publisher.py`
- `src/townlet_ui/telemetry.py`

### Dependencies
- Works well after WP-004 to keep queues bounded.

### Acceptance Criteria
- [ ] Payload size reduced by >=30% on baseline config without losing required fields.
- [ ] UI correctly renders incremental updates.
- [ ] Performance benchmarks document CPU/time wins.

### Related Issues
- Risk Register: R-05

## WP-006: Defensive Copying in World Snapshots

**Category**: CodeQuality
**Priority**: MEDIUM
**Effort**: S (2-8hrs)
**Risk Level**: Medium

### Description
`WorldState.snapshot` returns a shallow copy referencing live `AgentSnapshot` instances (`src/townlet/world/grid.py:1379`), letting telemetry or observers mutate world state inadvertently.

### Current State
Downstream consumers can modify agent dictionaries, leading to nondeterministic behaviour and snapshot corruption.

### Desired State
Return immutable or deep-copied agent data to outside callers, enforcing write isolation.

### Impact if Not Addressed
Hard-to-reproduce bugs and data races between telemetry/UI and the simulation loop.

### Proposed Solution
Clone `AgentSnapshot` dataclasses (or expose frozen dataclasses), document immutability, and add regression tests ensuring external mutation cannot affect the live world.

### Affected Components
- `src/townlet/world/grid.py`
- `src/townlet/telemetry/publisher.py`

### Dependencies
- None; can ship independently.

### Acceptance Criteria
- [ ] World snapshot consumers receive immutable data structures.
- [ ] Tests verify mutation attempts leave world state intact.
- [ ] Performance impact evaluated (and acceptable) for baseline agent counts.

### Related Issues
- Risk Register: R-06

## WP-007: Add Health Monitoring & Structured Logging

**Category**: Operational
**Priority**: MEDIUM
**Effort**: S (2-8hrs)
**Risk Level**: Medium

### Description
Subsystems emit minimal logging and expose no health endpoints, obscuring failures in perturbations, stability monitors, or telemetry channels.

### Current State
Only ad-hoc warnings exist (e.g. transport retries); there is no heartbeat for lifecycle, scheduler, or policy loops.

### Desired State
Provide structured logging, periodic health summaries, and counters (drops, queue depth, perturbation backlog) for observability.

### Impact if Not Addressed
Operational incidents go undetected until downstream metrics degrade; debugging requires invasive instrumentation.

### Proposed Solution
Adopt structured logging (JSON or key=value), emit metric hooks (e.g., Prometheus exporter or statsd), and add a `/health` CLI/console view summarizing subsystem state.

### Affected Components
- `src/townlet/core/sim_loop.py`
- `src/townlet/telemetry/publisher.py`
- `src/townlet/scheduler/perturbations.py`

### Dependencies
- Complements WP-004/WP-005 to validate improvements.

### Acceptance Criteria
- [ ] Health summary available via console/UI.
- [ ] Key metrics (drops, retries, queue length) exported for monitoring.
- [ ] Structured logs validated in CI.

### Related Issues
- Risk Register: R-04, R-05

## WP-008: Provide Container & Deployment Blueprint

**Category**: BestPractice
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
No Dockerfile, compose stack, or deployment guide exists, complicating reproducible environments and infra hardening.

### Current State
README references manual virtualenv setup; CI builds wheels but there is no production deployment story.

### Desired State
Offer container images, compose templates (simulation + UI + telemetry sink), and guidance on volume mounts and secret injection.

### Impact if Not Addressed
Environment drift, inconsistent dependencies, and delay in staging/production rollouts.

### Proposed Solution
Create Dockerfile with multi-stage build, define docker-compose (simulation, UI, monitoring), document environment variables, and integrate with CI publishing.

### Affected Components
- Repository root (new Dockerfile/docker-compose)
- `.github/workflows/`
- `docs/ops/`

### Dependencies
- Align with WP-001/WP-003 for secure defaults inside containers.

### Acceptance Criteria
- [ ] Container image builds reproducibly with pinned dependencies.
- [ ] Compose/helm manifests codify volumes for configs, logs, snapshots.
- [ ] Deployment runbook added to `docs/ops/`.

### Related Issues
- Risk Register: R-07

## WP-009: Complete Training & Promotion Pipeline

**Category**: Enhancement
**Priority**: MEDIUM
**Effort**: L (3-10 days)
**Risk Level**: Medium

### Description
Policy training scripts rely on placeholders; PPO/BC workflows lack end-to-end orchestration and evaluation hooks.

### Current State
`PolicyRuntime` scaffolds anneal blend and replay buffers, but training scripts do not integrate with promotion guardrails or telemetry comparisons.

### Desired State
Deliver a production-ready training loop with dataset ingestion, evaluation suites, and promotion criteria enforcement.

### Impact if Not Addressed
Simulation improvements cannot be validated or promoted, limiting experimentation ROI.

### Proposed Solution
Implement full PPO trainer tying `RolloutBuffer`, `compute_gae`, and `PromotionManager`, add replay/BC evaluation, and wire telemetry exports for model comparisons.

### Affected Components
- `scripts/run_training.py`
- `scripts/promotion_evaluate.py`
- `src/townlet/policy/runner.py`
- `src/townlet/stability/promotion.py`

### Dependencies
- Relies on WP-007 for metrics to judge training health.

### Acceptance Criteria
- [ ] Training script produces evaluable checkpoints with promotion metadata.
- [ ] Automated tests cover promotion gating logic.
- [ ] Documentation updated with training pipeline walkthrough.

### Related Issues
- Risk Register: R-08

## WP-010: Pay Down Placeholder & TODO Backlog

**Category**: TechnicalDebt
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
Numerous modules retain scaffolding (TODO markers, placeholder docstrings), risking drift between design docs and implementation.

### Current State
Module docstrings often indicate "scaffolding" (e.g., `src/townlet/stability/monitor.py`, `src/townlet/policy/scripted.py`) and TODO markers remain untracked.

### Desired State
Convert placeholders into concrete implementations or tracked backlog items, ensuring documentation matches behaviours.

### Impact if Not Addressed
Developers rely on stale assumptions; regressions slip into production due to missing assertions/tests.

### Proposed Solution
Inventory TODO markers, create issues or implement missing functionality, expand docstrings/tests to match reality, and enforce linting for placeholder text.

### Affected Components
- `src/townlet/stability/monitor.py`
- `src/townlet/policy/scripted.py`
- `docs/` design references

### Dependencies
- None; coordinates with team leads for prioritisation.

### Acceptance Criteria
- [ ] All TODOs linked to tracked issues or resolved.
- [ ] Module docstrings accurately describe current behaviour.
- [ ] Additional regression tests added where placeholders were removed.

### Related Issues
- Risk Register: R-08
