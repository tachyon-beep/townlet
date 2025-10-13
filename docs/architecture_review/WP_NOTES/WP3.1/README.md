# WP3.1 — Stage 6 Recovery Plan

**Purpose:** Realign the codebase with the WP3 Stage 6 target state that was reported complete on 2025-10-11, but not reflected in the repository. WP3.1 captures the remediation required to remove the remaining legacy shims, enforce DTO-only policy/telemetry flows, and reconcile documentation with reality.

---

## Objectives
- Eliminate the console command queue shim so telemetry routing relies solely on dispatcher events.
- Retire transitional adapter/world accessors and expose DTO-centric interfaces only.
- Remove `ObservationBuilder` and all legacy observation batch dependencies from runtime, tooling, and tests.
- Update documentation, status trackers, and guard tests to represent the true Stage 6 state.
- Re-run the Stage 6 verification bundle (pytest, ruff, mypy, docstring checks) and record the results.

## Workstreams & Entry Points
| # | Workstream | Primary Doc | Status |
|---|------------|-------------|--------|
| 1 | Console Queue Retirement | `console_queue_retirement.md` | ✅ COMPLETE |
| 2 | Adapter Surface Cleanup | `adapter_surface_cleanup.md` | ✅ COMPLETE |
| 3 | ObservationBuilder Retirement | `observationbuilder_retirement.md` | ⏳ PENDING |
| 4 | Documentation & Verification Alignment | `documentation_alignment.md` | 🔄 IN PROGRESS |

Each workstream document contains numbered implementation steps with explicit
file targets, commands, and acceptance criteria.

## Execution Order & Gates
1. **Workstream 1** — eliminate `queue_console_command` everywhere and ensure
   console suites pass before proceeding.
2. **Workstream 2** — remove adapter/world escape hatches; block advancement
   until adapter + orchestration suites pass with the DTO-first surface.
3. **Workstream 3** — delete `ObservationBuilder` only after Workstreams 1 and 2
   are merged. Gate on `rg "ObservationBuilder"` returning only the guard test
   plus green DTO parity.
4. **Workstream 4** — refresh docs/status and execute the verification sweep
   once code changes are complete.

## Tracking & Reporting
- Record execution notes and command outputs in `docs/architecture_review/WP_NOTES/WP3.1/stage6_recovery_log.md` (created during implementation).
- Update `docs/architecture_review/WP_NOTES/WP3/status.md` only after all recovery tasks are complete and validated.

---

## Progress Summary

**Last Updated**: 2025-10-13 06:45 UTC

### Completed ✅

**WS1: Console Queue Retirement** (2025-10-13 02:50 → 04:30 UTC)
- Removed `queue_console_command` / `export_console_buffer` from protocol
- Migrated to event-based console caching via dispatcher
- Updated 6 test files to use new pattern
- **Result**: 63/63 console tests passing, 0 references in src/

**WS2: Adapter Surface Cleanup** (2025-10-13 05:30 → 06:30 UTC)
- Added `components()` method to DefaultWorldAdapter
- Migrated SimulationLoop to use component accessor
- Updated 3 test files (9 locations)
- Removed 4 escape hatch properties (27 lines)
- **Result**: 15/15 adapter tests passing, 0 escape hatch references in src/

### In Progress 🔄

**WS4: Documentation & Verification Alignment**
- Updating WP3.1 documentation to reflect WS1/WS2 completion
- Recovery log updated with detailed execution notes
- Remaining: Update WP3 status.md, verification sweep

### Pending ⏳

**WS3: ObservationBuilder Retirement**
- 40 references across 14+ files
- High complexity migration
- Blocked pending WS1/WS2 completion (now unblocked)

### Metrics

| Metric | Value |
|--------|-------|
| Workstreams Complete | 2/4 (50%) |
| Commits Made | 8 total (4 WS1 + 4 WS2) |
| Test Suites Validated | Console (63/63), Adapters (15/15) |
| Lines Removed | 61 (34 WS1 + 27 WS2) |
| Files Modified | 13 (src + tests) |

---

**Next Action**: Consider WS3 (ObservationBuilder Retirement) or pause for review assessment.
