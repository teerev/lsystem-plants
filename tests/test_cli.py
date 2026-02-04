from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def _run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "lsystem", *argv],
        cwd=str(cwd),
        text=True,
        capture_output=True,
    )


def test_cli_help(tmp_path: Path) -> None:
    p = _run(["--help"], cwd=tmp_path)
    assert p.returncode == 0
    assert "usage" in p.stdout.lower() or "usage" in p.stderr.lower()
    assert "list" in (p.stdout + p.stderr)
    assert "render" in (p.stdout + p.stderr)


def test_cli_list_shows_presets(tmp_path: Path) -> None:
    p = _run(["list"], cwd=tmp_path)
    assert p.returncode == 0
    out = p.stdout
    assert "fern" in out
    assert "weed" in out
    assert "bush" in out


def test_cli_render_creates_default_output(tmp_path: Path) -> None:
    p = _run(["render", "fern"], cwd=tmp_path)
    assert p.returncode == 0
    out_file = tmp_path / "fern.svg"
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert content.startswith("<svg")
    assert "<line" in content
    assert "Wrote" in p.stderr


def test_cli_render_custom_output(tmp_path: Path) -> None:
    out_file = tmp_path / "custom.svg"
    p = _run(["render", "fern", "--output", str(out_file)], cwd=tmp_path)
    assert p.returncode == 0
    assert out_file.exists()


def test_cli_invalid_preset_exits_1(tmp_path: Path) -> None:
    p = _run(["render", "nope"], cwd=tmp_path)
    assert p.returncode == 1
    assert "unknown preset" in p.stderr.lower()


def test_cli_override_dimensions(tmp_path: Path) -> None:
    p = _run(["render", "fern", "--width", "321", "--height", "123"], cwd=tmp_path)
    assert p.returncode == 0
    content = (tmp_path / "fern.svg").read_text(encoding="utf-8")
    assert 'viewBox="0 0 321 123"' in content
    assert 'width="321"' in content
    assert 'height="123"' in content


def test_cli_override_iterations_changes_output(tmp_path: Path) -> None:
    p1 = _run(["render", "weed", "--output", "a.svg", "--iterations", "1"], cwd=tmp_path)
    p2 = _run(["render", "weed", "--output", "b.svg", "--iterations", "3"], cwd=tmp_path)
    assert p1.returncode == 0
    assert p2.returncode == 0
    a = (tmp_path / "a.svg").read_text(encoding="utf-8")
    b = (tmp_path / "b.svg").read_text(encoding="utf-8")
    assert a != b
