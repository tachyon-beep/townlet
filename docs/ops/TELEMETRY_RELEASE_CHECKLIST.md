# Telemetry Transport Release Checklist

Use this checklist whenever enabling or modifying the telemetry transport in staging or production.

## Preconditions
- [ ] Confirm `config.telemetry.transport` matches the target environment (stdout for dev, file/tcp for shared observers).
- [ ] Ensure transport credentials/endpoints (for tcp) are provisioned in the deployment environment.
- [ ] Verify buffer limits (`transport.buffer.max_batch_size`, `transport.buffer.max_buffer_bytes`) align with expected tick cadence.

## Deployment Steps
1. Update the configuration repository with the transport changes.
2. Run the smoke suite locally (or in CI) before rollout:
   ```bash
   pytest tests/test_telemetry_client.py tests/test_observer_ui_dashboard.py           tests/test_telemetry_stream_smoke.py tests/test_telemetry_transport.py
   ```
3. Capture a fresh payload sample from the target transport (e.g., tail the file sink or TCP consumer) and archive it under `docs/samples/` if the schema changes.
4. Deploy the configuration (feature flag or config service update).

## Post-Deployment Verification
- [ ] Execute `telemetry_snapshot` via the console; confirm `transport.connected` is true, `dropped_messages` is zero, and `last_error` is empty.
- [ ] Review the observer dashboard header transport panel for the same status.
- [ ] Tail shard logs for transport retry warnings for 5–10 minutes.
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
