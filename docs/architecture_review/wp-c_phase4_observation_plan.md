# WP-C Phase 4 — Observation & Telemetry Integration Plan

## Baseline Artifacts (Phase 0)
- `tmp/wp-c/phase4_baseline_shapes.json` — observation tensor summary built from the test fixture world (see `tests/test_observation_builder.py:1`).
- `tmp/wp-c/phase4_baseline_telemetry.jsonl` — 10-tick telemetry capture from `scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 10`.

## Consumer Inventory (`townlet.world.observation.*`)
| Module | Entry Points | Notes |
| --- | --- | --- |
| `src/townlet/world/grid.py` | `local_view`, `agent_context`, `build_local_cache`, `snapshot_precondition_context` | Legacy shims still re-export helpers; world tick loop calls these when prepping observations & snapshots. |
| `src/townlet/observations/builder.py` | `_build_local_cache`, `_encode_path_hint`, `_encode_common_features` | Core observation runtime relies on helper outputs and metadata. |
| `src/townlet/rewards/engine.py` | `observation_agent_context` import | Reward heuristics sample agent context scalars (needs, wallet). |
| `tests/test_world_local_view.py` | `local_view`, `agent_context` | Regression coverage for helper behaviour. |
| `tests/test_world_observation_helpers.py` | `build_local_cache`, `snapshot_precondition_context` | Ensures helper outputs remain JSON serialisable and spatial indexes stay correct. |
| `docs/design/OBSERVATION_TENSOR_SPEC.md:24-111` | References helper origins | Documentation depends on stable helper names for table citations. |
| `docs/engineering/WORLDSTATE_REFACTOR.md:40-68` | Migration guidance | Notes current coupling; must be updated when helpers relocate. |

Additional downstream consumers referenced during earlier audits (see `audit/WORK_PACKAGES.md:188`) should be revisited once adapter surfaces land.

## Dependency Mapping (Phase 1)

```
townlet.world.observation.* helpers
        │
        ├─▶ ObservationBuilder (src/townlet/observations/builder.py:1)
        │       │
        │       ├─▶ SimulationLoop.observations.build_batch() (src/townlet/core/sim_loop.py:327)
        │       │       ├─▶ PolicyBackend.flush_transitions() (src/townlet/core/sim_loop.py:352)
        │       │       └─▶ RewardEngine / StabilityMonitor inputs (src/townlet/core/sim_loop.py:339-368)
        │       └─▶ Observation tests & fixtures (tests/test_observation_builder*.py)
        │
        ├─▶ RewardEngine (src/townlet/rewards/engine.py:11)
        │       └─▶ Consumes agent_context for heuristics & telemetry overlays
        │
        └─▶ TelemetryPublisher (src/townlet/telemetry/publisher.py:953, 1741, 2257)
                └─▶ Emits queue/relationship overlays and embedding metrics into outgoing payloads
```

Key policy/telemetry entrypoints:
- `SimulationLoop.step()` drives observation generation and forwards outputs to the active `PolicyBackend` (`flush_transitions`) and telemetry sinks (`publish_tick`).
- `TelemetryPublisher.publish_tick()` queries queue, rivalry, relationship snapshots built atop observation helpers to populate UI dashboards.
- Snapshot tooling (`snapshots/state.py:1`) packages helper outputs for persistence; these feed replay/training harnesses.

## Invariant Checklist
1. **Scalar bundle ordering** — `docs/design/OBSERVATION_TENSOR_SPEC.md:12-44` enumerates the canonical feature order; refactor must preserve names and indices.
2. **Map layout** — hybrid/full variants require 11×11 window with channel order `[self, agents, objects, reservations]`, full adds `path_dx`, `path_dy` (spec §2–3, lines 47-72). Compact window obeys map_window + object channel rules (§4, lines 74-116).
3. **Social snippet contract** — must continue to populate slots/aggregates according to `audit/WP_OBSERVATION_VARIANTS_PHASE1.md:38-74` and spec §5 (lines 118-150).
4. **Snapshot serialisability** — `snapshot_precondition_context` must deliver JSON-safe structures for telemetry/snapshot persistence (`tests/test_world_observation_helpers.py:55`).
5. **Employment hooks** — `agent_context` calls `_employment_context_wages`/`_employment_context_punctuality` when available; adapters must preserve fallback behaviour (`src/townlet/world/observation.py:101-132`).
6. **Path hint search** — `find_nearest_object_of_type` drives directional hints; relocation must not introduce O(n²) regressions (currently linear over `world.objects`, `src/townlet/world/observation.py:147-173`).
7. **Local cache performance** — `build_local_cache` constructs tile lookups without mutating `WorldState`; future adapter should keep pure dict/set outputs to satisfy tests `tests/test_world_observation_helpers.py:26`.

## Open Questions for Phase Planning
- Does telemetry require raw `WorldState` access for queue metrics (see `src/townlet/telemetry/publisher.py:953-1100`), or will adapters suffice once observations move? Document answers before Phase 2.
- Confirm observation builder personality channel toggles remain compatible with future adapter (currently hidden attribute access inside builder initialiser).

