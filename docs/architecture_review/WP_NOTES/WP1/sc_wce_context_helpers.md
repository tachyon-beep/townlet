# WC-E Prep4 – Context Snapshot Helper Plan

New helper methods on `WorldContext` provide the non-observation data needed for DTO envelopes:
- `export_queue_metrics` / `export_queue_affinity_metrics`
- `export_queue_state`
- `export_running_affordances`
- `export_relationship_snapshot` / `export_relationship_metrics`
- `export_employment_snapshot`
- `export_economy_snapshot`
- `export_perturbation_state`

These surface existing service data straight from `WorldContext` so `WorldContext.observe` (WC-E) can mirror the simulation loop’s data collection without direct dependency on the loop. Current implementation returns empty dict on error to keep compatibility with legacy fallback behaviour.
