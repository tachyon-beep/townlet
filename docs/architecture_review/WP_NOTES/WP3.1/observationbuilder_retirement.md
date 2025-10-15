# ObservationBuilder Retirement Plan

## Background
`ObservationBuilder` (1060 lines) was supposed to be replaced by DTO envelopes delivered through `ObservationService`. The class, its imports, and associated tests still exist, contradicting the Stage 6 status report.

## Current State Audit
- `ObservationBuilder` defined in `src/townlet/observations/builder.py` with extensive dependencies on legacy world state.
- Factory exports `ObservationBuilder` (`src/townlet/observations/__init__.py:7-15`).
- Numerous tests/scripts instantiate the builder (`tests/test_observation_builder_full.py`, `tests/test_observation_builder_compact.py`, `scripts/profile_observation_tensor.py`).
- DTO parity harness still references legacy builder snapshots for comparison.

## Implementation Plan

### 1. Reference Enumeration
1.1 `rg "ObservationBuilder" -n src tests scripts docs` and export the result to
    `WP3.1/recovery_log.md` for traceability.
1.2 Classify each hit:
    - Runtime (policy runner, telemetry, adapters).
    - Test (observation parity, embedding allocator, builder-specific tests).
    - Tooling (scripts, docs examples).
1.3 For each runtime usage, note the fields consumed from the builder output.

### 2. DTO Capability Audit
2.1 Map builder features to DTO equivalents using
    `ObservationService.observe()` + `ObservationEnvelope` schema.
    - Document any missing channels (e.g. social snippet toggles) in the same
      log.
2.2 If gaps exist, schedule schema additions (coordinated with WP3 DTO work).

### 3. Runtime Migration
3.1 Update `townlet/policy/runner.py` to require envelopes and remove fallback
    imports of `ObservationBuilder`.
3.2 Update scripted behaviour/training orchestrator to consume DTO world views
    only (no builder instantiation).
3.3 Replace builder usage in telemetry or profiling scripts with DTO service
    hooks.
3.4 Acceptance: `rg "ObservationBuilder" src/townlet` returns 0 before file
    deletion.

### 4. Test Migration
4.1 Replace builder tests with DTO equivalents:
    - Convert `tests/test_observation_builder_full.py` into a DTO parity test
      that asserts schema content using `ObservationService.observe()`.
    - Do the same for compact, baseline, and embedding allocator tests by
      reading from DTO envelopes.
4.2 Update fixtures creating builder instances to instantiate DTO services.
4.3 Acceptance: `rg "ObservationBuilder" tests` returns 0 (except guard test).

### 5. Tooling & Docs
5.1 Update `scripts/profile_observation_tensor.py` to profile DTO envelopes or
    mark it deprecated.
5.2 Replace documentation snippets referencing the builder with DTO pipeline
    explanations (`docs/design/OBSERVATION_TELEMETRY_PHASE3.md`,
    `docs/testing/QA_CHECKLIST.md`).

### 6. Deletion & Guard Rails
6.1 Remove `src/townlet/observations/builder.py` and drop the import from
    `observations/__init__.py` (keep only DTO factory exports).
6.2 Add `tests/test_observation_builder_removed.py` ensuring import raises
    `ImportError`.
6.3 Update `setup.cfg` or module metadata files to remove builder references.

### 7. Artefact Refresh
7.1 Re-record DTO sample files under `docs/architecture_review/WP_NOTES/WP3/dto_parity/`
    using the new envelope-only path.
7.2 Update parity harness baselines if numeric ordering changes.

### 8. Validation Sequence
- `rg "ObservationBuilder" src tests scripts docs`
- `pytest tests/core/test_sim_loop_dto_parity.py -q`
- `pytest tests/policy/ -q`
- `pytest tests/test_observation_builder_removed.py -q`
- Manual DTO smoke: `python scripts/run_training.py --config configs/examples/base.yml`
  (capture observation-related logs for the recovery log).

## Validation Checklist
- [ ] `grep -r "ObservationBuilder" src/ tests/ scripts/` returns no results.
- [ ] DTO parity harness passes: `pytest tests/core/test_sim_loop_dto_parity.py -q`.
- [ ] Policy/training tests pass: `pytest tests/policy/ -q`.
- [ ] Guard test passes: `pytest tests/test_observation_builder_removed.py -q`.
- [ ] Profiling/training scripts run against DTO path (document smoke runs in recovery log).

## Risks & Mitigations
- **Feature coverage gaps:** ensure DTO envelopes include all builder-provided channels; coordinate with feature owners if missing data.
- **Performance regression:** monitor observation generation time after switching to DTO path; capture metrics in recovery log.
- **External tooling:** communicate removal to data pipeline owners using builder outputs.

## Dependencies
- Requires adapter surface cleanup (workstream 2) so policies no longer rely on builder-supplied fallback data.
- Console queue retirement can occur in parallel but should be complete before final DTO verification.
