# WP: Observation Variants & Social Feature Slots — Phase 1 Discovery

## Implementation Survey
- ObservationBuilder initialises shared scalar features, optional landmark bearings, and social slots for every variant (`hybrid`, `full`, `compact`) while enforcing the relationships stage gate before enabling social snippets (`src/townlet/observations/builder.py:24-131`).
- Variant-specific assembly fans out inside `_build_single`, with `hybrid` and `full` emitting egocentric map tensors and `compact` returning a zero-sized map alongside the scalar vector (`src/townlet/observations/builder.py:287-358`, `src/townlet/observations/builder.py:404-463`).
- Social snippet vectors blend hashed agent embeddings with trust/familiarity/rivalry metrics plus optional aggregates, falling back to rivalry ledgers when relationship ties are absent (`src/townlet/observations/builder.py:500-610`).
- Existing pytest coverage already probes hybrid/full/compact layouts and the social snippet golden fixture, confirming shape expectations and landmark encoding (`tests/test_observation_builder.py:19-118`, `tests/test_observation_builder_full.py:11-74`, `tests/test_observation_builder_compact.py:11-67`, `tests/test_observations_social_snippet.py:11-83`).

## ADR & Spec Requirements
- ADR Section "Observation Builder" describes the multi-variant contract: hybrid as the primary 11×11 map with feature vector (~531 dims in early drafts) and placeholders for social slots (`docs/external/adr.txt:409-460`).
- Observation Tensor Specification codifies variant shapes: hybrid `(4, 11, 11)`, full `(6, 11, 11)` with path gradients, compact omitting the map (0×0×0) but retaining shared scalars and optional social snippet aggregates (`docs/design/OBSERVATION_TENSOR_SPEC.md:32-66`).
- Social snippet controls derive from config defaults (`top_friends=2`, `top_rivals=2`, `embed_dim=8`, aggregates optional) and are expected to surface relationship ledger data when stages ≥ A (`src/townlet/config/loader.py:181-215`).

## Relationship & Social Data Sources
- WorldState exposes rivalry and relationship ledgers, symmetric updates, and snapshot helpers consumed by the observation layer and telemetry (`src/townlet/world/grid.py:1520-1700`).
- TelemetryPublisher normalises relationship snapshots and tracks updates/events, ensuring downstream consumers can audit which ties informed the observation payloads (`src/townlet/telemetry/publisher.py:820-899`, `src/townlet/telemetry/publisher.py:1284-1317`).

## Gaps & Preliminary Acceptance Criteria
### Identified Gaps
- `_build_single` retains a stale TODO for the compact variant even though `_build_compact` is implemented, signalling the need to retire the fallback stub once parity is validated (`src/townlet/observations/builder.py:287-298`).
- Social snippet aggregates currently surface trust and rivalry means/max but omit familiarity rollups; ADR leaves aggregates open-ended, yet demo goals call for spotlighting social cohesion, so we need to decide whether to add familiarity aggregates or document their absence (`src/townlet/observations/builder.py:107-117`, `docs/external/adr.txt:422-460`).
- Relationship data reaches observations only when the ledger is populated; in baseline sims without chat/employment interactions the social slots remain zeroed, undermining the ADR expectation of visible top friends/rivals during demos. We should catalogue which events feed ties and define minimal activity scenarios that guarantee non-zero slots (`src/townlet/world/employment.py:320-392`, `src/townlet/world/grid.py:1740-1796`).

### Acceptance Criteria (Per Variant)
- **Hybrid**: Emit `(4, window, window)` maps with channel order `[self, agents, objects, reservations]`, include shared scalar bundle, and populate social snippet/aggregates when relationships stage ≥ A (`docs/design/OBSERVATION_TENSOR_SPEC.md:32-45`).
- **Full**: Extend hybrid by adding `path_dx`/`path_dy` channels, maintaining scalar parity and preserving landmark slice metadata for UI overlays (`docs/design/OBSERVATION_TENSOR_SPEC.md:46-55`, `src/townlet/observations/builder.py:399-450`).
- **Compact**: Return `map_shape == (0, 0, 0)` with an unchanged scalar vector, guaranteeing that metadata enumerates feature names/landmarks and that social slots align with configured counts (`docs/design/OBSERVATION_TENSOR_SPEC.md:56-66`, `src/townlet/observations/builder.py:422-463`).
- **Social Snippet**: For any variant with social slots enabled, guarantee that at least one standard scenario (e.g., rivalry conflict, shift assistance) yields non-zero trust/familiarity/rivalry entries and that aggregates reflect those values within tolerance (`tests/test_observations_social_snippet.py:27-83`).
