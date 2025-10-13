# ADR 0003: DTO Boundary

## Status

Accepted

## Context

Following WP1 (Port and Factory Registry) and WP2 (World Modularisation), the simulation loop depends on well-defined port contracts (`WorldRuntime`, `PolicyBackend`, `TelemetrySink`). However, these ports still accept and return dictionary payloads (`Mapping[str, Any]`), which creates several problems:

1. **No compile-time guarantees** — Missing or mistyped keys fail at runtime deep in call stacks.
2. **Implicit schemas** — Consumers must reverse-engineer payload shapes from implementation code or tests.
3. **Validation gaps** — Dict-based payloads bypass Pydantic validation, allowing malformed data to propagate.
4. **Versioning opacity** — Schema changes are invisible; telemetry clients and policy backends must defensively handle arbitrary shapes.
5. **Testing friction** — Test fixtures require verbose dict construction without IDE completion or type checking.

WP3 introduces **typed DTO (Data Transfer Object) boundaries** using Pydantic v2 models to enforce schema contracts at module boundaries. DTOs replace dict-based payloads for observations, telemetry events, and rewards, providing type safety and validation without coupling consumers to internal implementation details.

## Decision

Implement the following DTO-based architecture:

### 1. Top-Level DTO Package

Create `townlet/dto/` as the canonical location for cross-module data contracts:

```
townlet/dto/
  __init__.py
  observations.py    # ObservationEnvelopeDTO, ObservationSnippetDTO, etc.
  telemetry.py       # TelemetryEventDTO, TelemetryMetadata
  rewards.py         # RewardBreakdownDTO, RewardComponentDTO
  world.py           # WorldGlobalContextDTO, QueueMetricsDTO, etc.
```

DTOs are defined using Pydantic v2 `BaseModel` with:
- **Strict typing** — All fields have explicit types; no `Any` unless semantically correct
- **Field validation** — Use Pydantic validators for constraints (ranges, non-empty strings, etc.)
- **Frozen models** — Mark DTOs as `frozen=True` where immutability is required
- **Aliasing** — Use `Field(alias=...)` for wire format compatibility when needed

### 2. Port Contracts Enforce DTOs

Update port protocols to accept/return DTOs instead of dicts:

```python
# townlet/ports/telemetry.py
from typing import Protocol
from townlet.dto.telemetry import TelemetryEventDTO

class TelemetrySink(Protocol):
    def emit_event(self, event: TelemetryEventDTO) -> None: ...
    def emit_metric(self, name: str, value: float, **tags: Any) -> None: ...
    ...
```

```python
# townlet/ports/policy.py
from typing import Protocol
from townlet.dto.observations import ObservationEnvelopeDTO

class PolicyBackend(Protocol):
    def decide(self, observations: ObservationEnvelopeDTO) -> Mapping[str, Any]: ...
    ...
```

```python
# townlet/ports/world.py
from typing import Protocol
from townlet.dto.observations import ObservationEnvelopeDTO

class WorldRuntime(Protocol):
    def observe(self) -> ObservationEnvelopeDTO: ...
    ...
```

### 3. Core DTO Models

**Telemetry Event DTO:**

```python
# townlet/dto/telemetry.py
from pydantic import BaseModel, Field

class TelemetryMetadata(BaseModel):
    schema_version: str = "0.9.7"
    timestamp: int | None = None
    source: str | None = None

class TelemetryEventDTO(BaseModel):
    event_type: str = Field(min_length=1)
    tick: int = Field(ge=0)
    payload: dict[str, Any]
    metadata: TelemetryMetadata = Field(default_factory=TelemetryMetadata)
```

**Observation Envelope DTO:**

```python
# townlet/dto/observations.py
from pydantic import BaseModel
from typing import Any

class ObservationEnvelopeDTO(BaseModel):
    tick: int
    agent_observations: dict[str, Any]
    global_context: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
```

**Reward Breakdown DTO:**

```python
# townlet/dto/rewards.py
from pydantic import BaseModel

class RewardComponentDTO(BaseModel):
    homeostasis: float
    shaping: float
    work: float
    social: float
    total: float

class RewardBreakdownDTO(BaseModel):
    tick: int
    rewards: dict[str, RewardComponentDTO]
    metadata: dict[str, Any] = Field(default_factory=dict)
```

### 4. Migration Strategy

The migration follows a phased approach:

**Phase 1 (WS3.1-3.2):** Create `townlet/dto/` and migrate observation DTOs from `world/dto/` to the top-level package.

**Phase 2 (WS3.3-3.4):** Update port protocols to enforce DTO types and update concrete implementations (`TelemetryPublisher`, `WorldObservationService`, `PolicyRuntime`).

**Phase 3 (WS3.5):** Convert telemetry pipeline call sites (sim loop, console, lifecycle, etc.) to construct and pass `TelemetryEventDTO` instead of calling `emit_event(name, payload)`.

**Phase 4 (Future):** Extend DTO boundaries to policy actions, world commands, and snapshot payloads.

### 5. Backward Compatibility

During migration, adapters may temporarily unpack DTOs into legacy dict shapes:

```python
# Inside an adapter
def emit_event(self, event: TelemetryEventDTO) -> None:
    # Unpack DTO for legacy dispatcher
    self._legacy_dispatcher.emit(event.event_type, event.payload)
```

