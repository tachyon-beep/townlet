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
