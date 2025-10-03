# Work Packages

## Summary Statistics
- Priorities: CRITICAL (1), HIGH (3), MEDIUM (4), LOW (2)
- Category coverage: Security (2), Operational (1), Performance (1), Quality (1), BestPractice (1), Enhancement (2), TechnicalDebt (2)
- Effort by priority:
  - CRITICAL: 1 × XS (<2h)
  - HIGH: 2 × S (2–8h), 1 × M (1–3d)
  - MEDIUM: 1 × S, 3 × M
  - LOW: 1 × XS, 1 × S

## Priority: CRITICAL

## WP-001: Restore Simulation CLI Tick Execution

**Category**: Operational
**Priority**: CRITICAL
**Effort**: XS (< 2hrs)
**Risk Level**: High

### Description
`scripts/run_simulation.py` instantiates `SimulationLoop` and calls `loop.run(max_ticks=...)` without iterating the generator, so no ticks execute. The flagship CLI therefore produces no side effects, misleading operators and blocking smoke tests.

### Current State
- `SimulationLoop.run()` yields `TickArtifacts` lazily.
- CLI drops the iterable, exiting immediately without a single tick.
- No regression test guards this behaviour, so the defect persisted unnoticed.

### Desired State
- CLI iterates the generator (e.g., `for _ in loop.run(...): pass`).
- Add a smoke test that executes a small number of ticks and asserts tick counter/telemetry side effects.
- Optionally adjust `SimulationLoop.run()` to execute immediately when `max_ticks` is provided to prevent future misuse.

### Impact if Not Addressed
- Simulation CLI remains non-functional, blocking QA demos and automated rehearsals.
- Downstream tooling (telemetry capture, replay buffers) cannot be validated end-to-end.

### Proposed Solution
1. Update `scripts/run_simulation.py` to iterate over `loop.run()`.
2. Consider adding a convenience method (`loop.run_for(max_ticks)`) to make intent explicit.
3. Add a pytest CLI smoke test invoking the script via `subprocess` or direct call, asserting world tick increments.
4. Document expected usage in README/docs.

### Affected Components
- scripts/run_simulation.py
- tests (new CLI smoke test)
- src/townlet/core/sim_loop.py (optional API ergonomics)

### Dependencies
- None.

### Acceptance Criteria
- [ ] CLI executes requested tick count and logs telemetry.
- [ ] New smoke test fails on the pre-fix behaviour and passes after the fix.
- [ ] README or docs updated with corrected invocation guidance.

