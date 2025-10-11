# PB-A – WorldRuntime Port Contract (2025-10-11)

This note captures the revised `WorldRuntime` port surface we agreed to adopt
as part of the PB (Port Boundary) cleanup workstream. It removes legacy hooks,
clarifies the DTO-only data flow, and serves as the reference for the
subsequent PB-B/C/D implementation tasks.

## Target Contract

```python
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

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
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
- No direct observation-builder hooks remain; `observe()` is expected to return
  the DTO-structured mapping created by `WorldContext.observe`.
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
