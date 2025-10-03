# Employment Loop Hardening Work Package

## Risk Register & Reduction Plan
| Risk ID | Description | Probability | Impact | Exposure | Early Indicators | Mitigation Steps | Contingency / Backstop | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Attendance semantics diverge from product expectations, causing rework. | Medium | High | High | Conflicting interpretations in design brief or roadmap deltas. | Draft detailed Attendance & Wage Design Brief; hold async review; log approvals in repo. | Escalate unresolved decisions to PM; freeze implementation until decision matrix signed. | Architecture lead | Mitigated (design brief approved 2025-09-25) |
| R2 | Tick-loop regressions from new wage/penalty flow. | Medium | High | High | Increased failed/late queue tests; sim smoke alerts; performance degradation. | Feature-flag new behavior; add unit/property tests; run 1k-tick smoke per change. | Roll back flag to disable feature; capture incident note; hotfix. | Core simulation owner | Mitigated (smoke results 2025-09-25) |
| R3 | Telemetry/console schema drift breaks downstream tooling. | Medium | Medium | Medium | Serialization test failures; ops complaints about payload mismatch. | Publish sample payloads + schema version bump; add serialization tests; document in OPS handbook before release. | Provide compatibility shim in console router; document change log. | Telemetry lead | Mitigated (schema v0.2.0, tests/docs 2025-09-25) |
| R4 | Exit-cap policy ambiguous leading to incorrect lifecycle behavior. | Medium | High | High | Disagreement on global vs per-agent caps during review; inconsistent cap results in smoke runs. | Produce exit-cap decision matrix; enable debug logging; validate with sandbox runs before enforcement. | Keep cap flag off in release configs; revert to existing starvation-only exits. | Lifecycle owner | Mitigated (hybrid cap design approved 2025-09-25) |
| R5 | Console tooling (diagnostics/overrides) slips, leaving ops blind. | Low | Medium | Low | Command prototypes lag behind code; OPS handbook lacks updated procedures. | Prioritize console command implementation concurrently with core code; pair console unit tests with features. | Provide temporary CLI script reading telemetry snapshots; schedule follow-up sprint. | DevEx lead | Mitigated (dry run 2025-09-25) |
| R6 | Documentation/tests fall behind, undermining knowledge transfer. | Medium | Medium | Medium | PRs missing doc updates; failing coverage gates; reviewer comments. | Enforce doc updates per PR; extend pytest coverage (attendance, caps, console). | Block merges lacking docs/tests; allocate doc-debt cleanup cycle. | Doc steward | Mitigated (checklist in place 2025-09-25) |
| R7 | Performance degradation from added accounting/telemetry. | Low | Medium | Low | Profiling shows >5% tick time increase; telemetry backlog growth. | Benchmark before/after (tick timer, telemetry queue); optimize hotspots; lazy-load payload additions. | Scale back telemetry detail behind config flag until optimized. | Performance owner | Mitigated (tick benchmark 2025-09-25) |

### Risk Retirement Criteria
- R1 retired when design brief + decision matrix signed and stored in repo.
- R2 retired after new tests are green, feature flag default-on, and 1k-tick smoke passes twice consecutively.
- R3 retired when serialization tests and schema docs merged, and console payload consumers validated.
- R4 retired post sandbox validation with caps enabled and telemetry confirming expected exits.
- R5 retired once console commands ship with handbook updates and operator dry-run sign-off.
- R6 retired when docs/tests merged and CI gates enforce coverage + doc checklist.
- R7 retired after profiling report shows <5% tick overhead and telemetry backlog unchanged.

## Risk Reduction Activities (Execution Roadmap)
1. **Design Brief & Decision Matrix (addresses R1, R4)**
   - Author attendance/wage brief and exit-cap matrix in `/docs/design/`.
   - Route for approvals (architecture, PM, ops) with explicit sign-off checklist.
   - Archive approvals in repo (`docs/IMPLEMENTATION_NOTES.md`).
2. **Controlled Rollout & Testing (addresses R2, R7)**
   - Introduce `behavior.enforce_job_loop` flag default-off.
   - Implement unit/property tests for attendance, wage gating, exit caps.
   - Schedule automated 1k-tick smoke; track metrics in CI artifact.
3. **Telemetry & Console Schema Hardening (addresses R3, R5)**
   - Draft schema vNext document with sample payloads, update `TelemetryBridge` version field.
   - Add serialization tests in `tests/test_console_commands.py` + new telemetry snapshot tests.
   - Implement console diagnostics (`employment_status`, `debug queues`, override commands) and capture handbook updates.
