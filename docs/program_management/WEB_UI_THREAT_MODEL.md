# Web Observer Threat Model

The following table maps high-level threats to mitigations we will implement throughout FWP-07.

| Threat | Vector | Impact | Mitigation |
|--------|--------|--------|------------|
| Unauthorized operator access | Compromised share-link, missing auth | Command execution on live sim | OAuth-based login, role-scoped tokens, short session TTLs |
| WebSocket hijacking | Man-in-the-middle, unencrypted WS | Data tampering, command injection | Mandatory TLS, origin checks, signed capability token per command channel |
| Replay of diff payloads | Cache poisoning/proxy replay | Out-of-order state, UI corruption | Tick monotonicity checks, payload nonce, discard stale diffs |
| XSS in telemetry data | Unescaped strings (narrations, console logs) | Credential theft, UI compromise | Encode all Rich text server-side, sanitize before DOM insertion, Content Security Policy |
| DoS via flood clients | Multiple spectator tabs or bots | Gateway resource exhaustion | Connection quotas per IP, adaptive throttling, observability alerts |
| Command abuse | Malicious operator or script | Simulation integrity loss | Audit logging, two-person approval for critical commands, rate limiting |
| Config/secret leakage | Dumped config via API | Exposure of tokens/endpoints | Server-side filtering, dedicated allowlist for spectator fields |

## Mitigation Tasks (Milestone 0)
- Document auth requirements and threat mitigations (see security baseline).
- Add schema-level checks to ensure tick ordering and monotonic diffs.
- Define sanitization/injection policy for string fields (Rich -> plain text).

Risks and mitigations should be revisited at each milestone’s retro.
