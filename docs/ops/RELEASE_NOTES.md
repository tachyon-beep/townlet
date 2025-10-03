# Release Notes — Observation Variant Parity (2025-10-22)

## Highlights
- Full and compact observation variants now match the ADR specification. All
  variants share the same feature initialisation path and expose enriched
  metadata (`variant`, `map_shape`, `map_channels`, `social_context`).
- Social snippets are populated from the relationship ledger (rivalry fallback
  when ties are missing) with aggregate trust/rivalry metrics. Observation
  metadata records how many slots were filled and which source supplied the
  data.
- Tooling refresh: replay/profile scripts persist and render the richer
  metadata; scripted capture embeds metadata in behaviour cloning datasets and
  the tensor profiler reports social slot coverage and relation sources.

## Required Actions for Training & Scenarios
1. **Regenerate replay datasets** captured with `scripts/capture_scripted.py` or
   `scripts/capture_rollout.py` to pick up the new metadata schema. Downstream
   consumers should read `sample.metadata` instead of assuming fixed feature
   indices.
2. **Update training harness configs** that rely on variant-specific behaviour:
   - Set `features.systems.observations` to `full` or `compact` as needed; the
     harness now respects the full channel list and compact’s feature-only mode.
   - When using social snippets, ensure
     `features.stages.relationships` is ≥ `"A"` and document expected slot
     counts in scenario manifests for auditing.
3. **Scenario configs** that reference observation shapes (e.g., custom model
   heads) should pivot to metadata introspection (`map_shape`, `feature_names`)
   rather than static dimensions. Regenerate golden fixtures stored under
   `docs/samples/` after switching variants.
4. **Telemetry/analytics pipelines** must account for the optional
   `social_context` metadata block when parsing observation payloads.

## Compatibility Notes
- No breaking changes to the hybrid variant; previously recorded replay samples
  remain valid but lack the new metadata. Refresh critical datasets to avoid
  mixed-schema archives.
- Telemetry schema unchanged, but CLI surfaces now expose social diagnostics in
  human-readable summaries. Ops should include the profiler JSON in upgrade run
  books to document social coverage.

## References
- `docs/design/OBSERVATION_TENSOR_SPEC.md`
- `docs/external/Townlet – Authoritative Design Reference.pdf`
- `docs/engineering/IMPLEMENTATION_NOTES.md` (2025-10-22 entry)

# Release Notes — Social Loop Completion (2025-10-23)

## Highlights
- Relationship ledger now drives both friendship and rivalry narrations
  (`relationship_friendship`, `relationship_rivalry`, `relationship_social_alert`) with
  configurable thresholds under `telemetry.relationship_narration`.
- Console surfaces expose social diagnostics via
  `relationship_summary`, `relationship_detail`, and `social_events`, and the observer
  dashboard Social section renders per-agent ties, churn metrics, and recent social events.
- Observation variants (hybrid/full/compact) ingest live relationship data so social snippet slots
  remain populated across all variants.

## Required Actions
1. **Telemetry consumers** must tolerate the new narration categories and optional
   `relationship_summary.churn` payload. Update alert rules/watchers to include the
   relationship categories alongside conflict narrations.
2. **Ops configuration**:
   - Use `features.stages.relationships` and `features.stages.social_rewards` to
     enable/disable relationship updates and reward loops in staging vs demo runs.
   - Tune narration thresholds via `telemetry.relationship_narration.*` when calibrating demo
     intensity (trust and rivalry cutoffs).
3. **Console/Dashboard workflows** should add the new social commands to dry-run checklists and
   capture screenshots/logs demonstrating the Social section populated during readiness reviews.

## Compatibility Notes
- Existing telemetry schema clients continue to function; new fields are additive. Pipelines that
  assume narrations only cover conflict must add allowlists for the three relationship categories.
- When social stages are disabled, narrations gracefully fall back to conflict-only output; the
  console commands still return empty summaries.

## References
- `docs/ops/OPS_HANDBOOK.md` (Social telemetry tooling section)
- `docs/design/OBSERVATION_TENSOR_SPEC.md`
- `docs/telemetry/TELEMETRY_CHANGELOG.md`
