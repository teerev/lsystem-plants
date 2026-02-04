from __future__ import annotations

from pathlib import Path

import pytest

from lsystem.cli import main


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--help"])
    assert code == 0
    out = capsys.readouterr().out
    assert "usage:" in out.lower()
    assert "list" in out
    assert "render" in out


def test_cli_list(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["list"])
    assert code == 0
    out = capsys.readouterr().out
    assert "fern" in out
    assert "weed" in out


def test_cli_render_preset_creates_default_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    code = main(["render", "fern"])
    assert code == 0
    p = tmp_path / "fern.svg"
    assert p.exists()
    content = p.read_text(encoding="utf-8")
    assert content.startswith("<svg")


def test_cli_render_custom_output(tmp_path: Path) -> None:
    out = tmp_path / "custom.svg"
    code = main(["render", "fern", "--output", str(out)])
    assert code == 0
    assert out.exists()


def test_cli_invalid_preset_exits_1(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["render", "nope"])
    assert code == 1
    err = capsys.readouterr().err
    assert "unknown preset" in err


def test_cli_override_iterations_changes_output(tmp_path: Path) -> None:
    out1 = tmp_path / "a.svg"
    out2 = tmp_path / "b.svg"
    code1 = main(["render", "fern", "--output", str(out1), "--iterations", "1"])
    code2 = main(["render", "fern", "--output", str(out2), "--iterations", "2"])
    assert code1 == 0
    assert code2 == 0
    assert out1.read_text(encoding="utf-8") != out2.read_text(encoding="utf-8")


def test_cli_render_custom_dimensions(tmp_path: Path) -> None:
    out = tmp_path / "dim.svg"
    code = main(["render", "fern", "--output", str(out), "--width", "123", "--height", "45"])
    assert code == 0
    txt = out.read_text(encoding="utf-8")
    assert 'width="123"' in txt
    assert 'height="45"' in txt
