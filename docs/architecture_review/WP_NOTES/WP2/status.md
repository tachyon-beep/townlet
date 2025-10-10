# WP2 Status

**Current state (2025-10-10)**
- Planning, skeleton, stateless helper extraction, and state/action/system scaffolding (Steps 0–6) remain green; unit suites across `tests/world/**` continue to pass.
- Step 7 factory/adapter integration is effectively complete: default providers now build `WorldContext`, dummy adapters are aligned, and `WorldRuntimeAdapter` bridges the modular result into remaining legacy pathways. Migration notes for the simulation loop live under WP1 but reflect WP2 surfaces.
- WP3B completion and the ongoing WP3C DTO rollout mean world adapters must now expose DTO-derived snapshots; the context supplies queue/affordance/employment/economy/relationship data required by the policy/telemetry ports. Recent DTO export work (RolloutBuffer `*_dto.json`) ensures training tooling can consume modular outputs without relying on legacy observation dicts.
- Remaining blockers before sign-off are tied to WP3C Stage 3/5: once policy/training consumers operate DTO-only, we can drop the legacy handles from the world adapters/factory and finish the composition-root cleanup.

**Next steps**
1. Coordinate with WP3C to remove the legacy observation translator and confirm policy/training adapters never request `WorldState` snapshots directly.
2. Update world adapter surfaces to expose DTO-ready observations/metadata only, then delete the compatibility hooks (`legacy_runtime`, observation dict, queue_console) when WP1 Step 8 resumes.
3. Refresh documentation (ADR-002 appendix) once the adapter cleanup lands and ensure WP1/WP3 status notes reference the final world provider flow.
