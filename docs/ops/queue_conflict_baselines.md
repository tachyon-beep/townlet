# Queue Conflict Telemetry Baselines

| Scenario | Mode | Rollout Ticks | Queue Conflict Events | Intensity Sum | Notes |
| --- | --- | --- | --- | --- | --- |
| queue_conflict | mixed (replay→rollout) | 40 | 32.0 | 52.75 | Captured via `capture_rollout.py` then `run_training.py --mode mixed`; log `artifacts/phase4/queue_conflict/ppo_mixed.jsonl`. |
| employment_punctuality | mixed (replay→rollout) (baseline) | 60 | 39.0 | 58.50 | Baseline for employment scenario; log `artifacts/phase4/employment_punctuality/ppo_mixed.jsonl`. |
| rivalry_decay | mixed (replay→rollout) | 50 | 32.0 | 48.00 | Rivalry scenario; log `artifacts/phase4/rivalry_decay/ppo_mixed.jsonl`. |
| observation_baseline | rollout | 30 | 0.0 | 0.00 | Control scenario; log `artifacts/phase4/observation_baseline/ppo_rollout.jsonl`. |

Use these targets to configure `telemetry_watch.py --queue-events-min` and
`--queue-intensity-min` thresholds. Set guardrails ~10–15% below the tabled values unless
intentionally exploring lower conflict pressure.

Monitor hygiene/rest counters alongside these baselines. For steady-state runs use `--utility-outage-max 0` (unless intentionally toggling utilities) and require at least one shower/sleep completion per window (`--shower-complete-min`, `--sleep-complete-min`). Adjust per scenario once additional hygiene affordances are introduced.

```bash
python - <<'PY'
from pathlib import Path
from types import SimpleNamespace
from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.policy.scenario_utils import apply_scenario

config = load_config(Path('configs/scenarios/queue_conflict.yaml'))
loop = SimulationLoop(config)
apply_scenario(loop, config.scenario)
loop.telemetry._transport_client = SimpleNamespace(send=lambda payload: None, close=lambda: None)
for _ in range(80):
    loop.step()
print(loop.telemetry.latest_conflict_snapshot()['queues'])
PY
```

The snippet above reproduces the scenario snapshot placed under `docs/samples/queue_conflict_snapshot.json` and is useful when validating guardrail tweaks locally. A similar block with `rivalry_decay.yaml` refreshes `docs/samples/rivalry_decay_snapshot.json`.

## Social Interaction Baselines

| Scenario | shared_meal_events (avg|min|max) | late_help_events | shift_takeover_events | chat_success/events | chat_failure_events | chat_quality_mean | Watcher Guidance |
| --- | --- | --- | --- | --- | --- | --- | --- |
| queue_conflict | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.0 / 0.0 / 0.0 | `--shared-meal-min 0`, `--late-help-min 0`, `--shift-takeover-max 1`, `--chat-quality-min 0.0` |
| employment_punctuality | 0 / 0 / 0 | **1 / 0 / 2** | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.0 / 0.0 / 0.0 | Require helpers: `--late-help-min 1`; others 0 |
| employment_punctuality (long soak) | 0 / 0 / 0 | **1 / 0 / 2** | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.0 / 0.0 / 0.0 | Maintain `--late-help-min ≥1`; monitor variance |
| rivalry_decay | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.0 / 0.0 / 0.0 | Social thresholds can stay permissive |
| kitchen_breakfast | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.0 / 0.0 / 0.0 | No social activity yet; keep defaults at 0 |
| kitchen_breakfast (long soak) | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.0 / 0.0 / 0.0 | Same as short run |
| observation_baseline | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.0 / 0.0 / 0.0 | Control scenario; all social thresholds 0 |

Collect additional data once social affordances/media features land; update this table before tightening thresholds.

**Latest soak metrics (2025-09-29)**

- `queue_conflict` mixed soak (`scripts/run_mixed_soak.py --cycles 4 --epochs 1 --rollout-ticks 40`)
  - Queue conflicts: 32 events, intensity sum 52.75 (matches table baseline).
  - Social metrics: shared_meal_events 0, late_help_events 0, shift_takeover_events 0, chat_success_events 0, chat_failure_events 0, chat_quality_mean 0.0.
  - Artefacts: `artifacts/phase4/queue_conflict/soak_summary.md`, `artifacts/phase4/queue_conflict/soak_watch.jsonl`.
  - No social interactions are expected in this scenario; thresholds remain permissive (keep shared_meal_min at 0 for this run).
- `employment_punctuality` mixed soak (`--rollout-ticks 60`)
  - Queue conflicts: 39 events, intensity sum 58.50 (aligns with table).
  - Social metrics: shared_meal_events 0, late_help_events 2, shift_takeover_events 0, chat_success_events 0, chat_failure_events 0, chat_quality_mean 0.0.
  - Artefacts: `artifacts/phase4/employment_punctuality/soak_summary.md`, `artifacts/phase4/employment_punctuality/soak_watch.jsonl`.
  - Update watcher defaults for employment scenarios to require `--late-help-min 1` while keeping other social thresholds permissive.
- `rivalry_decay` mixed soak (`--rollout-ticks 50`)
  - Queue conflicts: 32 events, intensity sum 48.0 (matches table baseline).
  - Social metrics: shared_meal_events 0, late_help_events 0, shift_takeover_events 0, chat_success_events 0, chat_failure_events 0, chat_quality_mean 0.0.
  - Artefacts: `artifacts/phase4/rivalry_decay/soak_summary.md`, `artifacts/phase4/rivalry_decay/soak_watch.jsonl`.
  - Rivalry scenario is conflict-driven but not social; keep social thresholds relaxed for this run (focus on queue metrics).
- `kitchen_breakfast` mixed soak (`--rollout-ticks 40`)
  - Queue conflicts: 26 events, intensity sum 39.0.
  - Social metrics: shared_meal_events 0, late_help_events 0, shift_takeover_events 0, chat_success_events 0, chat_failure_events 0, chat_quality_mean 0.0 (scenario focuses on kitchen usage without explicit social interactions).
  - Artefacts: `artifacts/phase4/kitchen_breakfast/soak_summary.md`, `artifacts/phase4/kitchen_breakfast/soak_watch.jsonl`.
- `observation_baseline` rollout soak (`--rollout-ticks 30`)
  - Queue conflicts: 0 events (control scenario).
  - Social metrics: shared_meal_events 0, late_help_events 0, shift_takeover_events 0, chat_success_events 0, chat_failure_events 0, chat_quality_mean 0.0.
  - Artefacts: `artifacts/phase4/observation_baseline/soak_summary.md`, `artifacts/phase4/observation_baseline/soak_watch.jsonl`.
