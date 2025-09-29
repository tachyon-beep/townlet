# Anneal Promotion Baselines (Phase 5.5)

## Baseline Metrics (Latest Runs)

| Metric | Source | Value |
| --- | --- | --- |
| BC accuracy (idle_v1) | `artifacts/m5/acceptance/summary_idle_v1.json` | **1.00** (threshold 0.80)
| PPO loss_total (idle_v1) | `artifacts/m5/acceptance/summary_idle_v1.json` | 0.2265 |
| PPO updates (idle_v1) | `artifacts/m5/acceptance/summary_idle_v1.json` | 14 |
| Queue conflict events (scenario mean) | `artifacts/phase4/queue_conflict/watch.jsonl` | 16 (max 32) |
| Queue conflict intensity (scenario mean) | `artifacts/phase4/queue_conflict/watch.jsonl` | 26.4 (max 52.75) |
| Queue conflict events (employment punctuality) | `artifacts/phase4/employment_punctuality/watch.jsonl` | 19.5 (max 39) |
| Queue conflict intensity (employment punctuality) | `artifacts/phase4/employment_punctuality/watch.jsonl` | 29.3 (max 58.5) |
| Late help events (employment punctuality avg) | `tmp/social_metric_aggregates.json` | 1.0 |
| Queue conflict loss_total mean (phase4 scenarios) | computed | see table below |

### Loss & Queue Metrics by Scenario

| Scenario | loss_total μ ± σ | queue_events μ / max | intensity μ / max |
| --- | --- | --- | --- |
| queue_conflict | 1.37 ± 0.23 | 16 / 32 | 26.38 / 52.75 |
| queue_conflict_soak | 1.39 ± 0.14 | 16 / 32 | 26.38 / 52.75 |
| employment_punctuality | 1.77 ± 0.11 | 19.5 / 39 | 29.25 / 58.5 |
| rivalry_decay | 1.61 ± 0.04 | 16 / 32 | 24.00 / 48 |

### Social Interaction Baselines

- `late_help_events`: average 1.0 per run (0–2 range) in employment punctuality scenarios.
- Other social metrics (`shared_meal`, `chat_success`, `chat_quality`) currently register **0** in baseline runs; treat non-zero values as signal once social affordances expand.

## Notes

- Baselines combine acceptance smoke (`idle_v1_production`) and Phase 4 scenario soaks.
- Update this document when new datasets or scenarios introduce non-zero social metrics.
- Record at least **three** anneal cycles per dataset before evaluating promotion gates.

## Promotion Thresholds (Proposed)

| Dimension | Threshold | Evaluation Window | Rationale |
| --- | --- | --- | --- |
| BC accuracy | Rolling mean ≥ **0.90**; min per run ≥ **0.85** | Last 3 anneal rehearsals | Idle_v1 baseline =1.0; allows modest noise while catching regressions. |
| PPO loss_total | Rolling mean within **±10 %** of scenario baseline; variance ≤ **0.05** | Last 3 rehearsals per scenario | Phase 4 loss μ ranges 1.37–1.77; 10 % bands keep within observed drift. |
| Queue conflict events | Stay within **±15 %** of baseline mean; max ≤ baseline max | Same | Protects conflict pressure captured in Phase 4. |
| Queue intensity sum | Stay within **±15 %** of baseline mean; max ≤ baseline max | Same | Mirrors event threshold to detect muted queues. |
| Social signals (late_help) | Mean ≥ **0.5** when scenario expects assistance; variance ≤ 1.0 | Employment punctuality | Ensures helper affordances stay active when model controls agents. |
| Telemetry health | `kl_divergence` ≤ **0.05**; `grad_norm` ≤ **2.5`; `entropy_mean` within baseline ±0.1 | Each run | Aligns with Phase 4 telemetry guardrails. |

> **Action:** Flag promotion as “hold” if any dimension breaches thresholds; require corrective run or dataset refresh before go-live.

### How Promotion Windows Are Evaluated

The stability monitor tracks promotion readiness using the configuration block at
`SimulationConfig.stability.promotion`:

- `required_passes`: consecutive windows that must complete without disallowed alerts.
- `window_ticks`: number of simulation ticks per evaluation window (rolling).
- `allowed_alerts`: alert identifiers that do **not** invalidate a window (for example,
  `embedding_reuse_warning` during expected reuse spikes).

On every tick, the monitor compares the active alert list against `allowed_alerts`.
If any other alert appears, the current window is marked as failed. When the window
length elapses:

1. The window is finalised; success increments the pass streak, failure resets it.
2. `candidate_ready` becomes `True` once `pass_streak >= required_passes`.
3. Telemetry snapshots expose `promotion.pass_streak`, `promotion.required_passes`,
   and `promotion.candidate_ready` so the UI and gate automation can surface the
   remaining passes.

> **Operational rule:** promotion remains blocked until the candidate is ready **and**
> the automated KPI checks above stay within bounds.

## Rollback Triggers & Detection Logic

1. **BC accuracy dip** — If `bc_accuracy < 0.85` on any rehearsal or production run:
   - Auto-trigger rollback by reverting to last safe checkpoint (`run_anneal` already halts when threshold fails).
   - Log incident in ops tracker and schedule dataset freshness review.

2. **PPO destabilisation** — Trigger rollback when either condition is true:
   - `loss_total` rises >15 % above baseline mean for two consecutive runs.
   - `kl_divergence` exceeds 0.05 **and** `grad_norm` > 2.5 in same run.
   Detection: extend `telemetry_watch.py` presets with `--kl-threshold 0.05` and `--grad-threshold 2.5`; treat simultaneous alerts as rollback signal.

3. **Queue/social drift** — Trigger rollback (or freeze anneal) when metrics breach limits twice in window:
   - `queue_conflict_events` or `queue_conflict_intensity_sum` falls outside ±20 % of baseline.
   - `late_help_events` drops to 0 across two rehearsals where scenario expects support.
   Detection: watcher JSON + summary tables already expose these values; add automated check in upcoming audit scripts.

4. **Telemetry degradation** — If watcher raises entropy/gradient anomalies (`entropy_mean` change >0.2 or `grad_norm` spikes >3.0), halt anneal and investigate policy behaviour before resuming.

> When rollback triggers fire, update the acceptance report with run details and capture corrective actions (dataset refresh, hyperparameter tweak, scenario fix).

## Tooling
- `scripts/telemetry_watch.py` includes anneal-specific switches (`--anneal-bc-min`, `--anneal-loss-max`, `--anneal-queue-min`, `--anneal-intensity-min`) to enforce these gates automatically when tailing PPO logs (defaults: 0.9 BC, ±10% loss, queue/intensity fall back to 85% of baseline).
- `scripts/telemetry_summary.py` (text/markdown) surfaces the latest anneal stage, dataset, accuracy vs threshold, and drift flags for inclusion in acceptance reports.
- The observer UI’s **Anneal Status** panel mirrors these metrics for live monitoring; see `docs/guides/OBSERVER_UI_GUIDE.md` for usage notes.