New code must use DTOs exclusively; adapters contain the compatibility shims until legacy consumers are migrated.

### 6. Validation Policy

- **Construct-time validation** — Pydantic validates all fields when a DTO is instantiated; invalid data raises `ValidationError` immediately.
- **No silent coercion** — DTOs use strict types; passing a string where an int is expected fails validation.
- **Test helpers** — Provide factory functions in `tests/fixtures/dto_factories.py` for common DTO shapes to reduce test verbosity.

## Consequences

### Positive

- **Type safety** — IDEs provide completion and static analyzers catch type errors at development time.
- **Self-documenting schemas** — DTO definitions serve as executable specifications; field types and constraints are explicit.
- **Validation** — Malformed data is rejected at module boundaries before propagating through the system.
- **Versioning** — DTOs carry `schema_version` fields enabling compatibility checks and graceful degradation.
- **Testing clarity** — Test fixtures use typed constructors instead of verbose dicts; invalid test data fails immediately.
- **Decoupling** — Consumers depend on DTO contracts, not internal implementation classes.

### Negative

- **Breaking change** — Existing code calling ports with dicts must be updated to construct DTOs.
- **Migration effort** — ~50+ call sites across sim loop, telemetry, tests required updating.
- **Serialization overhead** — DTOs add Pydantic construction/validation cost (mitigated by caching and reuse).
- **Import weight** — Modules depending on DTOs must import Pydantic (already a core dependency).

### Mitigations

- **Adapters contain breakage** — Port implementations handle DTO unpacking; consumers outside adapters don't change.
- **Incremental rollout** — WP3 stages ensure each boundary (telemetry, observations, rewards) migrates independently.
- **Comprehensive tests** — 147 telemetry tests validate DTO integration end-to-end.

## Implementation Notes

### DTO Package Structure

- **Public API** — `townlet/dto/__init__.py` exports all DTO models for external consumption.
- **Internal imports** — Modules should import from `townlet.dto.<module>` directly to avoid circular dependencies.
- **No business logic** — DTOs are pure data containers; validation logic only, no domain methods.

### Conversion Pattern

Before (dict-based):
```python
telemetry.emit_event("loop.tick", {"tick": 5, "duration_ms": 12.3})
```

After (DTO-based):
```python
from townlet.dto.telemetry import TelemetryEventDTO, TelemetryMetadata

event = TelemetryEventDTO(
    event_type="loop.tick",
    tick=5,
    payload={"tick": 5, "duration_ms": 12.3},
    metadata=TelemetryMetadata(),
)
telemetry.emit_event(event)
```

### Test Fixture Helpers

Provide factory functions to reduce test boilerplate:

```python
# tests/fixtures/dto_factories.py
def make_telemetry_event(
    event_type: str = "test.event",
    tick: int = 0,
    payload: dict[str, Any] | None = None,
) -> TelemetryEventDTO:
    return TelemetryEventDTO(
        event_type=event_type,
        tick=tick,
        payload=payload or {},
        metadata=TelemetryMetadata(),
    )
```

### Snapshot Compatibility

Snapshots serializing DTOs use `model_dump()` to produce JSON-safe dicts:

```python
snapshot_data = observation_dto.model_dump(by_alias=True)
```

When restoring, construct DTOs from snapshot dicts:

```python
observation_dto = ObservationEnvelopeDTO(**snapshot_data)
```

## Migration Notes

### Files Modified

**Production code (9 files):**
- `src/townlet/ports/telemetry.py` — Protocol enforces `TelemetryEventDTO`
- `src/townlet/core/interfaces.py` — TelemetrySinkProtocol enforces `TelemetryEventDTO`
- `src/townlet/telemetry/publisher.py` — Unpacks DTO for internal dispatcher
- `src/townlet/testing/dummy_telemetry.py` — Test stub accepts DTO
- `src/townlet/adapters/telemetry_stdout.py` — Adapter forwards DTO
- `src/townlet/core/sim_loop.py` — Constructs DTOs for all telemetry events
- `src/townlet/orchestration/console.py` — Console router uses DTO
- `src/townlet/demo/runner.py` — Demo seeding uses DTO
- `src/townlet/snapshots/state.py` — Snapshot helpers use DTO

**Test files (~12 files):**
- Updated ~40+ `emit_event` call sites to construct `TelemetryEventDTO`

### Breaking Changes

- **Port signatures** — `TelemetrySink.emit_event(name, payload)` → `emit_event(event: TelemetryEventDTO)`
- **Observation builders** — Must return `ObservationEnvelopeDTO` instead of dict
- **Test fixtures** — Dict-based telemetry calls fail; must use DTO constructors

### Deprecation Path

No deprecation period provided. WP3 completes as an atomic migration; mixed dict/DTO usage is prohibited to maintain consistency.

### Verification

- ✅ All 147 telemetry tests passing with DTO boundaries
- ✅ Type checkers (mypy) validate DTO usage at static analysis time
- ✅ Integration tests confirm end-to-end DTO flow through ports

## Related Documents

- `docs/architecture_review/WP_TASKINGS/WP3.md` — WP3 implementation checklist
- `docs/architecture_review/ARCHITECTURE_REVIEW_2.md` — Architectural context for typed boundaries
- `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md` — Port contracts that DTOs enhance
- `src/townlet/dto/` — DTO package containing all cross-module data contracts
