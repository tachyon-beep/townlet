# Phase 4.2 – Observation & Telemetry Prep Notes

This document captures the upfront design decisions and validation checklist for **Phase 4.2 – Social Observations & Telemetry** before implementation begins. Pair it with the execution plan in `M4_SOCIAL_FOUNDATIONS_EXECUTION.md`.

## Observation Snippet Design

Targeting the conceptual design requirements (`snapshots/CONCEPTUAL_DESIGN.md` §5–6):

- **Top-K relationships:** expose top-2 friends + top-2 rivals (configurable). Each entry carries:
  - `id_embed` (8 floats, shared embedding table)
  - `trust`, `familiarity`, `rivalry` scalars
  - `tie_age` scalar (planned addition for churn awareness)
- **Local aggregates:** mean/max trust and rivalry for agents within the 9×9 hybrid window; occupancy weighted counts will land in telemetry only.
- **Fallback behaviour:** until the full relationship lattice lands, rivalry ledgers feed the snippet (trust/familiarity=0, rivalry>0) so PPO wiring can stabilise ahead of Phase 4.1 completion.
- **Feature slots:** baseline hybrid feature vector currently ~64 floats; new snippet adds `K * (embed_dim + 3)` + 2 aggregates. For K=4 with embed_dim=8 ⇒ +44 floats, keeping tensor < 120 dims.
- **Config gating:** `observations.social.top_k` + `embed_dim` new fields. Feature flags must hard-fail when policy hash doesn’t support enriched tensor.
- **Ledger readiness:** core relationship storage scaffolding (`RelationshipLedger`) is now available; snippet consumption will promote trust/familiarity once event hooks populate the ledger beyond rivalry fallbacks.

## Implementation Steps

1. Extend `ObservationsConfig` with `social_snippet` block (`top_k`, `embed_dim`, `include_aggregates`).
2. Update `ObservationBuilder` to splice snippet after self-scalars; ensure deterministic ordering (friends first by trust, rivals by rivalry).
3. Emit `ctx_reset_flag` when snippet membership changes to help PPO handle sudden shifts.
4. Extend `EmbeddingAllocator` to reserve additional slots for relationship IDs with cooldown reuse checks.
5. Update `TrainingHarness`/policy models so feature_dim is auto-discovered from observation batches.

## Profiling & Validation

- **Tensor footprint:** add script `scripts/profile_observation_tensor.py` to report per-tick feature_dim, map dims, and memory footprint for sample scenarios.
- **Latency:** run hybrid baseline vs enriched snippet for 100 ticks; target < 10% increase in observation build time.
- **PPO smoke:** extend existing smoke test to assert new feature_dim matches expected config and PPO loss finite.
- **Regression fixtures:** capture golden observation NPZ for deterministic scenario; use to diff future schema changes.
- **Current baseline:** `python scripts/profile_observation_tensor.py configs/examples/poc_hybrid.yaml --ticks 10` → feature_dim 68 (hybrid + social snippet), map shape 4×11×11, mean trust aggregate currently 0.0 pending richer relationship events.

## Telemetry Wiring Plan

- `TelemetryPublisher` already exposes relationship churn payload; Phase 4.2 will add per-tick tie snapshot entry.
- Update `scripts/telemetry_summary.py`/`telemetry_watch.py` with social interaction metrics (shared meals, late help, shift takeovers, chat quality) so ops can enforce thresholds.
- Ops: add watch thresholds (`relationships_evicted_per_window`, social interaction mins) in watcher CLI and Ops handbook. Current baseline table lives in `docs/ops/queue_conflict_baselines.md` and is sourced from automated soaks (see `tmp/social_metric_aggregates.json`).

## Open Questions / TBD

- Do we need dynamic Top-K (per personality)? For now fixed K to ease batching; revisit after soak feedback.
- Snippet ordering when no rivals observed yet — proposal: pad with zeros and set `tie_present` flag per slot.
- Need config migration story for existing manifests; prepare loader fallback that injects defaults and logs warning.

## Next Actions

1. Finalise config schema change and add migration note to `DOCUMENTATION_PLAN.md`.
2. Prototype observation builder branch to assert feature_dim math.
3. Draft profiling script + include invocation in Phase 4.2 acceptance criteria.