## Mutation Guard Assessment (Phase 0)
- Proxy run using a read-only wrapper recorded attribute access during `ObservationBuilder.build_batch`:
  `{'snapshot', 'consume_ctx_reset_requests', 'embedding_allocator', 'agent_snapshots_view', 'agent_position', 'objects', 'objects_by_position_view', 'reservation_tiles', 'queue_manager', 'rivalry_top', 'relationships_snapshot', 'tick', '_employment_context_wages', '_employment_context_punctuality', 'active_reservations'}`.
  No attribute assignments occurred, indicating the helper code is read-only apart from invoking existing services.
- `embedding_allocator.allocate/release` mutates allocator state; adapter design must allow controlled mutation (likely via façade method) while keeping other structures read-only.
- Telemetry normalises helper outputs into fresh dicts (e.g., `_capture_relationship_snapshot` converts to new mapping), so sharing adapter views should remain safe without defensive copies beyond existing conversions.

## Data & RNG Requirements (Phase 1)
- ObservationBuilder touches the following `WorldState` accessors per proxy trace: `snapshot`, `consume_ctx_reset_requests`, `embedding_allocator.allocate/release`, `agent_snapshots_view`, `agent_position`, `objects`, `objects_by_position_view`, `reservation_tiles`, `queue_manager.queue_snapshot`, `queue_manager.metrics`, `active_reservations`, `rivalry_top`, `relationships_snapshot`, `_employment_context_wages`, `_employment_context_punctuality`, and `tick`.
- No direct RNG is consumed; temporal features derive from deterministic `sin/cos(world.tick / ticks_per_day)` and hashed action identifiers. Adapters must surface the tick counter and expose read-only mappings for agents/objects/queues while allowing controlled invocation of `embedding_allocator` lifecycle hooks.
- Observation metadata relies on configuration knobs stored on the builder instance (`SimulationConfig.observations_config.*`); protocol design should keep variant/config exposed for parity tests.

## Interface Draft Notes (Phase 1)
- Introduced `ObservationServiceProtocol` and `WorldRuntimeAdapterProtocol` in `src/townlet/world/observations/interfaces.py` alongside an `EmbeddingAllocatorProtocol` helper. Naming mirrors the existing agent/relationship service protocols (`src/townlet/world/agents/interfaces.py`) to keep consistency across `townlet.world.*` abstractions.
- Adapter contract currently exposes the exact accessors recorded during the proxy run (tick, snapshot views, queue manager, embedding allocator, relationship snapshots). This keeps the requirements explicit for Phase 2 extraction while we decide which methods remain optional.
- Pending decision: whether employment context helpers should remain optional (`getattr`-style) or become mandatory on the adapter. Flagged for revisit before implementation.

## Validation Prep Notes (Phase 1)
- Staged parity/adapter test outline in `tests/world/observations/README.md`; this will guide the new suites once extraction lands.
- Baseline fixtures referenced in the README map back to the Phase 0 artifacts so future diffs can compare against `tmp/wp-c/phase4_baseline_shapes.json` and `tmp/wp-c/phase4_baseline_telemetry.jsonl`.

## Phase 2 Snapshot (Module Extraction)
- Created dedicated modules under `src/townlet/world/observations/` (`cache.py`, `views.py`, `context.py`, `interfaces.py`) with docstrings referencing WP-C Phase 4.
- Updated runtime imports (`src/townlet/observations/builder.py`, `src/townlet/world/__init__.py`) to target the new modules. Legacy paths (`townlet.world.observation`, `townlet.world.observations`) now proxy with `DeprecationWarning` guidance.
- Observation helper tests have been repointed to the new modules, confirming parity without relying on the deprecated paths (`tests/test_world_observation_helpers.py`, `tests/test_world_local_view.py`).
- Legacy shims now lazily import helper modules to avoid cyclic imports introduced by the runtime adapter.

## Phase 3 Snapshot (Adapter Layer & Wiring)
- Added `WorldRuntimeAdapter` (`src/townlet/world/core/runtime_adapter.py`) exposing read-only access to agents, objects, queues, relationships, and embedding allocator through the existing `WorldContext` façade.
- `SimulationLoop` now maintains `world_adapter` alongside the mutable `world` instance; observation builder requests go through the adapter, and `WorldRuntime` tracks the adapter for downstream consumers.
- `ObservationBuilder` and observation helper modules accept either a `WorldState` or adapter, coercing via `ensure_world_adapter` to maintain backward compatibility while steering new callers toward the read-only surface.
- Introduced adapter-focused tests (`tests/test_world_runtime_adapter.py`) and expanded `tests/test_world_context.py` to assert immutability guarantees.
- Remaining mutable dependency: the queue manager is still returned directly; document consumers must treat it as read-mostly until a dedicated view is introduced.
