# WP2 Status

**Current state (2025-10-11)**
- Planning, skeleton, stateless helper extraction, and state/action/system scaffolding (Steps 0–6) remain green; unit suites across `tests/world/**` continue to pass.
- Step 7 factory/adapter integration is effectively complete: default providers now build `WorldContext`, dummy adapters are aligned, and `WorldRuntimeAdapter` bridges the modular result into remaining legacy pathways. Migration notes for the simulation loop live under WP1 but reflect WP2 surfaces.
- Console services are now supplied by the factory via `WorldState.attach_console_service`; `WorldComponents` threads the handle into the loop and telemetry captures dispatcher-emitted results (no `_console_results_batch` mirrors). Console/telemetry regressions (`tests/test_console_router.py`, `tests/test_console_commands.py`, `tests/test_console_dispatcher.py`, `tests/test_telemetry_new_events.py`) stay green.
- WP3B completion and the ongoing WP3C DTO rollout mean world adapters must now expose DTO-derived snapshots; the context supplies queue/affordance/employment/economy/relationship data required by the policy/telemetry ports. Recent DTO export work (RolloutBuffer `*_dto.json`) ensures training tooling can consume modular outputs without relying on legacy observation dicts.
- Stage 6 guardrails in WP3 were re-run on 2025-10-11 after removing the last
  `ObservationBuilder` imports from the world package; telemetry surface guards
  remain green, so adapter cleanup can proceed once the remaining Stage 6 tasks
  (docs + regression sweep) land.
- Remaining blockers before sign-off are the DTO-only ML parity work and final world adapter surface cleanup (dropping ObservationBuilder shims and queue console hooks) once WP3C wraps; telemetry consumers are now DTO-native, so adapter cleanup can focus on slimming the world surface.

**Next steps**
1. Coordinate with WP3C to remove the legacy observation translator and confirm policy/training adapters never request `WorldState` snapshots directly.
2. Update world adapter surfaces to expose DTO-ready observations/metadata only, then delete the compatibility hooks (`legacy_runtime`, observation dict, queue_console) when WP1 Step 8 resumes.
3. Refresh documentation (ADR-002 appendix) once the adapter cleanup lands and ensure WP1/WP3 status notes reference the final world provider flow.

---

## WP3 Stage 6 Recovery Completion (2025-10-13)

**✅ UNBLOCKED**: WP3 Stage 6 Recovery (WP3.1) has been completed, clearing blockers for WP2 Step 7 completion.

**What was completed:**
- Console queue shim (`queue_console_command` / `export_console_buffer`) fully removed from world runtime
- Adapter escape hatches cleaned up (4 deprecated properties removed: `.world_state`, `.context`, `.lifecycle`, `.perturbations`)
- `ObservationBuilder` fully retired from world package (1059 lines deleted, replaced with modular encoder functions)
- All world/adapter tests passing (15/15), observation tests passing (24/24)
- Guard tests updated to prevent reintroduction of legacy patterns

**Impact on WP2:**
- World adapter surface is now fully cleaned (no escape hatches to legacy internals)
- DTO-only observation flow established via `WorldObservationService`
- Console service integration complete (factory-provided, event-based)
- Modular systems (queue/affordance/employment/economy/relationships) verified

**Next Steps for WP2:**
1. ✅ Adapter surface cleanup complete - no further action needed
2. Coordinate with WP3C on remaining DTO parity tasks
3. Final documentation refresh (ADR-002 appendix) once WP1 Step 8 completes
4. Update world provider flow documentation

See `docs/architecture_review/WP_NOTES/WP3.1/` for comprehensive recovery documentation.
