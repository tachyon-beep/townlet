# Scripted Rollout Scenarios

This document outlines candidate scripted scenarios for generating deterministic
replay datasets. Each scenario aims to exercise a focused subsystem (queues,
conflict, employment, rewards) while remaining short enough for rapid capture.

## Scenario Design Principles
- **Deterministic State:** Use fixed seeds, scripted behaviors, or minimal agent
  counts to ensure repeatable trajectories.
- **Short Duration:** 20–100 ticks so captures remain lightweight and fast.
- **Targeted Coverage:** Each scenario illuminates specific state transitions or
  reward mechanics that should be reflected in replay metrics.
- **Minimal Dependencies:** Prefer standalone YAML configs with the standard
  asset set; avoid long-running simulation requirements.

## Scenario Candidates

### 1. Kitchen Breakfast Rush
- Config: `configs/scenarios/kitchen_breakfast.yaml`
- **Purpose:** Exercise queueing, affordance start/finish, and basic reward flow.
- **Setup:**
  - Two agents (`alice`, `bob`) spawn near a shared stove/fridge.
  - Scripted behavior forces sequential `request -> start -> finish` for a
    meal prep affordance.
  - Capture should show positive rewards, log-probs around action choice, and
    value predictions rising post-meal.
- **Ticks:** 40
- **Artifacts:** replay manifest with two samples, `queue_conflict` metrics near
  zero but need-driven action sequence visible.

### 2. Queue Conflict Hand-off
- Config: `configs/scenarios/queue_conflict.yaml`
- **Purpose:** Validate queue conflict telemetry and rivalry features.
- **Setup:**
  - Three agents attempt to use a single checkout; scripted logic forces one to
    block, triggering ghost-step/hand-off events.
  - Track rivalry increases and ensure `rewards` include penalties where
    applicable.
- **Ticks:** 60
- **Artifacts:** replay samples showing `rivalry_max` growth, positive `log_prob`
  adjustments when agents yield or avoid conflict.

### 3. Employment Punctuality Drill
- Config: `configs/scenarios/employment_punctuality.yaml`
- **Purpose:** Cover employment loop states, lateness penalties, and reward
  deductions.
- **Setup:**
  - Two agents assigned to staggered shifts with scripted arrival times (one
    punctual, one late).
  - Rewards should capture lateness penalty, while value predictions diverge.
- **Ticks:** 80
- **Artifacts:** metadata capturing shift state transitions, negative rewards for
  late arrivals, value head anticipating penalties.

### 4. Rivalry Decay & Resolution
- Config: `configs/scenarios/rivalry_decay.yaml`
- **Purpose:** Showcase rivalry increment/decay and confirm log-probs capture
  conflict-driven decisions.
- **Setup:**
  - Pair of agents with forced repeated conflicts followed by cooperative
    actions; rivalry should rise then decay.
  - Monitor action policy adjustments and value responses.
- **Ticks:** 50
- **Artifacts:** replay samples showing alternating high/low rivalry stats.

### 5. Observation Baseline Smoke
- Config: `configs/scenarios/observation_baseline.yaml`
- **Purpose:** Provide a minimal scenario with no major events (control).
- **Setup:**
  - Single agent idles; ensures zero rewards, consistent log-probs, value near
    baseline.
- **Ticks:** 20
- **Artifacts:** baseline sample for regression comparisons.

## Capture Strategy
- Place scenario YAMLs under `configs/scenarios/` with descriptive names.
- Extend `scripts/capture_rollout.py` with `--scenario` presets referencing these
  configs.
- Provide a simple wrapper script (e.g., `scripts/capture_scenarios.py`) to loop
  over all scenarios and dump manifests.
- Use `configs/scenarios/_template.yaml` as a validated starting point for new
  scenario configs (includes seeding, reward defaults, behaviour thresholds).
- Each capture writes `<prefix>_metrics.json` alongside the manifest, capturing
  reward breakdowns, rivalry statistics, action distributions, and lateness
  averages to aid tuning.

## Risk-Reduction Prestage Activities
- **Scripted Behaviour Hooks (Completed):** `tests/test_scripted_behavior.py` injects a
  deterministic stub to validate repeatable action schedules.
- **Seed Audit (Completed):** `PolicyRuntime` seeds torch networks deterministically
  (`torch.manual_seed(0)`), and capture runs now produce identical log-probs/value preds across
  executions.
- **Golden Stats Fixture (Completed):** Baseline metrics stored in
  `docs/samples/rollout_baseline_stats.json` capture reward sums/log-probs for regression checks.
- **CLI Automation Harness (Completed):** `scripts/capture_rollout_suite.py` iterates configs and
  invokes `capture_rollout.py`, simplifying multi-scenario captures.
- **Config Template (Completed):** `configs/scenarios/_template.yaml` provides a validated base
  config for new scripted scenarios.

## Validation Hooks
- Add pytest fixture to run `capture_rollout.py` for each scenario and verify:
  - Replay NPZ contains expected timesteps/action_dim.
  - Metrics (e.g., rivalry_max, rewards) fall within expected ranges.
  - Log-probs/value predictions are finite (no NaNs).
- Golden stats JSON (`docs/samples/rollout_scenario_stats.json`) provides
  baseline reward/log-prob metrics; `tests/test_rollout_capture.py` exercises
  captures and compares against these values for drift detection.

## Open Questions
- Should scenarios enforce scripted behavior via config or via custom behavior
  controllers? (Config-driven preferred for reproducibility.)
- How many ticks do we need to capture meaningful engagement without bloating
  sample size?
- What schedule should we adopt for regenerating scenario samples (per release,
  CI nightly)?