### Related Issues
- AUDIT_SUMMARY.md (Top priority #1)

## Priority: HIGH

## WP-002: Harden Affordance Hook Module Imports

**Category**: Security
**Priority**: HIGH
**Effort**: S (2-8hrs)
**Risk Level**: High

### Description
`WorldState` reads `TOWNLET_AFFORDANCE_HOOK_MODULES` and blindly imports each module, enabling arbitrary code execution if the environment variable is manipulated.

### Current State
- `world/grid.py` builds the module list, `world/hooks.load_modules` imports without validation.
- No allowlist, signature checks, or sandboxing.

### Desired State
- Restrict hook imports to configured allowlists or packaged entry points.
- Reject or warn on modules outside trusted namespaces.
- Document secure deployment expectations.

### Impact if Not Addressed
- Anyone with environment access can execute arbitrary Python within the simulation process.
- Violates least-privilege expectations in shared or automated environments.

### Proposed Solution
1. Add configuration allowlist (e.g., `config.affordances.allowed_hook_modules`).
2. Validate environment-provided modules against allowlist and log rejections.
3. Consider replacing env control with config-level specification.
4. Add tests covering valid/invalid module imports.
5. Update security docs with guidance.

### Affected Components
- src/townlet/world/grid.py
- src/townlet/world/hooks/__init__.py
- configs (new allowlist field)
- docs/security guidance

### Dependencies
- None.

### Acceptance Criteria
- [ ] Hook imports limited to explicit allowlist.
- [ ] Invalid modules raise descriptive errors and refuse execution.
- [ ] Tests cover trusted/untrusted module scenarios.
- [ ] Security documentation updated.

### Related Issues
- AUDIT_SUMMARY (Security finding #1)

---

## WP-003: Secure Telemetry Transport Path

**Category**: Security
**Priority**: HIGH
**Effort**: M (1-3 days)
**Risk Level**: High

### Description
`TelemetryPublisher` supports a TCP transport that sends JSON payloads in plaintext with no authentication, exposing sensitive simulation metrics and console results on the network.

### Current State
- `TcpTransport` uses `socket.create_connection` without TLS.
- Transport configuration lacks authentication or shared secrets.
- No warnings surface when TCP is selected.

### Desired State
- Provide TLS (via `ssl.wrap_socket` or a pluggable secure client) and/or token-based signing.
- Default to secure transports; clearly warn (or disallow) plaintext in production.

### Impact if Not Addressed
- Telemetry can be intercepted or modified in transit.
- Console command audit trails and promotion state may leak.

### Proposed Solution
1. Add TLS configuration (cert paths, verification flags) to telemetry transport config.
2. Wrap sockets using Python’s `ssl` module; fall back to plaintext only when explicitly allowed.
3. Optionally add HMAC signing of payloads.
4. Document deployment steps and update tests/mocks for new parameters.

### Affected Components
- src/townlet/telemetry/transport.py
- src/townlet/telemetry/publisher.py (config validation)
- configs/examples (new TLS fields)
- docs/ops or security guidance

### Dependencies
- WP-002 (shared security review cadence).

### Acceptance Criteria
- [ ] TLS-enabled TCP transport with certificate validation is available.
- [ ] Plaintext mode emits explicit warnings and is disabled by default in production configs.
- [ ] Unit tests cover secure and insecure modes.
- [ ] Documentation updated with deployment guidance.

### Related Issues
- AUDIT_SUMMARY (Security finding #2)

---

## WP-004: Add CLI Regression Tests & Strengthen SimulationLoop Contract

**Category**: Quality
**Priority**: HIGH
**Effort**: S (2-8hrs)
**Risk Level**: Medium

### Description
Lack of integration tests allowed the simulation CLI regression to ship. `SimulationLoop.run` returning a generator is easily misused.

### Current State
- No automated tests execute CLI scripts.
- `SimulationLoop.run` does not guard against non-iteration usage.

### Desired State
- Regression tests cover `run_simulation.py` and `run_training.py` happy paths.
- Simulation loop exposes a convenience API that cannot be misused silently.

### Impact if Not Addressed
- Future regressions will slip through review.
- Developers remain unaware of API pitfalls.

### Proposed Solution
1. Create pytest integration tests invoking CLI entry points (via subprocess or direct call) with temporary configs.
2. Add helper method `SimulationLoop.run_for(max_ticks)` that executes internally, deprecating the generator usage in CLI contexts.
3. Update documentation and test harnesses accordingly.

### Affected Components
- tests/test_sim_loop_structure.py (extend) or new integration test module
- scripts/run_simulation.py
- scripts/run_training.py (smoke path)
- src/townlet/core/sim_loop.py (API ergonomics)

### Dependencies
- WP-001 (ensures CLI works after fix).

### Acceptance Criteria
- [ ] Tests fail on current regression and pass post-fix.
- [ ] CLI helper method documented for developers.
- [ ] CI includes new regression tests.

### Related Issues
- AUDIT_SUMMARY (Operational/Quality findings)

## Priority: MEDIUM

## WP-005: Optimise World Local View & Observation Builder Hot Paths

**Category**: Performance
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
`WorldState.local_view` and `ObservationBuilder._build_single` rebuild neighbourhood maps for every agent each tick, leading to O(n²) behaviour as agent count grows beyond the design target.

### Current State
- For each agent, loops over all agents/objects to rebuild lookup tables.
- Tests currently focus on small populations (≤10 agents), hiding scaling issues.

### Desired State
- Precompute spatial indices once per tick and reuse across agents.
- Profile and document resulting performance budgets.

### Impact if Not Addressed
- Performance degrades rapidly with additional agents or scripted NPCs.
- PPO training and anneal rehearsals stall when scaling scenarios.

### Proposed Solution
1. Introduce shared spatial cache computed once per tick (e.g., grid occupancy map).
2. Inject cache into observation builder/local view functions.
3. Add benchmarks or profiling assertions for target agent counts.
4. Update tests to cover larger agent populations.

### Affected Components
- src/townlet/world/grid.py (local_view, snapshot usage)
- src/townlet/observations/builder.py
- tests/test_observation_builder*.py

### Dependencies
- None.

### Acceptance Criteria
- [ ] Local view/observation builder reuse cached spatial data.
- [ ] Profiling demonstrates sub-quadratic behaviour for 32 agents.
- [ ] Tests updated to cover higher agent counts.

### Related Issues
- AUDIT_SUMMARY (Performance finding)

---

## WP-006: Complete Compact Observation Variant

**Category**: TechnicalDebt
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
`ObservationBuilder` contains a TODO for the compact variant and tests reference it, but no implementation exists.

### Current State
- Hybrid/full variants implemented; compact path unimplemented (`# TODO(@townlet)`).
- Config allows selecting `compact`, risking runtime errors or inconsistent tensors.

### Desired State
- Compact variant produces deterministic tensors with documentation and tests.

### Impact if Not Addressed
- Users selecting compact observations hit placeholder behaviour.
- PPO/training code cannot rely on variant parity.

### Proposed Solution
1. Define compact feature map (subset of hybrid features) and implement builder path.
2. Add fixtures/tests verifying shapes/values for compact variant.
3. Update docs/config comments explaining variant differences.

### Affected Components
- src/townlet/observations/builder.py
- tests/test_observation_builder_compact.py (extend)
- docs/guides on observations

### Dependencies
- WP-005 (shared observation refactor) [optional sequencing].

### Acceptance Criteria
- [ ] Compact variant enabled via config without crashes.
- [ ] Test coverage validates tensor shapes/values across variants.
- [ ] Documentation updated to describe variant capabilities.

### Related Issues
- TODO marker in observations builder

---

## WP-007: Introduce Dependency Pinning & Environment Guidance

**Category**: BestPractice
**Priority**: MEDIUM
**Effort**: S (2-8hrs)
**Risk Level**: Medium

### Description
`pyproject.toml` specifies only lower bounds. Without pinning, new upstream releases (numpy, pydantic, pettingzoo) can break the project unpredictably.

### Current State
- No lock file; contributors may install divergent versions.
- Lack of documented Python/PyTorch compatibility matrix.

### Desired State
- Reproducible dependency sets via lock file or constraints.
- Documented tooling versions for CI/local parity.

### Impact if Not Addressed
- Builds become non-deterministic; subtle regressions surface unexpectedly.
- Difficult to troubleshoot dependency-induced failures.

### Proposed Solution
1. Generate `requirements.lock` or `uv.lock` capturing tested versions.
2. Update contribution docs to instruct installation via lock.
3. Configure CI to install from lock to verify reproducibility.

### Affected Components
- pyproject.toml (optional adjustments)
- New lock/constraints file
- docs/CONTRIBUTING.md
- CI workflows

### Dependencies
- None.

### Acceptance Criteria
- [ ] Lock/constraints file committed and referenced in docs.
- [ ] CI installs using locked versions.
- [ ] Contribution guide updated with upgrade cadence.

### Related Issues
- AUDIT_SUMMARY (Best practice finding)

---

## WP-008: Reduce Telemetry Payload Volume via Diffing/Channels

**Category**: Enhancement
**Priority**: MEDIUM
**Effort**: M (1-3 days)
**Risk Level**: Medium

### Description
Telemetry currently serialises full world snapshots every tick, even when most data is unchanged. This strains transports and downstream analytics.

### Current State
- `_build_stream_payload` copies large dictionaries each tick.
- Buffer drops payloads when over capacity, but does not reduce churn.

### Desired State
- Emit incremental updates or split channels (e.g., high-frequency vs slow-changing metrics).

### Impact if Not Addressed
- High bandwidth usage and larger telemetry logs.
- Increased risk of buffer overflow/dropped messages under load.

### Proposed Solution
1. Identify frequently vs infrequently changing fields.
2. Implement diffing or channel-based emission (e.g., state vs events).
3. Provide config toggles and update downstream tooling to accept new schema.

### Affected Components
- src/townlet/telemetry/publisher.py
- Telemetry consumer tooling/scripts
- docs on telemetry schema

### Dependencies
- WP-003 (transport review).

### Acceptance Criteria
- [ ] Telemetry supports diff/channel mode with backward-compatible schema versioning.
- [ ] Buffer utilisation drops in profiling scenarios.
- [ ] Documentation updated for new schema.

### Related Issues
- AUDIT_SUMMARY (Performance/Enhancement finding)

## Priority: LOW

## WP-009: Clean Affordance Outcome Logging & Metadata Persistence

**Category**: TechnicalDebt
**Priority**: LOW
**Effort**: XS (< 2hrs)
**Risk Level**: Low

### Description
`apply_affordance_outcome` appends metadata to `_affordance_outcomes` but contains duplicate trimming logic and drops affordance/object identifiers that would aid debugging.

### Current State
- Duplicate `if len(outcome_log) > 10: del outcome_log[0]` lines.
- Metadata lacks affordance/object IDs due to TODO tracking.

### Desired State
- Single trimming block with configurable history length.
- Outcome metadata includes identifiers for telemetry/debugging.

### Impact if Not Addressed
- Minor maintenance burden and reduced observability when diagnosing affordance failures.

### Proposed Solution
1. Consolidate trimming logic.
2. Persist affordance/object IDs in metadata until schema evolves.
3. Add unit test covering `apply_affordance_outcome` history retention.

### Affected Components
- src/townlet/world/affordances.py
- tests/world affordance coverage (new)

### Dependencies
- None.

### Acceptance Criteria
- [ ] Outcome log retains bounded history without duplicate trimming.
- [ ] Metadata includes identifiers verified by tests.

### Related Issues
- AUDIT_SUMMARY (Technical debt observation)

---

## WP-010: Extend Telemetry Health Metrics with Worker Liveness

**Category**: Enhancement
**Priority**: LOW
**Effort**: S (2-8hrs)
**Risk Level**: Low

### Description
Telemetry health payload lacks explicit worker liveness, retry counters, or flush latency histograms, limiting operational insight.

### Current State
- Health metrics cover queue length, dropped messages, perturbation counts.
- No gauge for worker thread status or retry frequency.

### Desired State
- Surface worker alive flag, last flush success age, retry counters.
- Expose metrics to console/telemetry consumers for alerting.

### Impact if Not Addressed
- Harder to diagnose stalled transports or silent failures.

### Proposed Solution
1. Track flush worker heartbeat timestamps and retry counts in `_transport_status`.
2. Emit new fields in health payload and documentation.
3. Update tests to assert metrics presence.

### Affected Components
- src/townlet/telemetry/publisher.py
- Telemetry consumer scripts/tests

### Dependencies
- WP-003 (shared telemetry workstream).

### Acceptance Criteria
- [ ] Health payload contains worker liveness + retry counters.
- [ ] Documentation updated describing new metrics.
- [ ] Tests cover metric emission.

### Related Issues
- AUDIT_SUMMARY (Enhancement optional #10)
