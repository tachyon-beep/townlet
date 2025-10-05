# Core Simulation Interfaces

The target architecture calls for the simulation loop to depend on behaviour contracts rather than concrete implementations. The following protocols live in `src/townlet/core/interfaces.py` and are exported via `townlet.core`:

- `WorldRuntimeProtocol`: advancing tick state, queueing console input, and exposing per-tick artefacts.
- `PolicyBackendProtocol`: scripted/learned policy bridge offering `decide`, `post_step`, and policy metadata accessors.
- `TelemetrySinkProtocol`: tick publication, console ingestion, health reporting, and snapshot import/export hooks.

Existing implementations (`WorldRuntime`, `PolicyRuntime`, `TelemetryPublisher`) conform to these protocols; `tests/test_core_protocols.py` guards that contract. Provider registries exposed via `townlet.core.resolve_*` now return protocol instances while allowing additional implementations to register themselves. New factories and adapters should type against the protocols, importing them from `townlet.core` rather than the concrete modules. This keeps downstream code aligned with the target architecture outlined in `docs/architecture_review/townlet-target-architecture.md`.

Configuration files can select providers via the `runtime` block on `SimulationConfig`, with optional keyword arguments forwarded to the registered factory. When the block is omitted, defaults (`world: default`, `policy: scripted`, `telemetry: stdout`) are applied automatically.

Built-in fallback providers (`policy.stub`, `policy.pytorch`, `telemetry.stub`, `telemetry.http`) automatically degrade to stub implementations when optional dependencies such as PyTorch or `httpx` are absent. The stubs log structured warnings so operators know that reduced capability is active.

Future refactors (WP-B onward) should extend these contracts rather than re-introducing direct dependencies on concrete classes.
