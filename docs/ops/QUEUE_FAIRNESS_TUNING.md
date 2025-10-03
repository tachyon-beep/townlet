# Queue Fairness Tuning

Townlet enforces fairness at interactive stations through three primary knobs:

- `queue_fairness.cooldown_ticks`: number of ticks an agent is barred from re-entering a queue
  after a successful interaction. Default `60` ticks prevents the same agent from monopolising a
  bottleneck.
- `queue_fairness.ghost_step_after`: count of consecutive blocked attempts before the head of the
  queue ghost-steps (temporarily yields) so the next agent can proceed. Default `3` keeps queues
  moving without over-penalising legitimate holds.
- `queue_fairness.age_priority_weight`: small bonus in `_assign_next` that favours agents waiting
  longer. Default `0.1` reduces starvation without disrupting deterministic ordering.

### Operational Guidance
- Bump `cooldown_ticks` if operators observe repeated back-to-back usage; lower it when throughput
  matters more than fairness.
- Decrease `ghost_step_after` to flush deadlocks quickly; increase if ghost steps trigger too often
  in high-traffic areas.
- Tune `age_priority_weight` cautiously; large values can destabilise deterministic pathing.

### References
- `src/townlet/world/queue_manager.py` for implementation details.
- `tests/test_queue_metrics.py` exercises ghost-step/rotation counters to ensure telemetry remains
  trustworthy.
