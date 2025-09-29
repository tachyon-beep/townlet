# Affordance Effects Reference

## Supported Effect Keys
- **Needs (`hunger`, `hygiene`, `energy`)**: Values are treated as deltas to the agent's need
  saturation. Effects are clamped to keep each need within `[0.0, 1.0]`.
- **money**: Applied as a straight delta to the agent wallet after the affordance completes.

New agents or respawns backfill missing needs to `0.5` so manifest effects always have an impact.
Affordance failures (explicit `release` with `success: false` or precondition aborts) skip effect
application.


## Testing Hooks
- `tests/test_need_decay.py` exercises need decay constants and lifecycle termination thresholds.
- `tests/test_world_queue_integration.py` covers `eat_meal`/`use_shower` success paths and verifies
  failed releases do not mutate needs.

These tests should be extended whenever new effect types or affordances are introduced.
