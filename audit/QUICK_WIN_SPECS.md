# Quick Win Specifications

## QW-001: Sandbox Snapshot & Console File Operations (maps to WP-002)

**Objective**: Prevent console/telemetry users from accessing the filesystem outside approved snapshot roots.

**Scope**
- Harden `_parse_snapshot_path` plus all snapshot-related handlers in `src/townlet/console/handlers.py`.
- Restrict snapshot load/save/migrate operations in `src/townlet/snapshots/state.py` to validated directories.
- Ensure telemetry replay/import routines respect the same allowlist.

**Implementation Outline**
1. Derive a set of allowed paths:
   - Primary: `SimulationConfig.snapshot_root()`.
   - Optional overrides supplied in config (e.g., `snapshot.guardrails.allowed_paths`).
2. Replace raw `Path.resolve()` usage in `_parse_snapshot_path` with helper `resolve_snapshot_path` that:
   - Normalises and resolves `path`.
   - Checks `path.is_relative_to(allowed_root)` (Python 3.9+ fallback to manual comparison).
   - Rejects directories unless handler explicitly expects them.
3. Gate `snapshot_migrate` output directories the same way (must live under an allowed root).
4. Audit `SnapshotManager.save/load` to ensure they refuse escaped paths, adding guardrails if missing.
5. Update console router to return `{error: "forbidden"}` on violations.

**Testing Plan**
- Unit tests covering:
  - Allowed path passes (existing snapshot root).
  - Attempted traversal (`../etc/passwd`) returns forbidden.
  - Directory vs. file validation for `snapshot_inspect` and `snapshot_migrate`.
- Integration smoke: run console commands via `tests/test_console_commands.py` to confirm behaviour.

**Dependencies & Risks**
- Requires Python ≥3.10 for `Path.is_relative_to`; otherwise implement manual helper.
- Coordinate with documentation to communicate allowed root configuration.

**Estimated Effort**: XS (<2hrs)

---

## QW-002: Defensive Copying in World Snapshots (maps to WP-006)

**Objective**: Ensure telemetry/UI consumers cannot mutate live simulation state via `WorldState.snapshot()`.

**Scope**
- `WorldState.snapshot` (and any caller like `TelemetryPublisher.export_state`) in `src/townlet/world/grid.py` / `src/townlet/telemetry/publisher.py`.
- Associated helper routines that expose agent dictionaries, employment queues, or affordance manifests.

**Implementation Outline**
1. Replace `return dict(self.agents)` with deep copy semantics:
   - Use `copy.deepcopy` or dataclass `replace` to clone `AgentSnapshot` instances.
   - Provide immutable views (e.g., `MappingProxyType`) where practical.
2. Audit other exposure points: `WorldState.local_view`, `TelemetryPublisher.export_state`, queue manager dumps.
3. Consider adding `AgentSnapshot.copy()` helper to avoid repetitive clone logic.

**Testing Plan**
- New unit test: obtain snapshot, mutate returned agent needs, assert original world remains unchanged.
- Regression tests for telemetry export to confirm compatibility.
- Performance check with representative agent count to ensure copies stay lightweight (document any acceptable overhead).

**Dependencies & Risks**
- Must avoid circular references or large deep copies; use selective cloning.
- Coordinate with telemetry builders to accept immutable structures (update tests if they expect mutability).

**Estimated Effort**: S (single sprint day)

---

## QW-003: Health Monitoring & Structured Logging (maps to WP-007)

**Objective**: Improve observability across simulation subsystems with structured logs and health summaries.

**Scope**
- Subsystems: `SimulationLoop`, `TelemetryPublisher`, `PerturbationScheduler`, `LifecycleManager`, `PolicyRuntime` (core touchpoints).
- Logging configuration: ensure JSON or structured key/value logs optional via config flag.
- Console commands: add `health_status` or extend existing telemetry snapshot with aggregated health view.

**Implementation Outline**
1. Introduce lightweight health registry (e.g., `townlet.telemetry.health.HealthSnapshot`) capturing:
   - Tick latency / duration percentiles.
   - Telemetry queue depth, dropped payloads.
   - Perturbation backlog counts / retry metrics.
   - Policy possession count, lifecycle backlog.
2. Enhance logging to include structured fields (use `logging.LoggerAdapter` or `structlog` style key=value formatting). Optionally control via config flag `logging.structured = true`.
3. Emit periodic health summaries (every N ticks) and expose through `TelemetryPublisher.latest_stability_metrics()` or new console command (`health_status`).
4. Document log format and sample outputs under `docs/ops/`.

**Testing Plan**
- Unit tests verifying health summary contains expected keys when subsystems update metrics.
- Log capture tests ensuring structured entries produced when flag enabled (use `caplog`).
- Manual smoke: run `scripts/run_simulation.py` and confirm health panel appears in observer UI.

**Dependencies & Risks**
- Ensure logging changes remain backward compatible (no flooding existing log sinks).
- Avoid performance degradation—keep health calculation lightweight.
- Coordination with WP-004 metrics already in place to avoid duplication.

**Estimated Effort**: S (single sprint day)

