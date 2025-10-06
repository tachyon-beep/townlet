
## Lifecycle extraction prep (Phase 5 Step 0)

- `tmp/wp-c/phase5_lifecycle_telemetry.jsonl` captured via `python scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 25 --telemetry-path ...`
- Helpers to migrate: `_generate_agent_id`, `_is_position_walkable`, `_sync_agent_spawn`, `_assign_job_if_missing`, `_sync_reservation_for_agent`, `spawn_agent`, `teleport_agent`, `remove_agent`, `kill_agent`, `respawn_agent`, `_release_queue_membership`
- Callers touching spawn/respawn: console handlers (`world/console/handlers.py`), lifecycle manager (`lifecycle/manager.py`), demo runner/storylines, tests (`tests/test_lifecycle_manager.py`, `tests/test_queue_resume.py`), runtime tick loop (via nightly reset, employment hooks)
- Shared state dependencies: agents registry, spatial index (`_spatial_index`), queue manager (`QueueManager`), employment service (job assignment), reservation maps (`_active_reservations`, `_objects_by_position`), embedding allocator, event emission
- Baseline telemetry metrics to diff post-refactor: queue history (cooldown/ghost/rotation events), employment exits, perturbation snapshots, stability window counters

## Lifecycle extraction completion (Phase 5 Step 4)

- Introduced `townlet.world.agents.lifecycle.LifecycleService` orchestrating spawn/teleport/remove/kill/respawn, basket updates, employment resets, embedding allocation, and queue release.
- `WorldState` and `WorldContext` now expose `lifecycle_service`; console handlers, lifecycle manager tests, and telemetry suites rely on the façade instead of private helpers.
- `world/grid.py` reduced to 1 647 LOC (down ~330 from the Phase 4 checkpoint); remaining large block: spawn/despawn blueprint handling to be further trimmed after console integration.
- Residual follow-ups: convert remaining call sites to service (`generate_agent_id` usage in demos), fill docstrings around employment queue APIs, address `mypy` errors (employment runtime, queue manager), expand queue conflict tests for lifecycle removal edge cases.
