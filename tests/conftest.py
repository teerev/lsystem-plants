from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Temporary output directory for tests that write files.

    Using a dedicated subdir keeps outputs separate from other tmp_path usage.
    """

    out = tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)
    return out
