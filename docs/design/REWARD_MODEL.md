# Reward Model Reference

This note captures the Townlet reward shaping contract for Milestone LR2.
It complements `docs/policy/REWARD_ENGINE.md` by describing every tap,
its configuration knobs, and telemetry exposure so design and ops stay in
sync as we expand the training harness.

## 1. Components

- **Survival tick** – `config.rewards.survival_tick` grants each agent a
  small positive base reward every tick to keep returns positive when
  they satisfy needs.
- **Needs penalty** – quadratic deficit cost per need using
  `config.rewards.needs_weights`. Deficits clamp to `[0, 1]` before we
  square so large gaps escalate quickly without producing runaway values.
- **Wages** – time-on-shift drives reward via
  `config.rewards.wage_rate`. RewardEngine reads employment context
  (`world.agent_context(agent_id)["wages_paid"]`) to avoid double counting
  wallet deltas or withheld wages. Withheld wages subtract from the tap so
  operators can see the penalty in the breakdown.
- **Punctuality** – scales the per-agent punctuality ratio (0–1) by
  `config.rewards.punctuality_bonus`. Employment bookkeeping ensures the
  ratio only reflects completed shifts; guardrails keep the bonus below
  hunger pain (`config.rewards.needs_weights.hunger`).
- **Social bonuses** – Phase C1 chat rewards (`config.rewards.social`)
  apply when `features.stages.social_rewards` ∈ {C1, C2, C3}. We clamp
  quality multipliers to `[0, 1]` and skip the tap when any tracked need
  deficit exceeds 0.85.
- **Terminal penalties** – new in LR2.1: RewardEngine applies
  `config.rewards.faint_penalty` when the lifecycle marks an agent as
  fainted and `config.rewards.eviction_penalty` for employment exits.
  Penalties are included explicitly in the breakdown as
  `terminal_penalty` so operators can audit when and why agents lost
  reward mass.

## 2. Guardrails

- **Death-window suppression** – `config.rewards.clip.no_positive_within_death_ticks`
  blocks positive totals for any agent flagged terminated within the
  configured window. Negative totals (including penalties) continue to
  flow so policy gradients still observe the consequence of failures.
- **Per-tick clip** – `config.rewards.clip.clip_per_tick` clamps the
  absolute reward after all taps and penalties. This keeps PPO gradients
  bounded even when inputs change suddenly (perturbations, outages).
- **Per-episode clip** – `config.rewards.clip.clip_per_episode` caps the
  running total so prolonged positive streaks do not destabilise value
  targets. Totals reset whenever lifecycle terminates the agent.
- **Needs override for social taps** – If any need deficit exceeds 0.85
  we skip social bonuses; this prevents runaway positive loops while an
  agent is close to collapse.

## 3. Telemetry & Testing

- RewardEngine exposes the full component breakdown via
  `TelemetryPublisher.latest_reward_breakdown()`; the payload now
  includes the `terminal_penalty` slot in addition to `survival`,
  `needs_penalty`, `social`, `wage`, `punctuality`, `clip_adjustment`,
  and `total`.
- Regression coverage lives in `tests/test_reward_engine.py`, with new
  fixtures exercising penalty application and clipping. Lifecycle tests
  (`tests/test_lifecycle_manager.py`) confirm termination reasons are
  recorded so the reward tap can distinguish faint vs. eviction.
- Sample telemetry (`docs/samples/telemetry_stream_sample.jsonl`) records
  the updated reward breakdown schema for consumer validation.

## 4. Operator Guidance

- Tune wage and punctuality taps together to maintain the intended daily
  return profile (~0.2 total reward per day in baseline configs). If
  adjustments push the total above the per-episode clip, increase the
  clip or dial back wages to preserve signal fidelity.
- Monitor `terminal_penalty` in rollouts to ensure faint/eviction rates
  match expectations. Spikes typically indicate lifecycle tuning or needs
  decay regressions.
- Whenever social reward stages change, capture fresh goldens so PPO
  drift suites can detect scaling regressions that sneak past guardrails.

## Ops Tooling

- Inspect reward breakdowns in telemetry snapshots with:
  `python scripts/reward_summary.py docs/samples/telemetry_stream_sample.jsonl`.
  The tool aggregates component means/min/max and surfaces top positive/negative
  agents so ops can spot anomalies quickly.
- Use `--agent alice --agent bob` to drill into specific citizens or
  `--format markdown` when pasting into runbooks. JSON output is available for
  automation integrations.
