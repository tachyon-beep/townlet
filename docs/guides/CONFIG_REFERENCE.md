# Configuration Reference Highlights

This note complements the docstrings recorded in `src/townlet/config/loader.py`
and calls out the most frequently tuned sections in YAML configs.

## Feature Flags

- `features.stages` (see `StageFlags` docstring) controls high-level product
  milestones such as relationship staging and social rewards.
- `features.systems` toggles entire runtime subsystems – set
  `observations: compact` to opt into the compact observation variant.
- `features.training.curiosity` gates curiosity-style intrinsic reward phases.

## Policy Runtime

- `policy_runtime.option_commit_ticks` defines how long options remain committed
  before a policy can select a new one.

## Reward Surface

- `rewards.needs_weights`, `rewards.social`, and `rewards.clip` each have
  docstrings documenting typical ranges and validation rules.
- Shaping and curiosity settings (`ShapingConfig`, `CuriosityConfig`) affect
  intrinsic rewards; refer to their docstrings when tweaking anneal behaviour.

## Observations

- `observations.hybrid` / `observations.compact` docstrings capture the
  validation rules enforced by the observation builder (window sizes must be
  odd, optional target channels, etc.).
- `observations.social_snippet` explains how many friends/rivals are encoded and
  when aggregates are disabled.

## Stability Guardrails

- Canary configs (`StarvationCanaryConfig`, `RewardVarianceCanaryConfig`,
  `OptionThrashCanaryConfig`) describe the thresholds used to trigger alerts.
- `promotion` (PromotionGateConfig) captures how many passes are required before
  a policy is eligible for promotion.

For additional detail invoke:

```bash
python scripts/check_docstrings.py src/townlet/config/loader.py --summary-only
python -m interrogate -c pyproject.toml src/townlet/config/loader.py
```
