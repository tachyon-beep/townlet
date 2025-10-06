from __future__ import annotations

import importlib
from pathlib import Path


def test_policy_module_imports_without_torch() -> None:
    # Must not raise even if torch is not installed
    mod = importlib.import_module("townlet.policy")
    assert hasattr(mod, "DEFAULT_POLICY_PROVIDER")
    assert hasattr(mod, "resolve_policy_backend")


def test_training_orchestrator_import_without_torch() -> None:
    # The module should import even if Torch isn't present; heavy ops are lazy.
    mod = importlib.import_module("townlet.policy.training_orchestrator")
    assert hasattr(mod, "PolicyTrainingOrchestrator")


def test_pytorch_provider_resolves_conditionally() -> None:
    from townlet.config.loader import load_config
    from townlet.core.factory_registry import resolve_policy
    from townlet.policy.fallback import StubPolicyBackend
    from townlet.policy.models import torch_available
    from townlet.policy.runner import PolicyRuntime

    project_root = Path(__file__).resolve().parents[1]
    cfg = load_config(project_root / "configs" / "examples" / "poc_hybrid.yaml")

    backend = resolve_policy("pytorch", config=cfg)
    if torch_available():
        assert isinstance(backend, PolicyRuntime)
    else:
        assert isinstance(backend, StubPolicyBackend)
