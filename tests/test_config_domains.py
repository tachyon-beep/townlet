from __future__ import annotations

import pytest

from townlet.config.runtime import RuntimeProviderConfig
from townlet.config.telemetry import TelemetryTransformEntry
from townlet.config.world_config import BehaviorConfig, EmploymentConfig


def test_runtime_provider_config_coerces_from_string() -> None:
    cfg = RuntimeProviderConfig.model_validate("scripted")
    assert cfg.provider == "scripted"
    assert isinstance(cfg.options, dict)


def test_world_behavior_defaults() -> None:
    behavior = BehaviorConfig()
    assert 0.0 <= behavior.hunger_threshold <= 1.0
    assert 0.0 <= behavior.hygiene_threshold <= 1.0
    assert 0.0 <= behavior.energy_threshold <= 1.0
    assert behavior.job_arrival_buffer >= 0


def test_world_employment_defaults() -> None:
    emp = EmploymentConfig()
    assert emp.grace_ticks >= 0
    assert emp.absent_cutoff >= 0
    assert emp.max_absent_shifts >= 0
    assert isinstance(emp.enforce_job_loop, bool)


def test_telemetry_transform_entry_invalid_options_type() -> None:
    with pytest.raises(TypeError):
        TelemetryTransformEntry.model_validate({"id": "redact_fields", "options": 123})

