from __future__ import annotations

from pathlib import Path

import pytest

from lsystem.render_svg import render_svg, save_svg
from lsystem.turtle import Segment


def _simple_segments() -> list[Segment]:
    # Not pre-transformed; render_svg must scale/center these.
    return [
        Segment(start=(0.0, 0.0), end=(10.0, 0.0)),
        Segment(start=(10.0, 0.0), end=(10.0, 10.0)),
    ]


def test_svg_valid_structure() -> None:
    svg = render_svg(_simple_segments(), width=200, height=100)
    assert svg.startswith("<svg ")
    assert svg.endswith("</svg>\n")
    assert "xmlns=\"http://www.w3.org/2000/svg\"" in svg


def test_svg_deterministic() -> None:
    segs = _simple_segments()
    svg1 = render_svg(segs, width=200, height=100)
    svg2 = render_svg(segs, width=200, height=100)
    assert svg1 == svg2


def test_float_precision_4dp() -> None:
    segs = [Segment(start=(0.123456, 1.0), end=(2.0, 3.987654))]
    svg = render_svg(segs, width=100, height=100, padding=0.0)
    # stroke-width and coordinates must be formatted with exactly 4 decimals.
    assert "stroke-width=\"1.0000\"" in svg
    for attr in ["x1=\"", "y1=\"", "x2=\"", "y2=\""]:
        idx = svg.index(attr) + len(attr)
        num = svg[idx : idx + 10]  # e.g. 12.3456 (at least)
        # First token ends at quote
        num = num.split('"', 1)[0]
        assert "." in num
        assert len(num.split(".", 1)[1]) == 4


def test_custom_stroke_and_width() -> None:
    svg = render_svg(_simple_segments(), width=200, height=100, stroke="#000000", stroke_width=2.5)
    assert "stroke=\"#000000\"" in svg
    assert "stroke-width=\"2.5000\"" in svg


def test_segments_rendered_count() -> None:
    segs = _simple_segments()
    svg = render_svg(segs, width=200, height=100)
    assert svg.count("<line ") == len(segs)


def test_empty_segments_valid_minimal_svg() -> None:
    svg = render_svg([], width=200, height=100)
    assert svg.startswith("<svg ")
    assert "<line" not in svg
    assert svg == (
        '<svg height="100" viewBox="0 0 200 100" width="200" xmlns="http://www.w3.org/2000/svg">\n'
        "</svg>\n"
    )


def test_save_creates_file(tmp_path: Path) -> None:
    content = render_svg(_simple_segments(), width=120, height=80)
    out = tmp_path / "out.svg"
    save_svg(content, out)
    assert out.exists()
    assert out.read_text(encoding="utf-8") == content


def test_svg_attribute_ordering_line() -> None:
    svg = render_svg([Segment(start=(0.0, 0.0), end=(1.0, 1.0))], width=10, height=10, padding=0.0)
    # Ensure alphabetical ordering in the <line .../> element.
    line = [ln for ln in svg.splitlines() if ln.strip().startswith("<line ")][0]
    ix = [line.index(k) for k in ["x1=", "x2=", "y1=", "y2=", "stroke=", "stroke-width="]]
    assert ix == sorted(ix)
