# Golden Rollout Scenario Catalog

Milestone **M7** tracks five deterministic rollout scenarios that serve as
regression baselines for capture, PPO replay, and telemetry drift tests. The
metrics for each scenario are stored in `docs/samples/rollout_scenario_stats.json`
(grouped by scenario name). The capture suite (`scripts/capture_rollout_suite.py`)
produces per-agent replay samples whose metrics should match the values below.

| Scenario | Config | Description | Key Metrics |
| --- | --- | --- | --- |
| `kitchen_breakfast` | `configs/scenarios/kitchen_breakfast.yaml` | Two agents alternate cooking breakfast without queue contention. Exercises hot/cold affordance flow and verifies neutral reward totals. | `timesteps=40`, `reward_sum=-8.0`, `rivalry_max_mean=0.0` |
| `queue_conflict` | `configs/scenarios/queue_conflict.yaml` | Three agents contest a single shower to trigger queue rotation, ghost-steps, and rivalry deltas. | `timesteps=80`, `reward_sum=-16.0`, `rivalry_max_mean≈0.858`, `rivalry_avoid_count_max≥1` |
| `employment_punctuality` | `configs/scenarios/employment_punctuality.yaml` | Tracks lateness and employment telemetry for the morning commute scenario. | `lateness_mean≈0.8875`, `reward_sum=-16.0`, `rivalry_max_mean≈0.852` |
| `rivalry_decay` | `configs/scenarios/rivalry_decay.yaml` | Two agents with pre-existing rivalry decaying over 50 ticks; ensures decay and avoid counts remain stable. | `reward_sum=-10.0`, `rivalry_max_mean≈0.807`, `rivalry_avoid_count_mean≈0.86` |
| `observation_baseline` | `configs/scenarios/observation_baseline.yaml` | Minimal wait-only scenario used to sanity-check observation tensors. | `timesteps=20`, `reward_sum=-4.0`, zero rivalry/queue activity |

Each scenario includes a deterministic tick count (`scenario.ticks`) and scripted
agent schedules. Capture metadata records the config id, scenario description,
policy hash, and capture timestamp so diffs can be audited. Update this catalog
whenever new golden scenarios are added or existing ones change behaviour.
