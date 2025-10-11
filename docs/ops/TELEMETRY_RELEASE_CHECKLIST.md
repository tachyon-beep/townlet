# Telemetry Transport Release Checklist

Use this checklist whenever enabling or modifying the telemetry transport in staging or production. For TLS-specific steps, see `docs/ops/TELEMETRY_TLS_SETUP.md`.

## Preconditions
- [ ] Confirm `config.telemetry.transport` matches the target environment (stdout for dev, file/tcp for shared observers).
- [ ] Ensure transport credentials/endpoints (for tcp) are provisioned in the deployment environment.
- [ ] Provision TLS material when using tcp (TLS is enabled by default; provide CA/cert/key paths as needed). Plaintext requires `allow_plaintext: true`, `dev_allow_plaintext: true`, a localhost endpoint, and VP approval.
- [ ] Verify buffer limits (`transport.buffer.max_batch_size`, `transport.buffer.max_buffer_bytes`) align with expected tick cadence.

## Deployment Steps
1. Update the configuration repository with the transport changes.
2. Run the smoke suite locally (or in CI) before rollout:
   ```bash
   pytest tests/test_telemetry_client.py tests/test_observer_ui_dashboard.py           tests/test_telemetry_stream_smoke.py tests/test_telemetry_transport.py
   ```
3. For TLS endpoints, run `openssl s_client -connect <host:port> -servername <host>` (or equivalent) to confirm certificates and hostname verification succeed before touching production shards.
4. Capture a fresh payload sample from the target transport (e.g., tail the file sink or TCP/TLS consumer) and archive it under `docs/samples/` if the schema changes.
5. Deploy the configuration (feature flag or config service update).

## Post-Deployment Verification
- [ ] Execute `telemetry_snapshot` via the console; confirm `transport.connected` is true, `dropped_messages` is zero, and `last_error` is empty.
- [ ] Verify the telemetry worker block reports `worker_alive: true` and `worker_error: null`; if the worker is down, escalate before continuing rollout.
- [ ] Review the observer dashboard header transport panel for the same status.
- [ ] Tail shard logs for transport retry warnings for 5–10 minutes.
- [ ] For TLS, confirm no `SSL:` errors are emitted and the console snapshot reports `transport.tls_enabled: true` (see telemetry health panel).
- [ ] Run the smoke suite against the live environment if a staging shard is accessible.

## Rollback Plan
- [ ] Switch `transport.type` back to `stdout` (or previous known-good setting) and redeploy.
- [ ] Clear/rotate file sinks if disk pressure caused the failure.
- [ ] Document the incident in `ops/rollouts.md`, including console snapshot status and errors.

## Artefact Checklist
- Updated config diff
- Smoke test output
- Console snapshot JSON (with transport block)
- Observer dashboard screenshot (transport panel)
- `docs/samples/telemetry_stream_sample.jsonl` refresh (if schema fields changed)

### DTO-Only Telemetry Rollout Notes (2025-10-11)
- DTO schema v0.2.0 parity confirmed (`pytest tests/core/test_sim_loop_dto_parity.py tests/policy/test_dto_ml_smoke.py tests/world/test_world_context_parity.py -q`).
- Health/failure payloads include `summary` metrics; ensure dashboards parse the new structure (see docs/design/WEB_TELEMETRY_SCHEMA.md).
- Notify analytics/ML teams with `docs/architecture_review/WP_NOTES/WP3/dto_migration.md` summary and sample payloads.
