# Policy Backends

This guide explains how Townlet selects and uses policy backends, how to enable
ML features, and what to expect when optional dependencies are missing.

- Default provider: `scripted` (no ML dependencies)
- Optional provider: `pytorch` (install with the `ml` extra)
- Fallback behavior: if a selected backend requires missing dependencies, a
  stub backend is used and a warning is logged.

## Selecting a Backend

Backends are resolved by the factory registry. You can set the provider via
configuration (preferred) or programmatically.

- Config (YAML):
  ```yaml
  runtime:
    policy:
      provider: scripted  # or pytorch
  ```
- Programmatic:
  ```python
  from townlet.core.factory_registry import resolve_policy
  backend = resolve_policy("scripted", config=cfg)
  ```

## Optional Dependencies

Install ML dependencies with the `ml` extra:

```
pip install -e .[ml]
```

When `pytorch` is selected but PyTorch is not installed, the registry logs a
warning and returns a stub backend that performs no ML work. This guarantees
that CLI tools and tests collect without Torch.

## Training Utilities

PPO and BC utilities live under backend packages and are imported lazily:

- PPO ops: `townlet.policy.backends.pytorch.ppo_utils`
- BC trainer: `townlet.policy.backends.pytorch.bc`

Public shims keep legacy import paths stable and importable without Torch:

- `townlet.policy.ppo.utils` re-exports ops when Torch is present and raises a
  clear error if used otherwise.
- `townlet.policy.bc` re-exports BC utilities when Torch is present and provides
  placeholder types that raise at runtime if you attempt to train without Torch.

## CLI Messaging

`scripts/run_training.py` emits friendly messages when a mode requires Torch
(`bc`, `anneal`, PPO) but Torch is not available.

