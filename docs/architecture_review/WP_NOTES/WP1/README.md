# WP1 — Ports & Factory Registry (Working Notes)

Purpose: capture findings, decisions, and progress while implementing Work Package 1. Update proactively as seams are discovered or addressed.

## TODO / Progress Checklist

- [ ] Inventory SimulationLoop dependencies (world, policy, telemetry methods used).
- [ ] Audit current world implementation entry points (`world/core`, adapters).
- [ ] Audit policy runtime / orchestrator interfaces.
- [ ] Audit telemetry publisher surface.
- [ ] Draft port protocol stubs aligning with ADR-001.
- [ ] Outline adapter delegations for default providers.
- [ ] Define registry module responsibilities & key names.
- [ ] Identify required dummies/testing hooks.
- [ ] Plan composition root refactor sequence.
- [ ] Note integration tests to add/adjust.

## Findings & Open Questions

### Loop Surface Inventory (2024-XX-XX)
- **Policy backend methods invoked by `SimulationLoop`:** `register_ctx_reset_callback`, `enable_anneal_blend`, `set_anneal_ratio`, `active_policy_hash`, `current_anneal_ratio`, `reset_state`, `decide`, `post_step`, `flush_transitions`, `latest_policy_snapshot`, `possessed_agents`, `consume_option_switch_counts`.  
  - *Implication:* Only `decide` (+ simple lifecycle) belong on the WP1 port. The remaining hooks must move behind policy adapters or be driven via strategy/telemetry services.
- **Telemetry sink usage:** `set_runtime_variant`, `update_policy_identity`, `drain_console_buffer`, `record_console_results`, `publish_tick`, `latest_queue_metrics`, `latest_embedding_metrics`, `latest_job_snapshot`, `latest_events`, `latest_employment_metrics`, `latest_rivalry_events`, `record_stability_metrics`, `latest_transport_status`, `record_health_metrics`, `record_loop_failure`.  
  - *Implication:* Port must stay slim (`start/stop/emit_event/emit_metric`). Console buffering, health reporting, and “latest_*” accessors need to live in adapters or separate telemetry services.
- **World runtime usage:** `queue_console`, `tick` (passing action provider), optional `bind_world_adapter`. Core loop also touches `WorldState` directly (`self.world`).  
  - *Implication:* Port should expose only `observe`, `apply_actions`, `tick`, `snapshot`. Console queueing + adapter binding remain implementation details in default adapter.
- **Direct world state access:** loop iterates `self.world.agents`, etc. Need to decide how much remains outside the port for WP1 (short-term we may keep direct access while world modularisation lands in WP2).

### Implementation Audit Notes (2024-XX-XX)
- **World runtime (`world/runtime.py`):** exposes rich console queueing, staged actions, `tick` returning `RuntimeStepResult`, and `snapshot`. Also supports `bind_world`, `bind_world_adapter`. Good news: port can wrap `tick/apply_actions/observe/snapshot`; adapters will need to bridge console queueing + binding mechanics.
- **World state (`world/grid.py` et al.):** `WorldState` still aggregates everything (console, relationships, etc.). For WP1, adapters should shield the loop from these details while WP2 performs the decomposition.
- **Policy runtime (`policy/runner.py`):** contains many extra hooks (anneal controls, action providers, telemetry snapshots). Port should boil this down to `on_episode_start`, `decide`, `on_episode_end`. Adapters for scripted/Torch/stub will continue exposing hashes, anneal ratios, console wiring internally.
- **Telemetry publisher (`telemetry/publisher.py`):** god-object maintaining queue metrics, console auth, worker threads, `latest_*` queries. Port must *not* expose these; default adapter should translate port calls (`emit_event`, `emit_metric`, `start`, `stop`) into publisher operations and preserve legacy accessors for consoles via composition.
- **Fallback providers:** `policy/fallback.py` and `telemetry/fallback.py` show how stub implementations operate today; useful reference when creating WP1 dummy/test utilities.

### Open Questions
- Where to relocate policy anneal blend + hash reporting so the WP1 port remains minimal?
- Can telemetry `latest_*` queries be satisfied via caching DTOs in the adapter while exposing only generic `emit_*` calls on the port?

## References

- `docs/architecture_review/WP_TASKINGS/WP1.md`
- `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md`
- `src/townlet/core/sim_loop.py`
- `src/townlet/world/**`
- `src/townlet/policy/**`
- `src/townlet/telemetry/**`

Update this file as work proceeds (new sections welcome: risk log, test plan, blockers, etc.).

### Composition Findings (2024-XX-XX)
- `core/factory_registry.py` currently holds three global registries (`world`, `policy`, `telemetry`) and registers providers inline. Keys in use: world (`default`, `facade`), policy (`scripted`, `default`, `stub`, `pytorch`), telemetry (`stdout`, `default`, `stub`, `http`). Multiple aliases resolve to the same implementation today.
- Configs (`runtime` section in e.g. `configs/examples/poc_hybrid.yaml`) specify provider names plus optional `options` dict. Migration to WP1 factories must preserve this schema or introduce a clear transition plan.
- Provider resolution happens during `SimulationLoop` construction via `resolve_world/policy/telemetry` with keyword options forwarded wholesale.
- WP1 registry modules will need to re-export the existing fallback behaviour (Torch/httpx guards) and ensure defaults match ADR-001 keys (`default`, `scripted`, `stdout`, with `dummy/stub` variants registered for tests).

### Stub & Test Inventory (2024-XX-XX)
- **Policy:** `townlet.policy.fallback.StubPolicyBackend` satisfies the legacy `PolicyBackendProtocol`, returning wait actions. Tests exercising it:
  - `tests/test_fallbacks.py::test_policy_stub_resolution`
  - `tests/test_policy_orchestrator.py::test_capture_rollout_warns_on_stub_policy`
  - `tests/test_policy_backend_selection.py::test_pytorch_provider_resolves_conditionally`
- **Telemetry:** `townlet.telemetry.fallback.StubTelemetrySink` mirrors telemetry port surface (including console buffers, latest_* accessors). Covered by `tests/test_fallbacks.py::test_telemetry_stub_resolution` and orchestrator stub wiring.
- **World:** no existing dummy/stub world implementation; WP1 must introduce `DummyWorld` to support loop smoke tests.
- **Utility helpers:** `townlet.core.is_stub_policy/is_stub_telemetry` rely on provider names; ensure new registry/factory API preserves these helpers or update tests accordingly.

Implication: new WP1 dummies should integrate cleanly with existing stub tests, or tests must be updated to the new factory paths.

### Tooling & Gate Check (2024-XX-XX)
- `pyproject.toml` already includes `pydantic>=2.11` and dev dependencies (`mypy`, `pytest`, `ruff`). Mypy runs in strict mode across `townlet` by default; expect to satisfy strict typing for new modules or configure targeted overrides.
- Ruff lint targets main sources/tests with rulesets `E,F,I,N,UP,B,A,C4,TID,RUF` and line length 140.
- Pytest default command includes coverage flags; new tests should fit within existing structure (`tests/...`).
- No additional config needed for DTO work—Pydantic is available out of the box.
- Pre-existing overrides ignore mypy missing imports for selected world modules; new ports/factories should not require similar overrides if typed cleanly.
