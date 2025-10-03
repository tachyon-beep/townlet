# QA Checklist — Observation Context Resets

## Observation Builder
- [ ] Confirm hybrid/full/compact variants include needs, queue flags, and lifecycle
      indicators (`need_*`, `reservation_active`, `in_queue`, `ctx_reset_flag`).
- [ ] Force agent termination (e.g., via `kill` console command) and verify
      `ctx_reset_flag == 1.0` for the terminated agent in the next observation batch.
- [ ] Issue `teleport` console command and confirm the teleported agent’s
      `ctx_reset_flag` is set for the following tick.
- [ ] Acquire possession via `console possess --payload '{"agent_id": "alice"}'` and verify
      the possessed agent surfaces `ctx_reset_flag == 1.0`; release possession and
      confirm the flag returns to `0.0` on subsequent ticks.
- [ ] Ensure embedding allocator releases slots only on termination; possession/teleport
      should preserve slot assignment while toggling the reset flag.

QA engineers should capture observation batches using `scripts/run_simulation.py` with
`--capture-observations` (when available) or directly through test helpers in
`tests/test_observation_builder.py` to validate the contract above.

## CLI Smoke Coverage
- [ ] Run `pytest tests/test_run_simulation_cli.py` to verify the simulation CLI and
      `SimulationLoop.run_for` helper execute bounded ticks.
- [ ] Run `pytest tests/test_demo_run_cli.py` to confirm the scripted demo renders without
      stdout telemetry noise.
- [ ] Run `pytest tests/test_observer_ui_cli.py` to exercise the observer dashboard entry point.

## Observer UI — Promotion Gate Review
- [ ] Run `scripts/observer_ui.py configs/examples/poc_hybrid.yaml --ticks 10 --refresh 0.0` and confirm the Promotion Gate panel renders `State`, `Pass streak`, `Required passes`, and `Reason` rows.
- [ ] While the system is idling (no evaluations yet), verify the reason reads "Awaiting first evaluation." and the border colour stays blue.
- [ ] Trigger an anneal rehearsal (e.g., `python scripts/run_anneal_rehearsal.py --config configs/examples/base.yml --exit-on-failure`) and rerun the dashboard; when a HOLD/FAIL occurs the reason surfaces the flagged drift (loss/queue/intensity) or a generic evaluation failure message with a yellow/red border.
- [ ] After a successful rehearsal, confirm the panel reports "Candidate ready" with a green border and the candidate metadata row lists the evaluation mode/cycle.
- [ ] Inspect the Promotion History table (latest three events) to ensure promote/rollback events log their metadata for operators.

## Observation Fixture Maintenance
- [ ] Regenerate the social snippet golden whenever the observation builder changes:
  ```bash
  PYTHONPATH=src python - <<'PY'
  from pathlib import Path
  import numpy as np
  from townlet.config import load_config
  from townlet.observations.builder import ObservationBuilder
  from townlet.world.grid import AgentSnapshot, WorldState

  config = load_config(Path("configs/examples/poc_hybrid.yaml"))
  world = WorldState.from_config(config)
  world.agents["alice"] = AgentSnapshot(
      agent_id="alice",
      position=(0, 0),
      needs={"hunger": 0.4, "hygiene": 0.5, "energy": 0.6},
      wallet=5.0,
  )
  world.agents["bob"] = AgentSnapshot(
      agent_id="bob",
      position=(1, 0),
      needs={"hunger": 0.3, "hygiene": 0.2, "energy": 0.7},
      wallet=3.0,
  )
  world.register_rivalry_conflict("alice", "bob")
  world.update_relationship("alice", "bob", trust=0.6, familiarity=0.3)

  builder = ObservationBuilder(config)
  obs = builder.build_batch(world, terminated={})["alice"]
  np.savez(
      "tests/data/observations/social_snippet_gold.npz",
      features=obs["features"],
      names=np.array(builder._feature_names, dtype=object),
  )
  PY
  ```
- [ ] Commit the refreshed `tests/data/observations/social_snippet_gold.npz` alongside observation builder changes so `tests/test_observations_social_snippet.py` stays in sync.
