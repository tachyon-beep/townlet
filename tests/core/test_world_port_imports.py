from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TARGET_DIRS = (
    ROOT / "src" / "townlet" / "core",
    ROOT / "src" / "townlet" / "factories",
    ROOT / "src" / "townlet" / "orchestration",
    ROOT / "src" / "townlet" / "testing",
    ROOT / "src" / "townlet" / "telemetry",
)
FORBIDDEN_IMPORT = "from townlet.core.interfaces import WorldRuntimeProtocol"


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for directory in TARGET_DIRS:
        if not directory.exists():
            continue
        files.extend(directory.rglob("*.py"))
    return files


@pytest.mark.parametrize("path", _iter_python_files(), ids=str)
def test_world_runtime_protocol_not_imported(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert (
        FORBIDDEN_IMPORT not in text
    ), "WorldRuntimeProtocol import is deprecated; import WorldRuntime from townlet.ports.world"
