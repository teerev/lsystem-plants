from __future__ import annotations

from pathlib import Path


def test_sanity_check() -> None:
    assert 1 + 1 == 2


def test_fixture_available(tmp_output_dir: Path) -> None:
    assert tmp_output_dir.exists()
    assert tmp_output_dir.is_dir()


def test_package_import() -> None:
    import lsystem

    assert hasattr(lsystem, "__version__")
