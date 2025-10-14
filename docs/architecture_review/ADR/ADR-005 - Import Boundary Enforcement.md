# ADR 0005: Import Boundary Enforcement

## Status

Accepted

## Context

The townlet simulation has completed four major architectural refactorings (WP1-4):
- WP1: Ports and adapters pattern with dependency inversion (ADR-001)
- WP2: World modularization with clean subsystem separation (ADR-002)
- WP3: DTO-based boundaries for typed, validated data transfer (ADR-003)
- WP4: Strategy-based training architecture (ADR-004)

These refactorings established clear architectural boundaries, but nothing prevented accidental coupling through Python imports. A developer could unknowingly add `from townlet.world import WorldState` to a DTO module, breaking the independence guarantee that DTOs are supposed to provide. Similarly, direct imports like `from townlet.telemetry import TelemetryPublisher` in policy modules would violate the separation of concerns.

Manual code review catches some violations, but humans miss subtle indirect import chains (e.g., `policy → config → snapshots → telemetry`). We need automated enforcement to:
1. Prevent regressions as the codebase grows
2. Guide new contributors toward correct patterns
3. Document legitimate exceptions with clear architectural rationale
4. Catch violations early in the development cycle (pre-commit and CI)

## Decision

Implement **import-linter** based boundary enforcement with 5 contracts defining the architectural layering and separation of concerns:

### 1. Contract Definitions

**Contract 1: DTO Independence**
```ini
[importlinter:contract:dto-independence]
name = DTOs must not import concrete packages
type = independence
modules =
    townlet.dto.observations
    townlet.dto.policy
    townlet.dto.rewards
    townlet.dto.telemetry
    townlet.dto.world
```

**Rationale**: DTOs are pure data containers (Pydantic v2 models) that cross architectural boundaries. They must remain independent of concrete implementations to avoid coupling consumers to internal details. This enables DTOs to be serialized, validated, and migrated without dragging in domain logic.

---

**Contract 2: Layered Architecture**
```ini
[importlinter:contract:layered-architecture]
name = Layered architecture (domain → core → ports → dto)
type = layers
layers =
    townlet.world | townlet.policy | townlet.telemetry | townlet.rewards |
    townlet.observations | townlet.snapshots | townlet.stability |
    townlet.lifecycle | townlet.benchmark | townlet.scheduler
    townlet.core
    townlet.ports
    townlet.dto
```

**Rationale**: Enforces the ports-and-adapters architecture:
- **Domain layer** (top): Business logic, systems, services
- **Core layer**: Orchestration (SimulationLoop), factories, interfaces
- **Ports layer**: Protocol definitions for dependency inversion
- **DTO layer** (bottom): Pure data, no dependencies

Higher layers can import from lower layers (domain → core → ports → dto), but not vice versa. This prevents:
- DTOs importing domain logic
- Ports importing core orchestration
- Core importing domain implementations (except through documented patterns)

---

**Contract 3: World/Policy Separation**
```ini
[importlinter:contract:no-world-to-policy]
name = World must not import policy
type = forbidden
source_modules = townlet.world
forbidden_modules = townlet.policy
```

**Rationale**: World and policy are at the same layer (domain), but world must not depend on policy decisions. World models the environment and physics; policy decides agent actions. This separation allows:
- Testing world behavior independently of policy
- Swapping policy implementations without touching world code
- Clear ownership: world owns state, policy owns decisions

**Direction**: Policy → world is allowed (policy needs to observe world state); world → policy is forbidden.

---

**Contract 4: Policy/Telemetry Separation**
```ini
[importlinter:contract:no-policy-to-telemetry]
name = Policy must not import telemetry
type = forbidden
source_modules = townlet.policy
forbidden_modules = townlet.telemetry
```

**Rationale**: Policy should not directly depend on telemetry implementation. Telemetry is a cross-cutting concern owned by the core orchestration layer (SimulationLoop). Policy emits events through core, not directly. This allows:
- Policy code to remain focused on decision-making
- Telemetry implementation changes without affecting policy
- Testing policy without telemetry infrastructure

**Exceptions**: Indirect paths (`policy → core → telemetry`, `policy → world → telemetry`) are acceptable because core owns telemetry for coordination.

---

**Contract 5: Config DTO-Only**
```ini
[importlinter:contract:config-dto-only]
name = Config must only import DTO and typing
type = forbidden
source_modules = townlet.config
forbidden_modules =
    townlet.world
    townlet.policy
    townlet.telemetry
    townlet.rewards
    townlet.observations
```

**Rationale**: Config is a pure data layer (Pydantic models) loaded before runtime initialization. It must not import domain packages to avoid:
- Circular dependencies (domain imports config for types)
- Heavy imports during config loading
- Config validation requiring runtime state

**Exception**: Config.loader can import `snapshots.migrations` for migration handler registration (minimal coupling to enable extensibility).

---

### 2. Exception Patterns

