# WP1 – T1.4 Factory DTO Assertions (Plan)

Goal: extend world factory coverage so `create_world` is locked to the modular
runtime pipeline—specifically that the adapter exposes a DTO-capable context and
emits the expected tick events.

## Current Behaviour Snapshot
- `tests/factories/test_world_factory.py` ensures `create_world` returns a
  `DefaultWorldAdapter` and that calling `tick` produces a `RuntimeStepResult`.
- `tests/world/test_world_factory.py` bootstraps the default provider with a
  config and checks that a tick/snapshot complete successfully.
- No test currently asserts:
  * the created adapter’s context can produce an `ObservationEnvelope`.
  * DTO schema/version is present in the observation payload.
  * tick events (`RuntimeStepResult.events`) are present and typed as mappings.

## Risks
- Downstream refactors could inadvertently detach the observation service or
  return a legacy runtime without test failures.
- DTO schema churn could go unnoticed without a guard on the observation payload.

## Execution Plan

### Step 1 – Context DTO Assertion
1. In `tests/world/test_world_factory.py`, after running a tick, obtain
   `adapter.context`.
2. Assert `context.observation_service` is configured and calling
   `context.observe(...)` returns an `ObservationEnvelope` with
   `dto_schema_version`.

### Step 2 – Event Emission Guard
1. Extend `tests/factories/test_world_factory.py` to verify that
   `RuntimeStepResult.events` is a list of mappings (even if empty) after a tick.

### Step 3 – Update Documentation
1. Mark T1.4 as completed in the WP1 trackers once tests land.

### Step 4 – Validation
1. Run targeted regression:
   ```
   pytest tests/factories/test_world_factory.py \
          tests/world/test_world_factory.py -q
   ```
