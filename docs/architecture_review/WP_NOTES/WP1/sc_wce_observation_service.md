# Observation Service Sketch (WC-E Prep2) – 2025-10-10

Goal: provide a dedicated component that `WorldContext` can depend on for observation assembly so DTO envelopes are produced without the simulation loop.

## Proposed Interface
```python
from typing import Iterable
from townlet.world.dto.observation import ObservationEnvelope

class WorldObservationService(Protocol):
    def build_observation_batch(
        self,
        *,
        adapter: WorldRuntimeAdapterProtocol,
        terminated: Mapping[str, bool],
    ) -> Mapping[str, Mapping[str, Any]]:
        """Return raw observation payloads per agent (map/features/metadata)."""

    def build_agent_contexts(
        self,
        *,
        adapter: WorldRuntimeAdapterProtocol,
    ) -> Mapping[str, Mapping[str, Any]]:
        """Return per-agent contextual data (pending intent, chat state, etc.)."""
```

`WorldContext.observe` will use these methods in combination with local services (queue manager, employment, economy, perturbations) to assemble the envelope via `build_observation_envelope`.

## Dependencies & Wiring
- Service needs access to:
  - Embedding allocator / observation cache (currently provided by `WorldRuntimeAdapter`).
  - Observation configuration (profiles) – use existing `ObservationBuilder` under the hood but keep it encapsulated.
- Wiring path:
  - Inject a `WorldObservationService` instance into `WorldState` when constructing `WorldContext` inside `WorldState._initialize_services()`.
  - Store reference on `WorldContext` (e.g., `self.observation_service`).

## Data responsibilities
- Observation service handles per-agent map/feature tensors, metadata, pending intents via existing observation helpers.
- `WorldContext` handles:
  - Tick stamping, console results, actions merges (already done).
  - Queue metrics (`queue_manager`), running affordances (`affordance_service`), relationship snapshots (relationship service), employment/economy snapshots (existing services), perturbation state.
  - Rewards/policy metadata remain inputs supplied by the loop.

## Next Steps
1. Implement concrete service (wrapper over existing `ObservationBuilder`).
2. Update `WorldState`/`WorldContext` to accept the service in constructors.
3. Adjust tests to use the service when building observations.
