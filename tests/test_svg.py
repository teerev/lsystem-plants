import re
from pathlib import Path

from lsystem.render_svg import render_svg, save_svg
from lsystem.turtle import Segment


def _segments_simple():
    return [
        Segment((0.0, 0.0), (10.0, 0.0)),
        Segment((10.0, 0.0), (10.0, 5.0)),
    ]


def test_svg_valid_structure():
    svg = render_svg(_segments_simple(), width=200, height=100)
    assert svg.startswith("<svg ")
    assert svg.endswith("</svg>\n")
    assert "xmlns=\"http://www.w3.org/2000/svg\"" in svg


def test_svg_deterministic():
    segs = _segments_simple()
    svg1 = render_svg(segs, width=200, height=100, padding=10.0)
    svg2 = render_svg(segs, width=200, height=100, padding=10.0)
    assert svg1 == svg2


def test_float_precision_exact_4dp_everywhere_in_line_elements():
    segs = [Segment((0.123456, 1.0), (2.0, 3.987654))]
    svg = render_svg(segs, width=200, height=100, padding=0.0, stroke_width=1.25)

    # Pull all numeric attributes from <line .../> and ensure 4 decimals.
    line = next(l for l in svg.splitlines() if l.startswith("<line "))
    nums = re.findall(r'="(-?\d+\.\d+)"', line)
    assert nums, "expected numeric attributes in <line>"
    assert all(re.fullmatch(r"-?\d+\.\d{4}", n) for n in nums)


def test_custom_stroke_and_width_reflected():
    svg = render_svg(
        _segments_simple(),
        width=200,
        height=100,
        stroke="#ff0000",
        stroke_width=2.5,
        padding=0.0,
    )
    assert 'stroke="#ff0000"' in svg
    assert 'stroke-width="2.5000"' in svg


def test_segments_rendered_line_count_matches():
    segs = _segments_simple()
    svg = render_svg(segs, width=200, height=100, padding=0.0)
    assert svg.count("<line ") == len(segs)


def test_autoscale_fits_viewbox_bounds():
    # Very wide shape should be scaled down and centered to fit.
    segs = [Segment((0.0, 0.0), (1000.0, 0.0))]
    width, height, pad = 200, 100, 10.0
    svg = render_svg(segs, width=width, height=height, padding=pad)

    line = next(l for l in svg.splitlines() if l.startswith("<line "))
    vals = dict(re.findall(r'(x1|y1|x2|y2)="(-?\d+\.\d{4})"', line))
    x1 = float(vals["x1"])
    x2 = float(vals["x2"])
    y1 = float(vals["y1"])
    y2 = float(vals["y2"])

    for v in (x1, x2):
        assert pad - 1e-6 <= v <= (width - pad) + 1e-6
    for v in (y1, y2):
        assert pad - 1e-6 <= v <= (height - pad) + 1e-6


def test_empty_segments_minimal_svg():
    svg = render_svg([], width=200, height=100)
    assert svg.splitlines()[0].startswith("<svg ")
    assert svg.strip().endswith("</svg>")
    assert "<line" not in svg


def test_save_creates_file(tmp_path: Path):
    content = render_svg(_segments_simple(), width=200, height=100)
    out = tmp_path / "out" / "plant.svg"
    save_svg(content, out)
    assert out.exists()
    assert out.read_text(encoding="utf-8") == content
