from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "lsystem", *args],
        cwd=str(cwd) if cwd is not None else None,
        text=True,
        capture_output=True,
    )


def test_cli_help() -> None:
    p = _run("--help")
    assert p.returncode == 0
    assert "Generate L-system plant SVG images" in p.stdout
    assert "list" in p.stdout
    assert "render" in p.stdout


def test_cli_list_contains_presets() -> None:
    p = _run("list")
    assert p.returncode == 0
    # Names should appear in stdout output lines
    assert "fern" in p.stdout
    assert "weed" in p.stdout
    assert "bush" in p.stdout


def test_cli_render_default_output_creates_svg(tmp_path: Path) -> None:
    p = _run("render", "fern", cwd=tmp_path)
    assert p.returncode == 0
    out = tmp_path / "fern.svg"
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert text.startswith("<svg")
    assert "<line" in text


def test_cli_render_custom_output_path(tmp_path: Path) -> None:
    out = tmp_path / "custom.svg"
    p = _run("render", "fern", "--output", str(out), cwd=tmp_path)
    assert p.returncode == 0
    assert out.is_file()


def test_cli_invalid_preset_exits_1() -> None:
    p = _run("render", "not-a-preset")
    assert p.returncode == 1
    assert "unknown preset" in p.stderr


def test_cli_override_dimensions_affect_svg(tmp_path: Path) -> None:
    out = tmp_path / "dim.svg"
    p = _run(
        "render",
        "fern",
        "--output",
        str(out),
        "--width",
        "123",
        "--height",
        "77",
        cwd=tmp_path,
    )
    assert p.returncode == 0
    text = out.read_text(encoding="utf-8")
    assert 'width="123"' in text
    assert 'height="77"' in text
    assert 'viewBox="0 0 123 77"' in text


def test_cli_output_path_is_directory_user_error(tmp_path: Path) -> None:
    out_dir = tmp_path / "outdir"
    out_dir.mkdir()
    p = _run("render", "fern", "--output", str(out_dir), cwd=tmp_path)
    assert p.returncode == 1
    assert "directory" in p.stderr


def test_cli_progress_prints_to_stderr(tmp_path: Path) -> None:
    p = _run("render", "fern", cwd=tmp_path)
    assert p.returncode == 0
    assert "Rendering preset" in p.stderr
    assert "Wrote" in p.stderr
