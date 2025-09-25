# Observation Builder Upgrade Work Package

## Objective
Replace placeholder observation payloads with fully realised tensors for the hybrid variant, aligning with HIGH_LEVEL_DESIGN requirements and preparing for renderer/UI consumers.

## Scope
- `src/townlet/observations/builder.py`
- Supporting utilities (neighbor queries, encoding helpers)
- Tests in `tests/test_observer_payload.py` and new suites for tensor shape/content
- Documentation updates describing observation schema

## Deliverables
- Hybrid observation tensor with egocentric map, scalar features, embedding slot
- Config-driven window sizes and feature flags
- Updated telemetry/sample payloads (if schema surfaces change)
- Comprehensive unit tests and sample fixtures
- Documentation: architecture guide section, implementation notes, checklist update

## Tasks
1. **Design Specification**
   - Finalise feature list per HIGH_LEVEL_DESIGN (map size, scalars, social placeholders)
   - Define tensor layout and metadata (dtype, ordering)
2. **Infrastructure Prep**
   - Introduce grid neighborhood utilities in `WorldState`
   - Add config validation for observation parameters
3. **Implementation**
   - Replace `_build_single` stub with real encoding
   - Add caching/performance safeguards (avoid repeated allocations)
4. **Testing**
   - Unit tests validating shapes/values
   - Snapshot tests with deterministic fixtures
   - Update existing observer tests to assert new keys
5. **Documentation & Samples**
   - Update `docs/ARCHITECTURE_INTERFACES.md` observation section
   - Add sample tensor dump in `docs/samples/`
   - Update checklist for observation changes

## Detailed Task Breakdown
- **Task 1A — Feature Matrix** ✅
- **Task 1B — Tensor Layout RFC** ✅
- **Task 2A — Neighborhood API** ✅ (placeholder object data TBD)
- **Task 2B — Config Guardrails** ✅
- **Task 3A/B — Map & Scalar Encoding** ✅
- **Task 3C — Social Placeholder** ✅ (slots reserved)
- **Task 4A/B — Tests** ✅
- **Task 5A/B/C — Docs & Samples** ✅

## Risks & Mitigations
- **R8**: Tensor mismatch breaks downstream consumers — provide sample payloads + tests.
- **R9**: Performance regression — micro-benchmark encoding time, optimise loops.
- **R10**: Map encoding incorrect due to inconsistent world data — add integration test using `SimulationLoop` snapshot.

_Target_: Complete before starting conflict/queue milestone work (M2.5).