Legitimate architectural patterns that require boundary crossings:

**Factory Pattern (ADR-001)**:
- Factories must import concrete implementations to instantiate them
- Example: `townlet.factories.world_factory → townlet.world.grid`
- Rationale: Dependency inversion requires factories to resolve abstractions to concrete types

**Orchestration (SimulationLoop)**:
- Core orchestration owns domain objects for coordination
- Example: `townlet.core.sim_loop → townlet.telemetry.publisher`
- Rationale: SimulationLoop is the composition root that wires up the system

**Composition Relationships**:
- Parent objects own child objects through composition
- Example: `townlet.world.runtime → townlet.lifecycle.manager`
- Rationale: WorldRuntime aggregates lifecycle management as a composed service

**Cross-Cutting Concerns (Snapshots)**:
- Snapshots serialize state from all subsystems
- Example: `townlet.snapshots.state → townlet.world.grid`
- Rationale: Snapshot serialization needs access to all subsystem state

**Same-Layer Imports (Domain modules)**:
- Domain modules at the same layer can import each other
- Example: `townlet.policy.runner → townlet.world.grid`
- Rationale: Policy needs to observe world state to make decisions

**Indirect Dependencies**:
- Long import chains through acceptable intermediate layers
- Example: `policy → core → telemetry` (policy imports core, core imports telemetry)
- Rationale: Indirect coupling through designed interfaces is acceptable

---

### 3. Enforcement Mechanism

**Local Development**:
```bash
lint-imports  # Run before committing
```

**CI Pipeline**:
```yaml
- name: Import boundary enforcement
  run: lint-imports
```
- Runs on all PRs targeting main
- Blocks merge on new violations
- Execution time: <5 seconds (214 files, 650 dependencies)

**Configuration**: `.importlinter` in repository root
- 5 contracts defined
- ~60 documented exceptions with architectural rationale
- Comments reference ADR-001, ADR-002, ADR-003

---

### 4. Developer Workflow

**When violation occurs**:
1. Run `lint-imports` locally to see violation details
2. Review the import chain shown in error message
3. Determine if import is legitimate:
   - **If legitimate**: Add exception to `.importlinter` with rationale comment
   - **If not legitimate**: Refactor to respect boundaries (use DTOs, ports, dependency inversion)
4. Update `docs/architecture_review/IMPORT_EXCEPTIONS.md` with full documentation
5. Commit changes; CI will validate

**Adding new exception**:
```ini
# In .importlinter, under appropriate contract's ignore_imports:
ignore_imports =
    # Factory pattern: Factories import what they instantiate (ADR-001)
    townlet.factories.world_factory -> townlet.world.grid
```

---

### 5. Removed Contracts

**Port Independence** (removed):
- Originally prevented ports from importing domain modules
- **Conflict**: Layered architecture already enforces dto → ports boundary
- **Issue**: Port protocols need to reference concrete types for type hints (e.g., `WorldRuntime` protocol returns `WorldState`)
- **Decision**: Remove; handled by layered architecture + documented exceptions

**Snapshot Boundaries** (removed):
- Originally prevented snapshots from importing implementations
- **Conflict**: Snapshots are cross-cutting by design - they must serialize all subsystems
- **Issue**: Created ~8 false positives for legitimate serialization
- **Decision**: Remove; snapshots are cross-cutting concern, not a layered boundary

---

## Consequences

### Positive

1. **Regression Prevention**: Automated checks prevent accidental coupling during development

2. **Architectural Guidance**: Clear violation messages guide developers toward correct patterns
   ```
   townlet.policy is not allowed to import townlet.telemetry:
   - townlet.policy.runner -> townlet.core.sim_loop (l.25)
     townlet.core.sim_loop -> townlet.telemetry.publisher (l.51)
   ```

3. **Documentation**: Exception registry documents all legitimate boundary crossings with rationale

4. **Fast Feedback**: <5 second execution suitable for pre-commit hooks and CI

5. **Onboarding**: New contributors see clear boundaries and exception patterns

6. **Refactoring Safety**: Changes that accidentally break boundaries are caught immediately

### Neutral

1. **Exception Maintenance**: ~60 documented exceptions require maintenance as code evolves
   - Mitigation: Comprehensive comments and exception registry documentation

2. **Learning Curve**: Developers must understand layered architecture and exception patterns
   - Mitigation: CLAUDE.md documents boundaries and common patterns

### Negative

1. **Initial Setup Effort**: Required Phase 0 fixes and exception documentation
   - Mitigated: One-time effort, now complete

2. **False Positives from Long Chains**: Indirect import chains can trigger violations
   - Mitigated: Exception system handles indirect paths; well-documented patterns

---

## Migration Notes

### For Developers

1. **Before Committing**: Run `lint-imports` to check for violations

2. **If Violation Found**:
   - Review architectural boundaries (CLAUDE.md: "Import Boundary Enforcement")
   - Check if pattern matches documented exceptions
   - Add exception with rationale if legitimate
   - Refactor if not legitimate

