from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Temporary directory for tests that need to write output files.

    This wraps pytest's built-in tmp_path to provide a semantically-named fixture
    for future SVG/image output tests.
    """
    out_dir = tmp_path / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir
