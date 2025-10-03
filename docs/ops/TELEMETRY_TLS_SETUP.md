# Telemetry TLS Setup Guide

This guide walks through enabling TLS for Townlet telemetry transports.

## 1. Prepare Certificates
- Issue or provision a server certificate/key pair for the telemetry collector.
- (Optional) Issue client certificates when mutual authentication is required.
- Distribute the CA bundle (`certs/<env>_ca.pem`) to all shards.
  The repository ignores the `certs/` directory by default; manage material per environment.

## 2. Update Simulation Config
Set the telemetry transport to TCP with TLS enabled:

```yaml
telemetry:
  transport:
    type: tcp
    endpoint: collector.internal:9100
    enable_tls: true
    verify_hostname: true
    ca_file: certs/internal_ca.pem
    cert_file: certs/shard_client.pem        # omit when client auth not needed
    key_file: certs/shard_client.key         # omit when client auth not needed
    allow_plaintext: false                   # required; keeps plaintext disabled
```

If you must run without TLS in a lab environment, set `allow_plaintext: true` to
acknowledge the risk. The shard will log a `telemetry_tcp_plaintext_enabled`
warning each time the transport initialises.

## 3. Validate Before Deployment
1. Run `openssl s_client -connect collector.internal:9100 -servername collector.internal`
   from a shard host to confirm the certificate chain and hostname validation.
2. Execute `pytest tests/test_telemetry_transport.py` locally to cover the TLS
   transport code paths.
3. Capture a telemetry payload with the new configuration and archive it under
   `docs/samples/` if downstream consumers rely on schema diffs.

## 4. Monitor After Rollout
- Watch shard logs for `SSL:` failures or reconnect loops.
- Inspect the telemetry header panel (Rich dashboard) to ensure
  `transport.connected` is true and `transport.tls_enabled` is surfaced in the
  JSON snapshot.
- Rotate certificates ahead of expiry; update configs and redeploy following the
  checklist once new material is available.

## 5. Incident Response
- If TLS negotiation fails in production, switch the config back to a local file
  transport (or enable `allow_plaintext: true` as a last resort) and redeploy.
- Document the incident in `ops/rollouts.md`, including certificate fingerprints
  and remediation steps, then restore TLS as soon as possible.
