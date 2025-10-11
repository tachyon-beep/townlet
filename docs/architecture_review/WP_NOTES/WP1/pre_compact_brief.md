# WP1 Pre-Compact Brief — 2025-10-10

## Current Focus
- WP1 remediation underway; WC-E observation pipeline complete (WorldContext.observe + loop integration).
- T1.1 (modular world builder) executed: `create_world` returns context-backed adapters by default, `DefaultWorldAdapter` handles modular and legacy runtimes, and factory tests cover the path.

## Outstanding Work
- T1.2/T2.x: remove `LegacyWorldRuntime` usage entirely (DefaultWorldAdapter cleanup, drop `.world_state`, rely on context-only APIs).
- T5.x: add dummy world/policy/telemetry providers + smoke tests.
- Simulation loop cleanup: remove `runtime.queue_console`, rely solely on ports; add missing loop/console smokes.
- Documentation updates (ADR-001, console/monitor ADR, statuses) after factory/adapter cleanup.

## Dependences / Notes
- Legacy path still available in `DefaultWorldAdapter` for callers passing `runtime`; plan removal once consumers migrate.
- Loop currently seeds observation service on context; once factory wires service directly, remove loop bootstrap.
- Telemetry/policy DTO work (WP3) remains active; ensure schema stays aligned while refactoring adapters.

## Helpful Paths
- Factory tests: `tests/factories/test_world_factory.py`
- World context tests: `tests/test_world_context.py`, `tests/world/test_world_context_observe.py`
- Simulation loop parity: `tests/core/test_sim_loop_dto_parity.py`

Use this as reorientation after compaction.
