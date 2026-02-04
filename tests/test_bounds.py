import pytest

from lsystem.bounds import compute_bounds, transform_segments
from lsystem.turtle import Segment


def _all_points(segments: list[Segment]) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for s in segments:
        pts.append(s.start)
        pts.append(s.end)
    return pts


def test_single_segment_bounds() -> None:
    segs = [Segment((1.0, 2.0), (3.0, 5.0))]
    b = compute_bounds(segs)
    assert b is not None
    assert b.min_x == 1.0
    assert b.min_y == 2.0
    assert b.max_x == 3.0
    assert b.max_y == 5.0


def test_multiple_segments_bounds() -> None:
    segs = [
        Segment((-1.0, 0.0), (2.0, 3.0)),
        Segment((10.0, -5.0), (0.0, 1.0)),
    ]
    b = compute_bounds(segs)
    assert b is not None
    assert b.min_x == -1.0
    assert b.min_y == -5.0
    assert b.max_x == 10.0
    assert b.max_y == 3.0


def test_empty_segments() -> None:
    assert compute_bounds([]) is None
    assert transform_segments([], 100.0, 100.0) == []


def test_transform_fits_canvas_and_centering() -> None:
    # 10x20 box, should scale by min(100/10, 50/20)=2.5 => 25x50, centered
    segs = [Segment((0.0, 0.0), (10.0, 20.0))]
    out = transform_segments(segs, width=100.0, height=50.0, padding=0.0)
    b = compute_bounds(out)
    assert b is not None
    assert pytest.approx(b.width, rel=1e-9, abs=1e-9) == 25.0
    assert pytest.approx(b.height, rel=1e-9, abs=1e-9) == 50.0

    # bounds should be fully inside canvas
    assert b.min_x >= 0.0
    assert b.min_y >= 0.0
    assert b.max_x <= 100.0
    assert b.max_y <= 50.0

    # centered
    cx, cy = b.center
    assert pytest.approx(cx, rel=1e-9, abs=1e-9) == 50.0
    assert pytest.approx(cy, rel=1e-9, abs=1e-9) == 25.0


def test_transform_with_padding_reduces_available_space() -> None:
    segs = [Segment((0.0, 0.0), (10.0, 20.0))]
    out = transform_segments(segs, width=100.0, height=50.0, padding=5.0)
    b = compute_bounds(out)
    assert b is not None

    # Available canvas: 90x40, scale=min(90/10,40/20)=2.0 => 20x40
    assert pytest.approx(b.width, rel=1e-9, abs=1e-9) == 20.0
    assert pytest.approx(b.height, rel=1e-9, abs=1e-9) == 40.0

    # Inside padded region
    assert b.min_x >= 5.0
    assert b.min_y >= 5.0
    assert b.max_x <= 95.0
    assert b.max_y <= 45.0


def test_aspect_ratio_preserved_uniform_scale() -> None:
    # Two distinct segments with different deltas; scaling should be uniform in x/y.
    segs = [Segment((0.0, 0.0), (10.0, 0.0)), Segment((0.0, 0.0), (0.0, 20.0))]
    out = transform_segments(segs, width=100.0, height=50.0, padding=0.0)

    # Infer scale from transformed extents.
    b_in = compute_bounds(segs)
    b_out = compute_bounds(out)
    assert b_in is not None and b_out is not None

    scale_x = b_out.width / b_in.width
    scale_y = b_out.height / b_in.height
    assert pytest.approx(scale_x, rel=1e-12, abs=1e-12) == scale_y

    # Also ensure all points are within canvas
    for x, y in _all_points(out):
        assert 0.0 <= x <= 100.0
        assert 0.0 <= y <= 50.0
