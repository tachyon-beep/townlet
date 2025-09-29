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
