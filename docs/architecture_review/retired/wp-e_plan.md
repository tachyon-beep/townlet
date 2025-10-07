# WP‑E: Policy Backend Abstraction

Objective: Isolate scripted vs. ML backends and provide optional extras for
heavy stacks. Ensure default operation without Torch and clean config-driven
selection.

## Phases, Steps, Tasks

### Phase 0 – Inventory
- Inventory direct imports of training utilities and PPO ops.
- Verify `PolicyBackendProtocol` covers training hooks used by loop/tools.

Status: complete.

### Phase 1 – Protocols & Registry
- Confirm `PolicyBackendProtocol` and factory registry entry points.
- Scripted backend remains default, `pytorch` is optional.

Status: complete (see `src/townlet/core/interfaces.py`, `src/townlet/core/factory_registry.py`).

### Phase 2 – Backend Packaging
- Create `policy/backends/pytorch/` for ML‑dependent utilities.
- Move PPO ops and BC utilities under the backend; keep public shims.

Status: complete.

### Phase 3 – Gating & Shims
- `townlet.policy.ppo.utils` becomes a shim that re‑exports ops if Torch is
  available, else raises a clear error when used.
- `townlet.policy.bc` becomes a shim that re‑exports when Torch is available,
  else provides placeholder types that raise on use (but remain importable).
- `PolicyTrainingOrchestrator` lazily imports PPO ops to avoid import‑time Torch
  dependency; `TrainingHarness` defers construction.

Status: complete.

### Phase 4 – Config & CLI Integration
- Factory: `scripted` default; `pytorch` falls back to stub if Torch missing.
- CLI: add friendly messages in `run_training.py` when Torch is required.

Status: complete.

### Phase 5 – Tests & Docs
- Tests: exercise provider fallback, import collection without Torch, and guard
  PPO unit tests behind Torch presence.
- Docs: add `docs/guides/policy_backends.md` and reference from the target
  architecture.

Status: tests complete; docs added.

## Exit Criteria
- Policy selection is config‑driven; scripted backend is default.
- pytest collects without Torch installed.
- Clear stub fallback path and CLI messaging in ML‑absent environments.

Status: met.

