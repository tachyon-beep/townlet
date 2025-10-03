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

## Operational Guidance

- Rotate tokens regularly and keep them out of version control. Use environment variables or secret stores for runtime injection.
- Ensure telemetry transports are encrypted (see `console_auth.require_auth_for_viewer` and WP-102) before exposing admin tokens over the network.
- Monitor `telemetry_snapshot["console_results"]` for `unauthorized` events to detect brute-force attempts.
