from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "lsystem", *args],
        cwd=str(cwd) if cwd is not None else None,
        text=True,
        capture_output=True,
    )


def test_cli_help() -> None:
    res = _run_cli("--help")
    assert res.returncode == 0
    assert "list" in res.stdout
    assert "render" in res.stdout


def test_cli_list_contains_presets() -> None:
    res = _run_cli("list")
    assert res.returncode == 0
    # at least one known preset
    assert "fern" in res.stdout
    assert "weed" in res.stdout


def test_cli_render_default_output_creates_svg(tmp_path: Path) -> None:
    res = _run_cli("render", "fern", cwd=tmp_path)
    assert res.returncode == 0
    out = tmp_path / "fern.svg"
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert content.startswith("<svg")
    assert "<line" in content
    assert "Rendered 'fern'" in res.stderr


def test_cli_render_custom_output(tmp_path: Path) -> None:
    out = tmp_path / "custom.svg"
    res = _run_cli("render", "fern", "--output", str(out), cwd=tmp_path)
    assert res.returncode == 0
    assert out.exists()


def test_cli_invalid_preset_exits_1() -> None:
    res = _run_cli("render", "does_not_exist")
    assert res.returncode == 1
    assert "unknown preset" in res.stderr


def test_cli_override_iterations_changes_output(tmp_path: Path) -> None:
    out1 = tmp_path / "a.svg"
    out2 = tmp_path / "b.svg"

    res1 = _run_cli("render", "weed", "--iterations", "1", "--output", str(out1), cwd=tmp_path)
    res2 = _run_cli("render", "weed", "--iterations", "2", "--output", str(out2), cwd=tmp_path)

    assert res1.returncode == 0
    assert res2.returncode == 0

    c1 = out1.read_text(encoding="utf-8")
    c2 = out2.read_text(encoding="utf-8")

    # more iterations should generally produce more line segments
    assert c1.count("<line") < c2.count("<line")


def test_cli_render_custom_dimensions(tmp_path: Path) -> None:
    out = tmp_path / "dim.svg"
    res = _run_cli(
        "render",
        "fern",
        "--width",
        "321",
        "--height",
        "123",
        "--output",
        str(out),
        cwd=tmp_path,
    )
    assert res.returncode == 0
    content = out.read_text(encoding="utf-8")
    assert 'width="321"' in content
    assert 'height="123"' in content
