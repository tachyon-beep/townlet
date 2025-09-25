# PPO Telemetry Schema Upgrade (telemetry_version 1.1 Draft)

## Objectives
- Expose richer PPO health metrics for dashboards and automated guardrails.
- Tag alternating rollout↔train cycles so streaming consumers can correlate rollouts with subsequent updates.
- Preserve backwards-compatibility by allowing `telemetry_version == 1.0` payloads through a config toggle during rollout.

## Proposed Additions
| Field | Type | Description |
| --- | --- | --- |
| `epoch_duration_sec` | float | Wall-clock seconds spent in the epoch (capture start/end timestamps). |
| `data_mode` | str | `"replay"` when sourced from manifest, `"rollout"` when fed from in-memory buffer, `"mixed"` during alternating cycles. |
| `cycle_id` | int | Monotonic identifier incremented each time we run `capture_rollout` before training; stays `0` when replay-only. |
| `batch_entropy_mean` | float | Mean entropy across all batches in the epoch (helps spot policy collapse). |
| `batch_entropy_std` | float | Standard deviation of entropy across batches. |
| `grad_norm_max` | float | Maximum gradient norm observed across mini-batches for the epoch. |
| `kl_divergence_max` | float | Maximum KL divergence observed (current average kept as-is). |
| `reward_advantage_corr` | float | Pearson correlation between rewards and advantages (sanity check for GAE). |
| `rollout_ticks` | int | Number of environment ticks captured for the dataset feeding the epoch (0 for pure replay). |
| `log_stream_offset` | int | Incrementing counter for NDJSON streaming mode (used by tailers to resume). |

## Compatibility Strategy
- Increment `telemetry_version` to `1.1` when new fields are present.
- Add harness flag `enable_telemetry_v1_1: bool = True` to fall back to 1.0 format if downstream consumers lag.
- Validator changes:
  - Accept 1.0 and 1.1; enforce new keys only when version == 1.1.
  - Ensure relative drift summary skips fields missing in baseline.
- Sample updates: extend `docs/samples/ppo_conflict_telemetry.jsonl` with new fields once implementation lands and regenerate canonical values.

## Implementation Checklist
1. Capture epoch start/end timestamps inside `TrainingHarness.run_ppo`.
2. Thread data-mode context into harness (dataset config vs rollout buffer) and store cycle id.
3. Accumulate entropy/grad/kl stats while iterating mini-batches.
4. Compute reward/advantage correlation using numpy (guard against zero variance).
5. Surface rollout tick counts from `RolloutBuffer.build_dataset()` metadata.
6. Maintain a log stream offset counter and include it in each summary.
7. Update validator + tests (`tests/test_telemetry_validator.py`) for versioned checks and failure cases.
8. Refresh docs/ops guides with new field explanations and streaming notes.
9. Run long alternating-cycle endurance tests to exercise the expanded metrics.

## Open Questions
- Do we need per-agent breakdowns in schema v1.1 or leave for future release?
- Should `log_stream_offset` reset on rotation or remain global? (Leaning global so watchers can deduplicate.)
- What thresholds should `telemetry_watch.py` use for new metrics (entropy collapse, reward/adv correlation)?
