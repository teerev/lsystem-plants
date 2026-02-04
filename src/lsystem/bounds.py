from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from lsystem.turtle import Segment


@dataclass(frozen=True)
class BoundingBox:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self) -> float:
        return self.max_x - self.min_x

    @property
    def height(self) -> float:
        return self.max_y - self.min_y

    @property
    def center(self) -> Tuple[float, float]:
        return ((self.min_x + self.max_x) / 2.0, (self.min_y + self.max_y) / 2.0)


def compute_bounds(segments: List[Segment]) -> Optional[BoundingBox]:
    """Compute axis-aligned bounds for a list of line segments.

    Returns None for an empty segment list.
    """

    if not segments:
        return None

    # Seed with first endpoint for determinism and simplicity.
    x0, y0 = segments[0].start
    min_x = max_x = float(x0)
    min_y = max_y = float(y0)

    for seg in segments:
        for (x, y) in (seg.start, seg.end):
            fx = float(x)
            fy = float(y)
            if fx < min_x:
                min_x = fx
            if fx > max_x:
                max_x = fx
            if fy < min_y:
                min_y = fy
            if fy > max_y:
                max_y = fy

    return BoundingBox(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)


def transform_segments(
    segments: List[Segment],
    width: float,
    height: float,
    padding: float = 0.0,
) -> List[Segment]:
    """Scale + translate segments to fit inside a target canvas.

    - Uniform scaling (aspect ratio preserved)
    - Centering (bounds center maps to canvas center)
    - Padding is absolute units and reduces available drawable area on all sides.

    Empty input returns an empty list.
    """

    if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
        raise ValueError("width and height must be numbers")
    if not isinstance(padding, (int, float)):
        raise ValueError("padding must be a number")

    w = float(width)
    h = float(height)
    pad = float(padding)

    if w <= 0 or h <= 0:
        raise ValueError("width and height must be positive")
    if pad < 0:
        raise ValueError("padding must be non-negative")

    if not segments:
        return []

    bounds = compute_bounds(segments)
    if bounds is None:
        return []

    avail_w = w - 2.0 * pad
    avail_h = h - 2.0 * pad
    if avail_w <= 0 or avail_h <= 0:
        raise ValueError("padding too large for the target canvas")

    bw = bounds.width
    bh = bounds.height

    # Handle degenerate cases (single point / zero-area bounds):
    # put everything at canvas center (deterministic) and do not scale.
    if bw == 0.0 and bh == 0.0:
        cx, cy = bounds.center
        tx = (w / 2.0) - cx
        ty = (h / 2.0) - cy

        def _t(p: Tuple[float, float]) -> Tuple[float, float]:
            return (p[0] + tx, p[1] + ty)

        return [Segment(start=_t(s.start), end=_t(s.end)) for s in segments]

    # Uniform scaling; if one dimension is zero, scale from the other.
    if bw == 0.0:
        scale = avail_h / bh
    elif bh == 0.0:
        scale = avail_w / bw
    else:
        scale = min(avail_w / bw, avail_h / bh)

    bx, by = bounds.center
    target_cx = w / 2.0
    target_cy = h / 2.0

    def _transform_point(p: Tuple[float, float]) -> Tuple[float, float]:
        x, y = float(p[0]), float(p[1])
        # Translate to origin at bounds center, scale, then translate to canvas center.
        return ((x - bx) * scale + target_cx, (y - by) * scale + target_cy)

    return [
        Segment(start=_transform_point(seg.start), end=_transform_point(seg.end))
        for seg in segments
    ]
