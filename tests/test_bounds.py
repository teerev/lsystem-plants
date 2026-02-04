import pytest

from lsystem.bounds import BoundingBox, compute_bounds, transform_segments
from lsystem.turtle import Segment


def test_single_segment_bounds():
    segs = [Segment((0.0, 0.0), (2.0, 3.0))]
    b = compute_bounds(segs)
    assert b is not None
    assert b.min_x == 0.0
    assert b.min_y == 0.0
    assert b.max_x == 2.0
    assert b.max_y == 3.0
    assert b.width == 2.0
    assert b.height == 3.0
    assert b.center == (1.0, 1.5)


def test_multiple_segments_bounds_negative_coords():
    segs = [
        Segment((-1.0, 2.0), (3.0, 4.0)),
        Segment((0.0, -2.0), (2.0, 1.0)),
    ]
    b = compute_bounds(segs)
    assert b is not None
    assert b.min_x == -1.0
    assert b.min_y == -2.0
    assert b.max_x == 3.0
    assert b.max_y == 4.0


def test_transform_fits_canvas_and_centering():
    # A 2x1 rectangle centered at (1, 0.5)
    segs = [
        Segment((0.0, 0.0), (2.0, 0.0)),
        Segment((2.0, 0.0), (2.0, 1.0)),
        Segment((2.0, 1.0), (0.0, 1.0)),
        Segment((0.0, 1.0), (0.0, 0.0)),
    ]

    out = transform_segments(segs, width=10.0, height=10.0)
    b = compute_bounds(out)
    assert b is not None

    # Should fit within the canvas
    assert b.min_x >= 0.0
    assert b.min_y >= 0.0
    assert b.max_x <= 10.0
    assert b.max_y <= 10.0

    # Should be centered
    cx, cy = b.center
    assert cx == pytest.approx(5.0)
    assert cy == pytest.approx(5.0)

    # Aspect ratio preserved: original w/h = 2.0, scaled should be same.
    assert (b.width / b.height) == pytest.approx(2.0)


def test_transform_with_padding_respects_margins():
    segs = [Segment((0.0, 0.0), (2.0, 0.0))]

    out = transform_segments(segs, width=10.0, height=10.0, padding=2.0)
    b = compute_bounds(out)
    assert b is not None

    # Drawing must lie within padded area [2,8] for x and y.
    assert b.min_x >= 2.0 - 1e-9
    assert b.max_x <= 8.0 + 1e-9
    assert b.min_y >= 2.0 - 1e-9
    assert b.max_y <= 8.0 + 1e-9


def test_empty_segments_handled_gracefully():
    assert compute_bounds([]) is None
    with pytest.raises(ValueError):
        transform_segments([], width=10.0, height=10.0)
