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

## Observer UI — Promotion Gate Review
- [ ] Run `scripts/observer_ui.py configs/examples/poc_hybrid.yaml --ticks 10 --refresh 0.0` and confirm the Promotion Gate panel renders `State`, `Pass streak`, `Required passes`, and `Reason` rows.
- [ ] While the system is idling (no evaluations yet), verify the reason reads "Awaiting first evaluation." and the border colour stays blue.
- [ ] Trigger an anneal rehearsal (e.g., `python scripts/run_anneal_rehearsal.py --config configs/examples/base.yml --exit-on-failure`) and rerun the dashboard; when a HOLD/FAIL occurs the reason surfaces the flagged drift (loss/queue/intensity) or a generic evaluation failure message with a yellow/red border.
- [ ] After a successful rehearsal, confirm the panel reports "Candidate ready" with a green border and the candidate metadata row lists the evaluation mode/cycle.
- [ ] Inspect the Promotion History table (latest three events) to ensure promote/rollback events log their metadata for operators.
