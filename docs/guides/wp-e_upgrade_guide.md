# WP‑E Upgrade Guide: Policy Backend Abstraction

This guide summarizes migration notes for the policy backend changes.

What changed
- Policy backends are now split by responsibility:
  - `scripted` backend (default) — no ML dependencies; backed by `PolicyRuntime`.
  - `pytorch` backend — ML utilities behind the optional `[ml]` extra.
  - `stub` backend — safe fallback when ML dependencies are missing.
- ML‑dependent utilities moved under backend packages and are imported lazily:
  - PPO ops: `townlet.policy.backends.pytorch.ppo_utils`
  - BC: `townlet.policy.backends.pytorch.bc`
  - Public shims keep old import paths importable without Torch:
    - `townlet.policy.ppo.utils` — re‑exports ops when Torch installed; otherwise raises on use.
    - `townlet.policy.bc` — re‑exports BC when Torch installed; otherwise provides placeholders that raise on use.

How to select a backend
- Config (preferred):
  ```yaml
  runtime:
    policy:
      provider: scripted  # or pytorch, stub
  ```
- Programmatic:
  ```python
  from townlet.core.factory_registry import resolve_policy
  backend = resolve_policy("scripted", config=cfg)
  ```

Enabling ML features
- Install the ML extra to enable the `pytorch` backend:
  ```
  pip install -e .[ml]
  ```
- Without `[ml]`, selecting `pytorch` falls back to the stub backend with a warning.

CLI behaviors
- `scripts/run_training.py` prints a friendly message and exits when an ML‑required path
  (`bc`, `anneal`, or PPO) is requested but Torch is not installed.

Common pitfalls
- Import errors in tests due to `torch` are usually caused by importing ML modules
  at module load time. Use the public shims or guard imports behind `torch_available()`.
- Tests that require Torch should be marked with a skip when Torch is not present.

New optional scripted alias
- For symmetry, a scripted alias package is available:
  ```python
  from townlet.policy.backends.scripted import ScriptedPolicyBackend
  ```
  This maps to `PolicyRuntime`.

