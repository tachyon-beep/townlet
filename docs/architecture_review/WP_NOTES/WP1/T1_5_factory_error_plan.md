# WP1 – T1.5 Factory Error Regression (Plan)

Objective: Ensure `create_world` surfaces clear, deterministic errors when
callers provide invalid provider keys or omit required configuration.

## Current State
- `tests/factories/test_world_factory.py` already asserts that missing `config`
  (when `world` is absent) raises `TypeError`, and that unsupported kwargs
  trigger `TypeError`.
- No explicit coverage ensures:
  * invalid provider names raise the expected `ConfigurationError`.
  * invocation without `config` when no `world` is supplied still raises the
    correct exception after the T1.3 cleanup.

## Plan

### Step 1 – Test Additions
1. Extend `tests/factories/test_world_factory.py` with:
   - `test_create_world_requires_known_provider` using an obviously invalid
     provider key and asserting `ConfigurationError`.
   - Adjust existing “requires config” test, if necessary, to confirm it still
     raises `TypeError`.

### Step 2 – Validation
1. Run the existing factory regression:
   ```
   pytest tests/factories/test_world_factory.py -q
   ```

### Step 3 – Documentation
1. Mark T1.5 as complete in WP1 status/task docs once the tests land.
