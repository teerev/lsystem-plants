from __future__ import annotations

from pathlib import Path


def test_sanity_check() -> None:
    assert 1 + 1 == 2


def test_fixture_available_and_writable(tmp_output_dir: Path) -> None:
    assert tmp_output_dir.exists()
    assert tmp_output_dir.is_dir()

    p = tmp_output_dir / "hello.txt"
    p.write_text("hello", encoding="utf-8")
    assert p.read_text(encoding="utf-8") == "hello"


def test_package_importable() -> None:
    import lsystem  # noqa: F401
