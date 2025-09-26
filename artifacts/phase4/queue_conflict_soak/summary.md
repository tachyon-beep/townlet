### PPO Telemetry Summary

- Epochs analysed: **1**
- Data mode: **rollout** (cycle `5.0`)
- Latest metrics: `loss_total=1.242929`, `kl_divergence=0.033680`, `grad_norm=2.019006`, `entropy_mean=1.384887`, `reward_adv_corr=0.000000`
- Epoch duration: `0.0157s`, roll-out ticks: `40`
- Queue conflicts: `32.0` events (intensity sum `52.75`)

| Metric | Min | Max |
| --- | --- | --- |
| loss_total | 1.242929 | 1.534439 |
| kl_divergence | 0.002583 | 0.033680 |
| grad_norm | 1.268185 | 2.019006 |
| queue_conflict_events | 0.0 | 32.0 |

#### Baseline Drift

| Key | Delta | Percent |
| --- | --- | --- |
| epoch | +0.000000 | +0.00% |
| updates | -4.000000 | -33.33% |
| transitions | +0.000000 | +0.00% |
| loss_policy | -0.003472 | +69.61% |
| loss_value | +0.197781 | +8.48% |
| loss_entropy | +0.001399 | +0.10% |
| loss_total | +0.095404 | +8.31% |
| clip_fraction | +0.000000 | +0.00% |
| adv_mean | -0.000000 | -2967.19% |
| adv_std | -0.013172 | -1.35% |
| grad_norm | +0.672766 | +49.97% |
| kl_divergence | +0.019793 | +142.53% |
| telemetry_version | +0.000000 | +0.00% |
| lr | +0.000000 | +0.00% |
| steps | +1500.000000 | +500.00% |
| epoch_duration_sec | -0.003948 | -20.14% |
| cycle_id | +5.000000 | n/a |
| batch_entropy_mean | +0.001399 | +0.10% |
| batch_entropy_std | -0.000012 | -8.42% |
| grad_norm_max | +0.093385 | +3.89% |
| kl_divergence_max | -0.012765 | -18.70% |
| reward_advantage_corr | +0.000000 | n/a |
| rollout_ticks | +0.000000 | +0.00% |
| log_stream_offset | +10.000000 | +500.00% |
| queue_conflict_events | +0.000000 | +0.00% |
| queue_conflict_intensity_sum | +0.000000 | +0.00% |
| baseline_sample_count | +0.000000 | +0.00% |
| baseline_reward_mean | +0.000000 | -0.00% |
| baseline_reward_sum | +0.000000 | -0.00% |
| baseline_reward_sum_mean | +0.000000 | -0.00% |
| baseline_log_prob_mean | +0.000000 | -0.00% |
| conflict.rivalry_max_mean_avg | +0.005844 | +0.71% |
| conflict.rivalry_max_max_avg | +0.000000 | +0.00% |
| conflict.rivalry_avoid_count_mean_avg | -0.068750 | -5.98% |
| conflict.rivalry_avoid_count_max_avg | +0.166667 | +12.50% |
