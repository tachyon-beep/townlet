"""Pytest configuration ensuring project imports resolve during tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.runtime_stubs import StubAffordanceRuntime

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for path in (SRC, ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "slow: marks tests as slow")


@pytest.fixture
def stub_affordance_runtime_factory():
    def _factory(world, context):
        return StubAffordanceRuntime(context)

    return _factory
