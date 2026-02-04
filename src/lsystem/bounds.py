from __future__ import annotations

from dataclasses import dataclass

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
    def center(self) -> tuple[float, float]:
        return ((self.min_x + self.max_x) / 2.0, (self.min_y + self.max_y) / 2.0)


def compute_bounds(segments: list[Segment]) -> BoundingBox | None:
    """Compute axis-aligned bounds of segment endpoints.

    Returns None for an empty segment list.
    """

    if not segments:
        return None

    xs: list[float] = []
    ys: list[float] = []

    for seg in segments:
        (x1, y1) = seg.start
        (x2, y2) = seg.end
        xs.extend([float(x1), float(x2)])
        ys.extend([float(y1), float(y2)])

    return BoundingBox(min(xs), min(ys), max(xs), max(ys))


def transform_segments(
    segments: list[Segment],
    width: float,
    height: float,
    padding: float = 0.0,
) -> list[Segment]:
    """Scale and translate segments to fit a target canvas.

    Uses uniform scaling (preserve aspect ratio) and centers the drawing.

    Parameters
    ----------
    segments:
        Input segments.
    width, height:
        Target canvas size.
    padding:
        Absolute padding (same unit as width/height), applied on all sides.

    Returns
    -------
    list[Segment]
        Transformed segments.

    Raises
    ------
    ValueError
        If width/height are non-positive, padding is negative, padding is too
        large, or segments are empty.
    """

    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if padding < 0:
        raise ValueError("padding must be non-negative")

    bounds = compute_bounds(segments)
    if bounds is None:
        raise ValueError("segments must not be empty")

    avail_w = width - 2.0 * padding
    avail_h = height - 2.0 * padding
    if avail_w <= 0 or avail_h <= 0:
        raise ValueError("padding too large for given width/height")

    # Degenerate bounds (point/line) should not cause division by zero.
    bw = bounds.width
    bh = bounds.height

    if bw == 0.0 and bh == 0.0:
        scale = 1.0
    else:
        scale_x = float("inf") if bw == 0.0 else (avail_w / bw)
        scale_y = float("inf") if bh == 0.0 else (avail_h / bh)
        scale = min(scale_x, scale_y)

    (cx, cy) = bounds.center
    target_cx = width / 2.0
    target_cy = height / 2.0

    def tx(p: tuple[float, float]) -> tuple[float, float]:
        x, y = p
        return (
            (float(x) - cx) * scale + target_cx,
            (float(y) - cy) * scale + target_cy,
        )

    return [Segment(start=tx(s.start), end=tx(s.end)) for s in segments]
