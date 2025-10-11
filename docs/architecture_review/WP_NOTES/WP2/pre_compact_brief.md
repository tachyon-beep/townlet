# WP2 Pre-Compact Brief (2025-10-11)

Snapshot of WP2 so the next session can resume without re-auditing prior work.

## Completed to date
- **Steps 0–3**: planning, skeleton package creation, and stateless helper extraction (spatial index, observation helpers, event primitives) remain in place with unit coverage.
- **Steps 4–6**: `AgentRegistry`, `WorldState`, action validation pipeline, and modular system orchestration (`queues`, `affordances`, `employment`, `relationships`, `economy`, `perturbations`) are all wired through `WorldContext.tick`, returning `RuntimeStepResult` with deterministic RNG streams. Tests across `tests/world/**` continue to pass.
- **Step 7 factory integration**: default/dummy world providers now construct `WorldContext`, registry metadata stays accurate, and `WorldRuntimeAdapter` bridges modular results for callers still expecting the legacy runtime. Docs and tasks are updated accordingly.
- DTO export plumbing from WP3C is compatible: trajectory frames include DTO metadata and `RolloutBuffer.save` emits `*_dto.json` artefacts referenced in manifests, so world consumers can migrate without relying on the legacy observation dict.

## Outstanding
1. Coordinate with WP3C to finish DTO-only policy/training adapters and retire the legacy observation translator; once complete, remove the legacy handles from world adapters/factories (Step 7 cleanup) and proceed with Step 8 composition-root refactor alongside WP1.
2. Update ADR-002/README once the adapter cleanup lands and ensure the simulation loop no longer references `WorldState` internals.
3. Prepare regression coverage for the default provider swap (factory tests, loop smokes) when WP1 Step 8 resumes.

## Key notes
- Observation building now lives inside the world context (via
  `WorldObservationService`); adapters no longer own the builder directly, but
  final DTO-only observers will replace the wrapper once WP3 Stage 6 closes.
- Console/telemetry orchestration is owned by WP1; WP2’s responsibility is to expose port-friendly world services and drop legacy shims when DTO parity is confirmed.
- Track dependencies in `WP3C_plan.md` and WP1 status so we remove the legacy world handles immediately after DTO-only consumers ship.