3. **Adding New Modules**:
   - Follow layered architecture (domain → core → ports → dto)
   - Use DTOs for cross-boundary data transfer
   - Import through ports, not concrete implementations
   - Check common exception patterns for guidance

4. **Adding New Exceptions**:
   - Add to `.importlinter` under appropriate contract
   - Add comment with architectural rationale and ADR reference
   - Update `IMPORT_EXCEPTIONS.md` with full documentation
   - Ensure CI passes before merging

### For Reviewers

1. **PR Review Checklist**:
   - Verify CI import-linter check passes
   - Review any new exceptions for architectural soundness
   - Ensure exceptions have clear rationale comments
   - Check exception registry updated if new pattern

2. **Red Flags**:
   - DTO importing domain modules
   - World importing policy
   - Policy directly importing telemetry (not through core)
   - Config importing runtime packages
   - Exception without rationale comment

---

## Implementation Status

**Status**: COMPLETE
**Completion Date**: 2025-10-15 (WP5 Phase 2)

### Delivered Components

**Phase 0: Risk Reduction** ✅
- 3 quick win fixes (core.utils, config.loader, layering order)
- Exception registry (`IMPORT_EXCEPTIONS.md`) with 21 documented patterns
- 73% violation reduction (79 → 21 legitimate exceptions)
- 3/5 contracts passing after fixes

**Phase 1: Production Configuration** ✅
- `.importlinter` production config with 5 contracts
- ~60 documented exceptions with architectural rationale
- All 5 contracts passing (100%)
- Performance validated: <5 seconds for 214 files, 650 dependencies

**Phase 2: CI Integration** ✅
- Updated `.github/workflows/ci.yml` to use production config
- CLAUDE.md documentation with developer guidance
- PR blocking on new violations
- Exception process documented

**Phase 3: Documentation** ✅
- ADR-005 (this document)
- Exception registry maintained
- CLAUDE.md updated with boundary guidance
- WP5 completion summary

### Metrics

- **Files Monitored**: 214 Python files
- **Dependencies Tracked**: 650 imports
- **Contracts Enforced**: 5
- **Exceptions Documented**: ~60
- **Analysis Time**: <5 seconds
- **CI Overhead**: <1% of total CI time
- **Violations Prevented**: 79 initial violations reduced to 0 (with documented exceptions)

### Test Coverage

- ✅ All contracts passing in CI
- ✅ Local `lint-imports` command available
- ✅ PR blocking on violations validated
- ✅ Exception patterns tested (factory, orchestration, composition, cross-cutting)

---

## Related Documents

- **ADR-001: Ports and Factory Registry** — Dependency inversion pattern; factories import implementations
- **ADR-002: World Modularisation** — World package structure; composition relationships
- **ADR-003: DTO Boundary** — DTO independence and serialization patterns
- **ADR-004: Policy Training Strategies** — Policy architecture and training coordination
- **IMPORT_EXCEPTIONS.md** — Comprehensive exception registry with rationale
- **WP5 Phase 0-2 Completion Summaries** — Implementation details and metrics
- **CLAUDE.md** — Developer guide to working with import boundaries

---

## Appendix: Contract Evolution

### Why 5 Contracts?

**Started With**: 7 contracts (initial analysis config)
1. DTO Independence ✅ Kept
2. Layered Architecture ✅ Kept
3. World/Policy Separation ✅ Kept
4. Policy/Telemetry Separation ✅ Kept
5. Config DTO-Only ✅ Kept
6. Port Independence ❌ Removed (redundant with layered architecture)
7. Snapshot Boundaries ❌ Removed (conflicts with cross-cutting nature)

**Removed Contracts**:
- **Port Independence**: Layered architecture already prevents dto → ports violations; port protocols need concrete type references for type hints (ADR-001 pattern)
- **Snapshot Boundaries**: Snapshots are cross-cutting by design - they serialize all subsystems; preventing imports would require duplicating state structures

**Result**: 5 contracts provide strong boundary enforcement without false positives

### Exception Count Evolution

**Phase 0 Start**: 79 violations
- 23 direct imports violating contracts
- 56 indirect import chains

**Phase 0 End**: 21 documented exceptions
- Removed core.utils convenience imports (eliminated 10 violations)
- Fixed config.loader snapshot import (eliminated 8 violations)
- Fixed layering order (eliminated 20 false positives)
- Remaining 21 = legitimate architectural patterns

**Phase 1 End**: ~60 documented exceptions
- Added factory pattern exceptions (12)
- Added orchestration exceptions (15)
- Added domain-level same-layer imports (16)
- Added composition relationships (4)
- Added cross-cutting snapshot serialization (8)
- Added indirect dependency chains (5)

**Final State**: All violations are documented exceptions with architectural rationale

---

**End of ADR-005**
