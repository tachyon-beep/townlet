# WP3C – DTO Parity Expansion & ML Validation

Purpose: Demonstrate DTO-only correctness across scripted and ML-backed scenarios so we can retire
legacy observation payloads and finish the WP1/WP2 composition-root cleanup.

## Objectives

1. Enrich the DTO parity harness to compare reward breakdown components, queue metrics, and policy
   metadata between legacy and DTO pipelines.
2. Exercise an ML-backed policy (short PPO/BC loop or replay) using DTO inputs, proving action and
   reward parity.
3. Finalise documentation and guard tests that prevent reintroduction of legacy observation flows.

## Work Breakdown

### A. Harness Enhancements
- Extend `tests/core/test_sim_loop_dto_parity.py` with reward breakdown diffs, queue/relationship
  snapshots, and telemetry payload assertions.
- Capture baseline fixtures for scripted vs DTO outputs (store under `tests/data/dto_parity/`).
- Add regression checks that fail if DTO schema fields are removed without updating fixtures.

### B. ML Smoke Scenario
- Stand up a minimal ML policy configuration (e.g., conflict-aware PPO checkpoint) that can run for
  20–30 ticks locally.
- Instrument the run to record DTO observations, actions, and rewards alongside the legacy path; use
  tolerance-based comparisons for floating-point outputs.
- Provide a feature flag so the smoke can be skipped in environments without Torch; mark the test
  `@pytest.mark.slow`.

### C. Legacy Observation Decommission
- Once parity is confirmed, remove the legacy observation blob from `loop.tick` telemetry payloads
  and delete consumer-side shims.
- Trim policy training/export code that still references `world.observations`.
- Update docs (WP1/WP2/WP3, ADR-001) with the DTO-only guidance and migration notes for downstream
  consumers.

### D. Guard Rails
- Add pytest guards ensuring legacy observation getters/writers stay removed.
- Wire CI targets (docs or scripts) that diff DTO fixtures whenever the schema version bumps.

## Exit Criteria

- DTO parity harness exercises scripted rewards, queue metrics, and policy metadata without relying
  on legacy snapshots.
- ML smoke test passes (or xfails with documented reason) using DTO inputs only.
- Telemetry/policy code no longer emits or expects legacy observation payloads.
- Documentation and tasks updated to reflect DTO-only operation.
