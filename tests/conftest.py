from __future__ import annotations

from collections.abc import Iterator

import pytest


@pytest.fixture
def tmp_output_dir(tmp_path) -> Iterator[object]:
    """Temporary output directory for tests that write files.

    Using a named fixture makes future I/O tests (e.g., SVG exports) consistent.
    """
    out_dir = tmp_path / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    yield out_dir
