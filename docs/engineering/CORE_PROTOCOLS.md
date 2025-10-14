# Core Simulation Interfaces

Townlet’s composition root depends on behaviour contracts instead of concrete classes.
The canonical protocol definitions live in `src/townlet/core/interfaces.py`, while the
world-runtime boundary is exported directly from `src/townlet/ports/world.py`. Import
paths to use:

- `townlet.ports.world.WorldRuntime` (structural protocol, runtime-checkable)
- `townlet.core.PolicyBackendProtocol`
- `townlet.core.TelemetrySinkProtocol`

Existing implementations (`WorldRuntime` facade, `PolicyRuntime`, `TelemetryPublisher`)
conform to these contracts; `tests/test_core_protocols.py` and
`tests/test_ports_surface.py` guard the surface. Provider registries exposed via
`townlet.core.resolve_*` now return port instances while allowing additional
implementations to register themselves. New factories and adapters should type against
these interfaces, importing them from the paths above, to stay aligned with the
target architecture in `docs/architecture_review/townlet-target-architecture.md`.

Configuration files select providers via the `runtime` block on `SimulationConfig`, with
optional keyword arguments forwarded to the registered factory. When the block is
omitted, defaults (`world: default`, `policy: scripted`, `telemetry: stdout`) apply.

Built-in fallback providers (`policy.stub`, `policy.pytorch`, `telemetry.stub`, `telemetry.http`) automatically degrade to stub implementations when optional dependencies such as PyTorch or `httpx` are absent. The stubs log structured warnings so operators know that reduced capability is active.

The `townlet.policy` package exposes `resolve_policy_backend(provider="scripted", **kwargs)` and a `DEFAULT_POLICY_PROVIDER` constant as convenience wrappers around the registry. Legacy `PolicyRuntime` remains available but new consumers should prefer the resolver and protocol interfaces to stay aligned with the modular architecture.

Training CLIs use `PolicyTrainingOrchestrator` to detect stub backends and emit warnings like `capture_rollout_stub_policy` during rollout capture, ensuring reduced capability is visible in automated runs. Dashboard helpers accept explicit provider names so UI callers can surface the same metadata.

Future refactors (WP-B onward) should extend these contracts rather than re-introducing direct dependencies on concrete classes.
