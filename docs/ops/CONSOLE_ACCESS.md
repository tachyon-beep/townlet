# Console & Telemetry Access Control

Townlet supports token-based authentication for console commands and telemetry subscribers. When enabled, every command queued through `TelemetryPublisher.queue_console_command` must provide a valid token; roles (`viewer` or `admin`) are derived from the token configuration rather than client-provided metadata.

## Configuration

Add a `console_auth` section to your simulation configuration:

```yaml
console_auth:
  enabled: true
  require_auth_for_viewer: true
  tokens:
    - label: viewer-dashboard
      role: viewer
      token_env: TOWNLET_CONSOLE_VIEWER_TOKEN
    - label: release-admin
      role: admin
      token: "local-admin-token"
```

- `enabled`: toggles authentication. When false, Townlet now coerces every command to viewer mode, logs a warning at startup, and rejects admin-only handlers. Enable auth before issuing admin commands.
- `require_auth_for_viewer`: if true, even viewer commands must include a token. Set to false for transitional environments.
- `tokens`: list of static tokens. Define exactly one of `token` (literal string) or `token_env` (environment variable containing the token). `label` populates the command issuer field for auditing.

Missing or invalid tokens result in an immediate `unauthorized` console result and the command is not queued.

## Telemetry Transport Security

- TCP telemetry transports now default to TLS. When `type: tcp`, operators only need to set certificate paths (see `configs/demo/poc_demo_tls.yaml`) and the connection negotiates TLS automatically.
- Development plaintext requires three explicit opt-ins: set `enable_tls: false`, `allow_plaintext: true`, and `dev_allow_plaintext: true`, and point the endpoint at `localhost` or `127.0.0.1`. Any other host raises a configuration error.
- When plaintext is enabled, Townlet logs `telemetry_tcp_plaintext_enabled` and telemetry status exposes `allow_plaintext: true`. Treat this as temporary and prefer TLS even in staging.
- The default example config (`configs/examples/poc_hybrid.yaml`) uses stdout transport for local work; switch to TCP+TLS before deploying multi-host collectors.

## Client Expectations

When auth is enabled, clients must attach an `auth` block to each command payload:

```python
loop.telemetry.queue_console_command(
    {
        "name": "telemetry_snapshot",
        "auth": {"token": os.environ["TOWNLET_CONSOLE_VIEWER_TOKEN"]},
    }
)
```

Tokens are stripped before commands reach the simulation world; audit logs record the command name, `cmd_id`, and issuer label.


## Simulation Loop Health

- The simulation loop now records a `loop_failure` telemetry event whenever a tick raises an exception. Operators can inspect `telemetry.latest_health_status()` or subscribe to the event stream to capture failure details (tick, error summary, failure count). Enable automatic failure snapshots with `snapshot.capture_on_failure: true`; the failure payload and telemetry health status include the saved snapshot path.
- CLI or automation clients may register a failure handler via `SimulationLoop.register_failure_handler` to perform cleanup or trigger graceful shutdowns before exiting with a non-zero status. The default `scripts/run_simulation.py` entry point now surfaces the failure summary and exits with status 1 when a tick fails.
- Health payloads include the last tick duration, transporter queue depth, and whether telemetry workers are still alive, enabling dashboards to surface anomalies quickly.

## Operational Guidance

- Rotate tokens regularly and keep them out of version control. Use environment variables or secret stores for runtime injection.
- Ensure telemetry transports are encrypted (see `console_auth.require_auth_for_viewer` and WP-102) before exposing admin tokens over the network.
- Monitor `telemetry_snapshot["console_results"]` for `unauthorized` events to detect brute-force attempts.
