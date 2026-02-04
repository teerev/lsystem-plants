from __future__ import annotations

import re
from pathlib import Path

from lsystem.render_svg import render_svg, save_svg
from lsystem.turtle import Segment


def test_svg_valid_structure() -> None:
    svg = render_svg([Segment((0.0, 0.0), (10.0, 0.0))])
    assert svg.startswith("<svg")
    assert svg.strip().endswith("</svg>")


def test_svg_deterministic() -> None:
    segs = [Segment((0.0, 0.0), (10.0, 5.0)), Segment((10.0, 5.0), (20.0, 25.0))]
    a = render_svg(segs)
    b = render_svg(segs)
    assert a == b


def test_float_precision_4_decimals() -> None:
    svg = render_svg([Segment((0.1, 0.2), (0.3, 0.4))])
    floats = re.findall(r"\"(-?\d+\.\d+)\"", svg)
    assert floats, "expected float attributes in SVG"
    assert all(len(s.split(".")[1]) == 4 for s in floats)


def test_custom_stroke_and_width_present() -> None:
    svg = render_svg(
        [Segment((0.0, 0.0), (1.0, 1.0))],
        stroke="#ff0000",
        stroke_width=2.5,
    )
    assert 'stroke="#ff0000"' in svg
    assert 'stroke-width="2.5000"' in svg


def test_segments_rendered_count_matches() -> None:
    segs = [
        Segment((0.0, 0.0), (1.0, 0.0)),
        Segment((1.0, 0.0), (1.0, 1.0)),
        Segment((1.0, 1.0), (0.0, 1.0)),
    ]
    svg = render_svg(segs)
    assert svg.count("<line ") == len(segs)


def test_empty_segments_minimal_svg() -> None:
    svg = render_svg([])
    assert "<line" not in svg
    assert svg.startswith("<svg")
    assert svg.strip().endswith("</svg>")


def test_save_creates_file(tmp_path: Path) -> None:
    # Small canvas should not fail even with default padding; padding is clamped.
    content = render_svg([Segment((0.0, 0.0), (1.0, 1.0))], width=10, height=10)
    out = tmp_path / "out.svg"
    save_svg(content, out)
    assert out.exists()
    assert out.read_text(encoding="utf-8") == content


def test_padding_clamped_small_canvas_no_error() -> None:
    svg = render_svg([Segment((0.0, 0.0), (1.0, 1.0))], width=10, height=10, padding=20.0)
    assert svg.startswith("<svg")
    assert svg.count("<line ") == 1
