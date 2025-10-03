# Web Observer Security Baseline

This checklist captures the minimum security posture required before exposing the web observer in shared demo environments.

## Authentication & Authorization
- Require authenticated sessions for operator console; spectator view can remain public but should use signed, cache-friendly URLs.
- Support SSO via OAuth 2.0 / OIDC provider (e.g., Auth0, Okta) with audience-scoped tokens.
- Enforce short-lived access tokens and refresh via secure cookies (SameSite=strict, Secure flag).

## Transport & Network
- Terminate TLS at the telemetry gateway; reject plaintext WebSocket upgrades.
- Rate-limit connection attempts per IP and enforce idle timeouts.
- Isolate telemetry gateway behind reverse proxy (NGINX/Envoy) with WAF rules for WebSocket.

## Session & Command Safety
- Prefix privileged channels (command dispatch) with signed capability tokens tied to operator role.
- Validate all incoming command payloads server-side using existing console schema.
- Log and audit every operator action (agent id, command, timestamp, result).

## Data Protection
- Never expose raw secrets/policy hashes in the browser; redact sensitive fields server-side.
- Compress and cache read-only spectator payloads but disable caching for operator state.

## Monitoring & Alerting
- Emit authentication metrics (logins, failures) and WebSocket error rates to telemetry/observability stack.
- Implement anomaly alerts for command bursts, auth failures, or excessive message sizes.

## Compliance Checklist
- [ ] Security baseline reviewed with ops/security stakeholder.
- [ ] OAuth client registered and dev credentials stored in secrets manager.
- [ ] Gateway deployment template includes TLS cert/config automation.
- [ ] Logging pipeline redacts tokens and PII.

Track updates to this baseline in the web UI roadmap and revisit before each milestone release.
