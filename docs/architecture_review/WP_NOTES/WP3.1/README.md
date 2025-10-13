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
| # | Workstream | Primary Doc |
|---|------------|-------------|
| 1 | Console Queue Retirement | `console_queue_retirement.md` |
| 2 | Adapter Surface Cleanup | `adapter_surface_cleanup.md` |
| 3 | ObservationBuilder Retirement | `observationbuilder_retirement.md` |
| 4 | Documentation & Verification Alignment | `documentation_alignment.md` |

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

**Next Action:** finalise the detailed plans in the workstream documents and start implementation, beginning with the console queue retirement.
