# Security Policy

## Supported Versions

Townlet is pre-release software. Security updates are provided on the `main`
branch until formal releases begin. Production deployments should pin to a
commit hash and track upstream changes closely.

## Reporting a Vulnerability

Please disclose vulnerabilities via security@townlet.dev. Include:

- A description of the issue and its impact
- Steps to reproduce, including configuration details
- Suggested mitigations if known

We aim to acknowledge reports within three business days and provide status
updates weekly until resolution. Once a fix is available we will credit the
reporter (if desired) and document the remediation path.

## Affordance Hook Security

Townlet allows projects to extend the simulation via affordance hook modules.
These modules run with full process privileges, so only trusted code should be
loaded. The runtime now enforces the following guardrails:

- A hook allowlist must be declared in configuration (`affordances.runtime
  .hook_allowlist`). Only modules in this list (or the built-in
  `townlet.world.hooks.default`) will be imported.
- Environment overrides via `TOWNLET_AFFORDANCE_HOOK_MODULES` are optional and
  gated by `affordances.runtime.allow_env_hooks`. Disable this flag in
  production to prevent operator error or environment tampering.
- Invalid modules (missing imports or `register_hooks`) are rejected with clear
  logging so operators can audit attempted injections.

**Operational guidance**

1. Add all approved hook modules to the configuration allowlist. Ship the list
   with your deployment artifact so it is version controlled.
2. For shared or cloud deployments, set `allow_env_hooks: false` to ensure
   runtime state cannot be altered by environment variables.
3. Monitor logs for `affordance_hook_rejected` entries; unexpected rejections
   may indicate tampering or misconfiguration.
4. Document any third-party hook packages as part of your threat model. Because
   hooks execute arbitrary Python, they should be reviewed like any code
   running inside the simulation container.

## Telemetry Transport Security

Townlet shards now require deliberate acknowledgement before emitting telemetry
over plaintext TCP. The transport config adds TLS controls:

- Enable TLS with `telemetry.transport.enable_tls: true`. Provide certificates
  via `ca_file`, `cert_file`, and `key_file` when mutual auth is required.
- Hostname verification is on by default; set `verify_hostname: false` only for
  trusted lab environments with pinned certificates.
- Plaintext TCP is disabled unless you set `telemetry.transport.allow_plaintext:
  true`. This flag is intended for legacy tooling and should not be used in
  multi-tenant or internet-facing deployments.
- All plaintext runs log a warning (`telemetry_tcp_plaintext_enabled`); treat it
  as an alert that hardening is incomplete.

Operational checklist:

1. Issue certificates for telemetry collectors and distribute CA bundles to
   shards. Store secrets via environment-specific tooling (e.g., Vault or
   Kubernetes secrets).
2. Configure endpoints in `configs/<env>/` with TLS enabled and hostname
   verification intact.
3. Run the telemetry release checklist before rollout to confirm the secure
   transport negotiates successfully.
4. Avoid sharing demo configs that set `allow_plaintext: true` unless the target
   environment is fully trusted.

## Observation Privacy & Social Data

Townlet observations can include per-agent social snippets (hashed identity
embeddings plus trust/familiarity/rivalry metrics). Treat these fields as
sensitive telemetry:

- Disable social observations entirely by keeping
  `features.stages.relationships: "OFF"` or setting
  `observations.social_snippet.top_friends = top_rivals = 0` when scenarios do
  not require social context. The observation builder now records the chosen
  configuration in `metadata.social_context` so downstream tools can verify the
  expected posture.
- If social snippets are required, ensure the output is scoped to trusted
  analytics paths (e.g., replay artifacts, telemetry dashboards). The hashed
  embeddings are not reversible, but the surrounding metrics can reveal agent
  interactions and should be shielded from untrusted parties.
- Operators must refresh replay datasets and downstream tooling after upgrading
  to this release so the new metadata (variant, map channels, social context)
  stays aligned across training pipelines.
