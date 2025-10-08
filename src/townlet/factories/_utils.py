"""Factory utility helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .registry import ConfigurationError


def extract_provider(cfg: Any, kind: str, default: str) -> tuple[str, Mapping[str, Any]]:
    """Extract the provider key and options for ``kind`` from ``cfg``."""

    runtime_cfg = getattr(cfg, "runtime", None)
    provider = default
    options: Mapping[str, Any] = {}
    if runtime_cfg is None and isinstance(cfg, Mapping):
        runtime_cfg = cfg.get("runtime")
    if runtime_cfg is not None:
        domain_cfg = getattr(runtime_cfg, kind, None)
        if domain_cfg is None and isinstance(runtime_cfg, Mapping):
            domain_cfg = runtime_cfg.get(kind)
        if domain_cfg is not None:
            provider = getattr(domain_cfg, "provider", provider)
            if isinstance(domain_cfg, Mapping):
                provider = domain_cfg.get("provider", provider)
                options = domain_cfg.get("options", {})
            else:
                options = getattr(domain_cfg, "options", {})
    provider = (provider or default).strip()
    if not provider:
        provider = default
    if not isinstance(options, Mapping):
        raise ConfigurationError(f"{kind} options must be a mapping, got {type(options)!r}")
    return provider, options


__all__ = ["extract_provider"]
