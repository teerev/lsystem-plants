import math

import pytest

from lsystem.bounds import BoundingBox, compute_bounds, transform_segments
from lsystem.turtle import Segment


def _bounds_of_points(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def _segments_points(segs):
    pts = []
    for s in segs:
        pts.append(s.start)
        pts.append(s.end)
    return pts


def test_bounding_box_properties():
    b = BoundingBox(min_x=-1.0, min_y=2.0, max_x=3.0, max_y=10.0)
    assert b.width == 4.0
    assert b.height == 8.0
    assert b.center == (1.0, 6.0)


def test_single_segment_bounds():
    segs = [Segment(start=(1.0, 2.0), end=(5.0, -1.0))]
    b = compute_bounds(segs)
    assert b is not None
    assert b.min_x == 1.0
    assert b.max_x == 5.0
    assert b.min_y == -1.0
    assert b.max_y == 2.0


def test_multiple_segments_bounds():
    segs = [
        Segment(start=(-2.0, 1.0), end=(3.0, 4.0)),
        Segment(start=(3.0, 4.0), end=(0.0, -5.0)),
        Segment(start=(10.0, 2.0), end=(7.0, -1.0)),
    ]
    b = compute_bounds(segs)
    assert b is not None
    assert (b.min_x, b.min_y, b.max_x, b.max_y) == (-2.0, -5.0, 10.0, 4.0)


def test_empty_segments_bounds_returns_none():
    assert compute_bounds([]) is None


def test_transform_fits_canvas_and_centers():
    # Rectangle 4x2 centered at (2,1)
    segs = [
        Segment(start=(0.0, 0.0), end=(4.0, 0.0)),
        Segment(start=(4.0, 0.0), end=(4.0, 2.0)),
        Segment(start=(4.0, 2.0), end=(0.0, 2.0)),
        Segment(start=(0.0, 2.0), end=(0.0, 0.0)),
    ]

    out = transform_segments(segs, width=100.0, height=50.0, padding=0.0)
    pts = _segments_points(out)
    min_x, min_y, max_x, max_y = _bounds_of_points(pts)

    assert min_x >= 0.0 - 1e-9
    assert min_y >= 0.0 - 1e-9
    assert max_x <= 100.0 + 1e-9
    assert max_y <= 50.0 + 1e-9

    # Centering: transformed bounds center should match canvas center.
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    assert abs(cx - 50.0) < 1e-9
    assert abs(cy - 25.0) < 1e-9


def test_transform_with_padding_respects_margins():
    segs = [
        Segment(start=(0.0, 0.0), end=(10.0, 0.0)),
        Segment(start=(10.0, 0.0), end=(10.0, 10.0)),
    ]

    out = transform_segments(segs, width=100.0, height=100.0, padding=10.0)
    pts = _segments_points(out)
    min_x, min_y, max_x, max_y = _bounds_of_points(pts)

    assert min_x >= 10.0 - 1e-9
    assert min_y >= 10.0 - 1e-9
    assert max_x <= 90.0 + 1e-9
    assert max_y <= 90.0 + 1e-9


def test_transform_preserves_aspect_ratio_uniform_scaling():
    # Use two perpendicular segments to detect non-uniform scaling.
    segs = [
        Segment(start=(0.0, 0.0), end=(10.0, 0.0)),  # horizontal length 10
        Segment(start=(0.0, 0.0), end=(0.0, 5.0)),   # vertical length 5
    ]

    out = transform_segments(segs, width=200.0, height=200.0, padding=0.0)

    h = out[0]
    v = out[1]

    h_len = math.hypot(h.end[0] - h.start[0], h.end[1] - h.start[1])
    v_len = math.hypot(v.end[0] - v.start[0], v.end[1] - v.start[1])

    # Original ratio is 10:5 => 2
    assert abs((h_len / v_len) - 2.0) < 1e-9


def test_transform_degenerate_single_point_centers_to_canvas():
    segs = [Segment(start=(3.0, 4.0), end=(3.0, 4.0))]
    out = transform_segments(segs, width=10.0, height=20.0, padding=0.0)
    assert len(out) == 1
    assert out[0].start == out[0].end
    assert abs(out[0].start[0] - 5.0) < 1e-12
    assert abs(out[0].start[1] - 10.0) < 1e-12


def test_transform_padding_too_large_raises():
    segs = [Segment(start=(0.0, 0.0), end=(1.0, 1.0))]
    with pytest.raises(ValueError):
        transform_segments(segs, width=10.0, height=10.0, padding=6.0)
