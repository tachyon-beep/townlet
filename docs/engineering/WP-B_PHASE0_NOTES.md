# WP-B Phase 0 – Factory Registry Recon

## Optional Dependency Touchpoints
- **PyTorch (`torch`)** – used in `policy.models`, `policy.runner`, PPO utilities, BC pipelines, and training orchestrator (
  - Runtime: enrich trajectory metadata; optional network inference in `PolicyRuntime`.
  - Training: required for PPO/BC; absent installations currently raise runtime errors or skip logic via helper guards.
- **FastAPI TestClient / httpx** – `tests/test_web_gateway.py` and `tests/test_web_operator.py` rely on `fastapi.testclient.TestClient`, bringing in `httpx`.
- **Uvicorn/FastAPI extras** – Runtime API server launched by `scripts/run_simulation.py` when web dashboard enabled; already in base dependency list but registry must allow disabling transports without optional stacks.
- **Console/Web sockets** – `telemetry.publisher`’s TCP transport depends on optional TLS packages only when configured; default `stdout` transport requires no extras.

## Factory Descriptor Concept
- Introduce `SimulationConfig.runtime` namespace housing provider descriptors:
  ```yaml
  runtime:
    world:
      provider: "default"          # maps to registry entry `world.default`
      options: {}
    policy:
      provider: "scripted"         # fallback backend; ml extras add `pytorch`
      options:
        anneal_blend: true
    telemetry:
      provider: "stdout"
      options:
        diff_enabled: true
  ```
- Backwards compatibility: absence of `runtime` block defaults to current implementations. `AffordanceRuntimeConfig.factory` continues to point to custom runtime factories until folded into the same scheme.
- Registry lookup key pattern: `<domain>.<provider>` with built-in aliases (`default`, `scripted`, `stdout`).

## Stub Implementation Requirements
- **Policy Stub** – Implements `PolicyBackendProtocol`; returns no-op actions (wait) and records minimal metadata when ML extras missing.
- **Telemetry Stub** – Implements `TelemetrySinkProtocol`; accumulates console commands and health metrics in-memory, enabling tests to run without external transports.
- **World Stub** – Optional for testing; consider hooking existing `WorldRuntime` into registry with alias `facade`.
- Stubs should emit structured warnings via logger indicating reduced capability and suggesting enabling extras.

## Success Criteria for Phase 1+
- `SimulationLoop` boots via registry resolution.
- Config descriptors validated via Pydantic; invalid provider names yield actionable errors.
- PyTorch absent + policy descriptor `pytorch` triggers stub fallback with warning instead of crash.
- Integration tests cover both default and stubbed providers.

## Phase 2 Snapshot (Config & Optional Dependencies)
- `SimulationConfig.runtime` exposes `world`, `policy`, and `telemetry` provider descriptors backed by Pydantic models. YAML may use either full mapping syntax or a shorthand string (e.g., `runtime.policy: "scripted"`).
- Example configs now include an explicit `runtime` block enumerating default providers (`configs/examples/poc_hybrid.yaml`).
- `SimulationLoop` consumes the parsed descriptors via the factory registry, preserving backward compatibility with ad-hoc overrides.
- `pyproject.toml` defines optional extras:
  - `[ml]` installs PyTorch and torchvision for neural policy backends.
  - `[api]` installs `httpx` for API/client testing when the HTTP stack is exercised.
- README quickstart documents the new extras so contributors can enable them on demand.

## Phase 3 Snapshot (Fallbacks & Docs)
- Registry now registers `policy.pytorch`/`telemetry.http` helpers that fall back to stub implementations when optional dependencies are missing, logging structured warnings for visibility.
- Stub policy and telemetry providers live in `townlet.policy.fallback` and `townlet.telemetry.fallback`, satisfying the core protocols while reducing behaviour to safe no-ops.
- Tests exercise fallback behaviour (`tests/test_fallbacks.py`), ensuring CI covers minimal environments without ML or HTTP extras.
- Core protocol documentation highlights provider selection, stub behaviour, and guidance for opting into extras.
