# Phase 4 Scenario Artefacts

These directories hold the canonical mixed-mode rollout → PPO telemetry captures used to close out
Phase 4 of the PPO integration workstream. Each scenario folder contains:

- `rollout_sample_manifest.json` / `rollout_sample_metrics.json`
- Per-agent NPZ/JSON payloads produced by `scripts/capture_rollout.py`
- PPO telemetry log (`ppo_*.jsonl`)
- Watch output (`watch.jsonl`) generated via `scripts/telemetry_watch.py --json`
- Markdown summary exported via `scripts/telemetry_summary.py --format markdown`

## Scenarios
| Directory | Scenario Config | Mode | Rollout Ticks | Notes |
| --- | --- | --- | --- | --- |
| `queue_conflict` | `configs/scenarios/queue_conflict.yaml` | mixed (replay→rollout) | 40 | Queue conflict baseline used in CI guardrail |
| `employment_punctuality` | `configs/scenarios/employment_punctuality.yaml` | mixed (replay→rollout) | 60 | Employment punctuality mixed-mode benchmark |
| `rivalry_decay` | `configs/scenarios/rivalry_decay.yaml` | mixed (replay→rollout) | 50 | Rivalry decay coverage |
| `observation_baseline` | `configs/scenarios/observation_baseline.yaml` | rollout | 30 | Control run (zero queue conflicts) |
| `queue_conflict_soak` | `configs/scenarios/queue_conflict.yaml` | alternating replay/rollout | 40 | 12-cycle soak harness output |

## Repro Commands
```
python scripts/capture_rollout.py <config> --output artifacts/phase4/<dir> --compress
python scripts/run_training.py <config> --mode mixed --replay-manifest artifacts/phase4/<dir>/rollout_sample_manifest.json \
  --rollout-ticks <ticks> --epochs 1 --ppo-log artifacts/phase4/<dir>/ppo_mixed.jsonl
python scripts/validate_ppo_telemetry.py artifacts/phase4/<dir>/ppo_mixed.jsonl
python scripts/telemetry_watch.py artifacts/phase4/<dir>/ppo_mixed.jsonl --json > artifacts/phase4/<dir>/watch.jsonl
python scripts/telemetry_summary.py artifacts/phase4/<dir>/ppo_mixed.jsonl --format markdown > artifacts/phase4/<dir>/summary.md
```
Adjust `--mode`/`--rollout-ticks` for the control scenario where replay input is not required.

For soak runs, use `python scripts/run_mixed_soak.py ... --output-dir artifacts/phase4/queue_conflict_soak`
and inspect `ppo_soak.jsonl`/`summary.md` for drift analytics.

## Baselines
Queue-conflict event and intensity baselines are tabulated in `docs/ops/queue_conflict_baselines.md`.
Reference this directory when updating watch thresholds or regenerating mixed-mode captures.
