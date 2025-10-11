# WP1 – T1.3 Legacy World Factory Kwargs Removal (Plan)

Objective: Delete the transitional keyword arguments that allowed callers to pass
legacy world services (`lifecycle`, `perturbations`, `observation_service`,
`runtime`) into `create_world`. The modular factory now owns this wiring, so the
kwargs are redundant and mask misconfigured callers.

## Current Behaviour Snapshot
- `townlet.factories.world_factory.create_world` accepts `**kwargs` and pops
  legacy keys (`runtime`, `lifecycle`, `perturbations`, `observation_service`,
  `rng_seed`, etc.) before delegating to the provider implementation.
- Tests rely on the kwargs for legacy fallback (`tests/factories/test_world_factory.py`)
  and for overriding services in composition-root tests (`SimulationLoop` override hooks).
- Some scripts/tests pass `runtime="legacy"` or explicit services as part of
  migration scaffolding.

## Risks / Mitigations
- **Risk:** Hidden caller still depends on the kwargs → Mitigate by running a
  repository-wide search for each key and updating those call sites to use the
  new override hooks (`SimulationLoop.override_world_components`, etc.).
- **Risk:** Tests expect kwargs behaviour → Update tests to assert that passing
  unsupported kwargs raises a `ConfigurationError`.
- **Risk:** Documentation assumes legacy kwargs → refresh WP1 docs/ADR references.

## Execution Plan

### Step 1 – Inventory & Call-Site Update
1. Search for `create_world(` usages with legacy kwargs (`runtime=`, `lifecycle=`,
   `perturbations=`, `observation_service=`).
2. Update any legitimate overrides to use the new mechanisms:
   - For tests: rely on factory defaults or use `SimulationLoop.override_world_components`.
   - For scripts: ensure they no longer attempt to supply these knobs.

### Step 2 – Factory Cleanup
1. Remove the kwargs handling from `townlet/factories/world_factory.py`
   (`_validate_kwargs`, `kwargs.pop` calls).
2. Raise `TypeError` if unsupported kwargs are provided.
3. Ensure provider creation pathways still receive `config`, `provider`, and any
   provider-specific options (no behavioural change there).

### Step 3 – Update Tests
1. Adjust `tests/factories/test_world_factory.py` to:
   - Assert that passing legacy kwargs raises `TypeError`.
   - Confirm the default provider path still returns a context-backed adapter.
2. Review `tests/core/test_sim_loop_modular_smoke.py` and other loop tests to
   ensure they no longer rely on direct kwargs (they should already use override hooks).

### Step 4 – Documentation & Status
1. Update WP1 trackers (`ground_truth_executable_tasks.md`, status/pre-brief) to
   mark T1.3 complete once merged.
2. Note the removal in ADR-001/WP1 README if they mention the transitional kwargs.

### Step 5 – Validation
1. Run targeted regression:
   ```
   pytest tests/factories/test_world_factory.py \
          tests/core/test_sim_loop_modular_smoke.py \
          tests/test_sim_loop_health.py -q
   ```
2. If no call sites break, proceed to the next task (likely T1.4 or T5.x).

---

## Execution Notes (2025-10-11)
- Legacy service kwargs have been removed from `_build_default_world`; the provider
  now instantiates `LifecycleManager`, `PerturbationScheduler`, and
  `ObservationBuilder` internally, seeding the scheduler from the context's
  `RngStreamManager`.
- `SimulationLoop` reads the lifecycle/scheduler back via adapter accessors and no
  longer creates those services directly.
- Regression bundle executed:
  ```
  pytest tests/factories/test_world_factory.py \
         tests/world/test_world_factory.py \
         tests/core/test_sim_loop_modular_smoke.py -q
  ```