4. **Documentation & Knowledge Transfer (addresses R6)**
   - Update `docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md`, `docs/ops/OPS_HANDBOOK.md`, `docs/engineering/IMPLEMENTATION_NOTES.md` in sync with code.
   - Add runbook appendix describing employment KPIs and alert responses.
   - Ensure PR template includes “Employment docs/tests updated” checkbox.
5. **Performance Monitoring (addresses R7)**
   - Add quick benchmark harness or timed log for tick duration before/after change.
   - Capture telemetry backlog metrics; document results in risk log.

## Objective
Bring the employment system up to Milestone M2 expectations by enforcing punctuality, handling absences, triggering unemployment exits, and exposing operator-facing telemetry and console tools.

## Scope
- Simulation employment logic (`src/townlet/world/grid.py`)
- Lifecycle enforcement (`src/townlet/lifecycle/manager.py`)
- Stability monitoring and telemetry snapshots (`src/townlet/stability/monitor.py`, `src/townlet/telemetry/publisher.py`)
- Console command surfaces and documentation updates
- Pytest coverage and runbooks touching the job loop

## Deliverables
- Attendance state machine with wage gating, penalties, and ratios
- Lifecycle exit caps and unemployment enforcement parameters
- Telemetry payloads + stability alerts for labour KPIs
- Console commands for employment diagnostics and overrides
- Updated architecture/ops docs and automated tests

## Tasks & Subtasks
1. **Current-State Analysis**
   - Review existing employment logic and tests; log behavioural gaps versus roadmap/ops expectations.
   - Catalogue current configuration knobs and identify required additions.
2. **Attendance & Wage Specification**
   - Define shift states (on-time, late, absent) including grace window, reset cadence, and wage/penalty rules.
   - Document planned telemetry/schema changes for job snapshots and stability metrics.
3. **Lifecycle & Exit Cap Design**
   - Determine exit-cap strategy (global/per-agent) and unemployment triggers; extend `SimulationConfig` schema accordingly.
   - Outline operator override policy and console/admin requirements.
4. **Implementation**
   - Update `WorldState` to compute attendance states, apply wages/penalties, and accumulate ratios.
   - Enhance `LifecycleManager` to enforce exit caps/unemployment exits and emit appropriate events.
   - Surface new telemetry/stability metrics mirroring design specs.
5. **Console & Ops Surfaces**
   - Implement diagnostic/override commands (e.g., `employment_status`, `debug queues`) with proper auth routing.
   - Extend telemetry bridges and update `docs/ops/OPS_HANDBOOK.md` playbooks.
6. **Validation & Documentation**
   - Add pytest coverage for attendance transitions, exit-cap enforcement, and console handlers.
   - Refresh `docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md`, `docs/engineering/IMPLEMENTATION_NOTES.md`, and related guides; capture sample telemetry output post-regression (`pytest`, lint, smoke sim).

## Timeline & Dependencies
- Tasks 1–3 must complete before implementation begins.
- Risk reduction activities 1–5 execute alongside relevant tasks; flags/tests must be in place before enabling new behavior by default.

## Success Criteria
- Simulation enforces attendance penalties and exit caps without regressing existing tests.
- Telemetry/console surfaces expose new employment KPIs and pass serialization tests.
- Ops documentation reflects the updated workflows and tooling.
- Extended smoke run completes without stability alerts exceeding new thresholds.

## Telemetry Consumer Adoption Plan
1. **Console CLI (Typer) & REST Gateway**
   - Add schema/version compatibility checks (warn on newer shards; block on major mismatches).
   - Update CLI help and API reference for employment fields and version semantics.
   - Add Typer integration test once CLI harness lands, asserting employment output and version warning copy.
2. **Observer UI / Renderer Prototype**
   - Teach payload parser to honour `schema_version`; render employment KPIs (per-agent pill + global widget).
   - Add UI snapshot tests using captured payloads (`employment_smoke_metrics.json`, telemetry snapshot sample).
   - Implement visual alerts for backlog/overflow tied to console remediation commands.
3. **Automation & Monitoring Scripts**
   - Ship `scripts/telemetry_check.py` (schema validator) and integrate into CI.
   - Update analytics notebooks (future) to pin schema expectations.
   - Extend smoke harness to optionally emit NDJSON for downstream replay.
4. **Documentation & Change Management**
   - Maintain schema change log + compatibility matrix (client vs schema).
   - Cross-link OPS handbook with consumer update checklist.

_Owners_: DevEx (CLI), UX/Renderer (UI), Data/Analytics (scripts). Target completion prior to enabling `employment.enforce_job_loop` in default configs.
