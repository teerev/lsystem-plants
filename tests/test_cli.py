from __future__ import annotations

import re
from pathlib import Path

import pytest

from lsystem.cli import main


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as e:
        # argparse exits with 0
        raise SystemExit(main(["--help"]))
    assert e.value.code == 0
    out = capsys.readouterr().out
    assert "list" in out
    assert "render" in out


def test_cli_list_shows_presets(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["list"])
    assert code == 0
    out = capsys.readouterr().out
    # at least one known preset
    assert "fern" in out


def test_cli_render_default_output_creates_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    code = main(["render", "fern"])
    assert code == 0
    out_path = tmp_path / "fern.svg"
    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert content.lstrip().startswith("<svg")


def test_cli_render_custom_output(tmp_path: Path) -> None:
    out_path = tmp_path / "custom.svg"
    code = main(["render", "fern", "--output", str(out_path)])
    assert code == 0
    assert out_path.exists()


def test_cli_invalid_preset_exits_1(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["render", "not-a-preset"])
    assert code == 1
    err = capsys.readouterr().err
    assert "unknown preset" in err


def test_cli_override_dimensions_affect_svg(tmp_path: Path) -> None:
    out_path = tmp_path / "dim.svg"
    code = main(
        [
            "render",
            "fern",
            "--output",
            str(out_path),
            "--width",
            "123",
            "--height",
            "77",
        ]
    )
    assert code == 0
    content = out_path.read_text(encoding="utf-8")
    assert re.search(r'width="123"', content)
    assert re.search(r'height="77"', content)


def test_cli_override_iterations_changes_output(tmp_path: Path) -> None:
    out1 = tmp_path / "i1.svg"
    out2 = tmp_path / "i2.svg"

    code1 = main(["render", "weed", "--output", str(out1), "--iterations", "1"])
    code2 = main(["render", "weed", "--output", str(out2), "--iterations", "3"])
    assert code1 == 0
    assert code2 == 0

    # More iterations should generally yield more segments -> larger SVG content
    c1 = out1.read_text(encoding="utf-8")
    c2 = out2.read_text(encoding="utf-8")
    assert len(c2) > len(c1)
