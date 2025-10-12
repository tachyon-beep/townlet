# PB-A – WorldRuntime Port Contract (2025-10-11)

This note captures the revised `WorldRuntime` port surface we agreed to adopt
as part of the PB (Port Boundary) cleanup workstream. It removes legacy hooks,
clarifies the DTO-only data flow, and serves as the reference for the
subsequent PB-B/C/D implementation tasks.

## Target Contract

```python
from townlet.world.dto.observation import ObservationEnvelope


@runtime_checkable
class WorldRuntime(Protocol):
    """Minimal contract for advancing the modular world."""

    def bind_world(self, world: "WorldState") -> None:
        ...

    def bind_world_adapter(self, adapter: "WorldRuntimeAdapter") -> None:
        ...

    def reset(self, seed: int | None = None) -> None:
        ...

    def tick(
        self,
        *,
        tick: int,
        console_operations: Iterable[ConsoleCommandEnvelope] | None = None,
        action_provider: Callable[["WorldState", int], Mapping[str, Any]] | None = None,
        policy_actions: Mapping[str, Any] | None = None,
    ) -> RuntimeStepResult:
        ...

    def agents(self) -> Iterable[str]:
        ...

    def observe(self, agent_ids: Iterable[str] | None = None) -> ObservationEnvelope:
        ...

    def apply_actions(self, actions: Mapping[str, Any]) -> None:
        ...

    def snapshot(
        self,
        *,
        config: Any | None = None,
        telemetry: "TelemetrySinkProtocol" | None = None,
        stability: Any | None = None,
        promotion: Any | None = None,
        rng_streams: Mapping[str, Any] | None = None,
        identity: Mapping[str, Any] | None = None,
    ) -> SnapshotState:
        ...
```

### Notable changes

- `queue_console()` has been removed. Console ingestion is now routed purely
  through `ConsoleRouter.enqueue` → `SimulationLoop.runtime.tick(console_operations=...)`.
- `observe()` now returns the DTO `ObservationEnvelope` produced by
  `WorldContext.observe`, aligning the port with Stage 6 DTO-only policy paths.
- The contract still accepts an `action_provider` that references `WorldState`;
  PB-C/D will introduce the DTO-only alternative once policy adapters finish the
  migration in WP3 Stage 6.

## Rationale

- Removing `queue_console` untangles the port from telemetry input handling and
  allows us to delete the legacy buffering in adapters/dummies.
- Keeping `bind_world`/`bind_world_adapter` temporarily preserves the existing
  swap-in behaviour used by the loop tests; we can deprecate them after the
  final composition-root refactor.
- This contract matches the implementation state after S5.D (console cleanup) –
  the code already behaves this way, so PB-A is pure documentation that locks in
  the agreed API.

## Next Steps

- PB-B/C will update adapters/dummy runtimes to expose helper aliases (if
  needed) and ensure they comply with the contract above.
- PB-D/E will enforce usage of `townlet.ports.world.WorldRuntime` across the loop
  and add guard tests to prevent regressions.
- PB-F will trim the deprecated members from `core/interfaces.py` once the new
  imports are in place.

## Registry & Provider Metadata (2025-10-11)

- The registry smoke `tests/test_factory_registry.py::test_simulation_loop_provider_metadata`
  now asserts that `SimulationLoop.provider_info` reflects the active world,
  policy, and telemetry providers, and that `policy_provider_name` /
  `telemetry_provider_name` pull from that mapping.
- The existing stub-path test (`test_simulation_loop_uses_registered_providers`)
  was extended to prove that the `is_stub_policy` / `is_stub_telemetry` helpers
  still infer stub status once the providers are registered through the factory
  registry.
- These checks give us early warning if future refactors drop provider metadata
  or bypass the registry. Keep them aligned with any changes to port resolution.
