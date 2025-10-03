## Executive Summary

Townlet’s codebase is well-structured into domain-focused modules with strong typing and configuration models, but several critical gaps block real-world execution. The flagship simulation CLI never advances the loop because `SimulationLoop.run()` is used as a generator without iteration. Telemetry streams are feature rich yet unencrypted, and affordance hooks can import arbitrary modules via environment variables without checks. These issues, combined with unbounded dependency ranges and performance hot spots in world/observation builders, shape the current risk profile.

Overall system health is **6/10**: architecture and typing are solid, but operational readiness and security hardening require immediate attention. The highest-impact remediations (see WP-001, WP-002, WP-003) are achievable within the next sprint and would unblock simulation workflows while reducing attack surface.

## Key Metrics

| Metric | Value |
| --- | --- |
| Python modules analysed | 174 |
| Source (`src/`) LOC | 18,523 |
| Tests (`tests/`) LOC | 10,003 |
| Scripts (`scripts/`) LOC | 4,409 |
| TODO markers | 2 outstanding (`world/affordances.py`, `observations/builder.py`) |
| Background threads | 1 (telemetry flush worker per `TelemetryPublisher`) |

## Findings by Category

- **Security**: Dynamic affordance hook imports execute arbitrary modules from `TOWNLET_AFFORDANCE_HOOK_MODULES` (WP-002). Telemetry’s TCP transport ships plaintext payloads without authentication (WP-003).
- **Operational**: `scripts/run_simulation.py` does not iterate the simulation generator, so no ticks ever run (WP-001). No automated regression tests cover CLI entry points (WP-004).
- **Performance**: `WorldState.local_view` and `_build_single` rebuild neighbour maps per agent, yielding O(n²) work each tick (WP-005). Telemetry payloads deep-copy large structures every tick (WP-008).
- **Code Quality**: Core orchestration methods lack docstrings and integration tests, increasing onboarding cost (WP-004). Duplicate log trimming logic in `apply_affordance_outcome` hints at copy/paste debt (WP-009).
- **Best Practice**: Dependencies specify only lower bounds; no lock file or reproducible environment guidance exists (WP-007).
- **Enhancement**: Telemetry pipeline already computes rich metrics; incremental payload emission and policy identity diffs would ease downstream processing (WP-008).
- **Technical Debt**: Compact observation variant remains unimplemented despite tests referencing it (WP-006). Affordance outcome metadata is truncated due to duplicated trimming logic (WP-009).

## Top 10 Priorities

1. **WP-001** — Fix `run_simulation.py` so ticks execute and add a smoke test (Critical, XS).
2. **WP-002** — Restrict or validate affordance hook module imports (High, S).
3. **WP-003** — Provide TLS/authenticated telemetry transport or disable insecure TCP by default (High, M).
4. **WP-004** — Add executable CLI regression tests and harden `SimulationLoop.run()` API contract (High, S).
5. **WP-005** — Optimise `WorldState.local_view`/observation builder to avoid redundant O(n²) scans (Medium, M).
6. **WP-006** — Implement compact observation variant end-to-end and cover with tests (Medium, M).
7. **WP-007** — Introduce dependency pinning/lock files and document supported Python/Torch combos (Medium, S).
8. **WP-008** — Add telemetry payload diffing or channel-based throttling to reduce bandwidth (Medium, M).
9. **WP-009** — Clean up `apply_affordance_outcome` duplication and persist affordance IDs alongside metadata (Low, XS).
10. **WP-010** — (Optional) Expand telemetry health metrics with worker liveness & retry counters for ops visibility (Low, S).

## System Health Score

- **Architecture**: 8/10 — clear layering, dataclass-driven state, strong config validation.
- **Security**: 4/10 — dynamic imports and plaintext telemetry are notable risks.
- **Operational readiness**: 5/10 — primary CLI broken; no regression tests for entry points.
- **Performance**: 6/10 — acceptable for small agent counts but quadratic hot paths will bite scale goals.
- **Quality & Testing**: 6/10 — abundant unit tests, yet integration gaps and missing docstrings remain.

Weighted average (architecture 30%, security 25%, operations 20%, performance 15%, quality 10%) yields **6/10**.

## Recommended Immediate Actions

1. Ship WP-001 in the next patch release so simulation smoke tests run end-to-end.
2. Begin WP-002 and WP-003 in parallel: locking hook imports and planning telemetry TLS both reduce exposure with modest effort.
3. Schedule WP-004 to add CLI integration tests; gate merges on those checks.
4. Plan WP-005/WP-006 for the upcoming sprint to stabilise observation outputs before scaling agent counts or integrating PPO.
5. Publish an interim runbook documenting current telemetry insecurity and environmental trust assumptions until mitigations land.
