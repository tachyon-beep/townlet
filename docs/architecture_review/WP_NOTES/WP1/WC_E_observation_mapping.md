# WC-E – Observation Envelope Source Mapping (2025-10-10)

Baseline gathered from `src/townlet/core/sim_loop.py` + DTO factory. This table records where each `build_observation_envelope` field currently comes from and the expected modular replacement when `WorldContext.observe()` produces the envelope directly.

| Envelope Field | Current Source (SimulationLoop) | Target Source inside `WorldContext` |
| --- | --- | --- |
| `tick` | `SimulationLoop.tick` stamped prior to `build_observation_envelope` | `WorldContext.state.tick` |
| `observations` | `ObservationBuilder.build_batch(self.world_adapter, terminated)` | Observation service wired to `WorldContext` (builder/view over `WorldState` + DTO agent contexts) |
| `actions` | `runtime_result.actions` from world runtime tick | `WorldContext.tick` return payload |
| `terminated` | `runtime_result.terminated` (Lifecycle manager evaluation) | `WorldContext.tick` (already computing via lifecycle service) |
| `termination_reasons` | `runtime_result.termination_reasons` | `WorldContext.tick` |
| `queue_metrics` | `WorldContext.export_queue_metrics()` (invoked by SimulationLoop) | Direct call on `WorldContext.queue_manager.metrics()` |
| `rewards` | `RewardEngine.compute(world, terminated, termination_reasons)` | Remains loop concern (policy reward engine) – pass in when requesting envelope |
| `reward_breakdown` | `self.rewards.latest_reward_breakdown()` | Loop-supplied until rewards move into modular service |
| `perturbations` | `self.perturbations.latest_state()` | `WorldContext.perturbation_service.latest_state()` |
| `policy_snapshot` | `PolicyController.latest_policy_snapshot()` / `PolicyRuntime.latest_policy_snapshot()` | Loop/policy responsibility (context consumes as input) |
| `policy_metadata` | Constructed from policy identity + option switches/anneal ratio | Loop responsibility (no world dependency) |
| `rivalry_events` | `_collect_rivalry_events(adapter)` → `world_adapter.consume_rivalry_events()` | `WorldContext.relationships` / ledger provides events via dispatcher |
| `stability_metrics` | `self.stability.latest_metrics()` (loop-owned) | Loop responsibility |
| `promotion_state` | `self.promotion.snapshot()` | Loop responsibility |
| `rng_seed` | `getattr(self.world, "rng_seed", None)` | `WorldContext.state.rng_seed` |
| `queues` | `world.queue_manager.export_state()` | `WorldContext.queue_manager.export_state()` |
| `running_affordances` | `world_adapter.running_affordances_snapshot()` | `WorldContext.affordance_service.runtime_snapshot()` (or similar helper) |
| `relationship_snapshot` | `world_adapter.relationships_snapshot()` | `WorldContext.relationships.snapshot()` |
| `relationship_metrics` | `world_adapter.relationship_metrics_snapshot()` | `WorldContext.relationships.metrics_snapshot()` |
| `agent_snapshots` | `dict(world_adapter.agent_snapshots_view())` | `WorldContext.state.agent_snapshots_view()` |
| `job_snapshot` | `WorldContext.export_job_snapshot()` | Helper inside context using employment runtime/service |
| `queue_affinity_metrics` | `WorldContext.export_queue_affinity_metrics()` (currently consumed by DTO tests) | `WorldContext.queue_manager.performance_metrics()` |
| `employment_snapshot` | `WorldContext.export_employment_snapshot()` | `WorldContext.employment_service.snapshot()` |
| `economy_snapshot` | `WorldContext.export_economy_snapshot()` | `WorldContext.economy_service.snapshot()` |
| `anneal_context` | `self.policy.anneal_context()` | Loop responsibility (policy-specific) |
| `agent_contexts` | `observation_agent_context(adapter, agent)` | Observation service / DTO builder inside context |

Notes:
- Fields labelled “Loop responsibility” remain inputs supplied by the loop even once `WorldContext.observe()` exists.
- Observation service must expose per-agent context (`pending_intent`, queue view, etc.) currently obtained via `observation_agent_context` helper.
- Legacy collectors on `SimulationLoop` (e.g., `_collect_queue_metrics`) have been removed; the loop now relies on `WorldContext.export_*` helpers so it stays a thin coordinator.
