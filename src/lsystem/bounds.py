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
        return float(self.max_x - self.min_x)

    @property
    def height(self) -> float:
        return float(self.max_y - self.min_y)

    @property
    def center(self) -> tuple[float, float]:
        return (self.min_x + self.width / 2.0, self.min_y + self.height / 2.0)


def compute_bounds(segments: list[Segment]) -> BoundingBox | None:
    if not segments:
        return None

    # Consider all endpoints
    xs: list[float] = []
    ys: list[float] = []
    for seg in segments:
        xs.append(float(seg.start[0]))
        ys.append(float(seg.start[1]))
        xs.append(float(seg.end[0]))
        ys.append(float(seg.end[1]))

    return BoundingBox(min(xs), min(ys), max(xs), max(ys))


def transform_segments(
    segments: list[Segment],
    width: float,
    height: float,
    padding: float = 0.0,
) -> list[Segment]:
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if padding < 0:
        raise ValueError("padding must be non-negative")

    bounds = compute_bounds(segments)
    if bounds is None:
        return []

    avail_w = width - 2.0 * float(padding)
    avail_h = height - 2.0 * float(padding)
    if avail_w <= 0 or avail_h <= 0:
        raise ValueError("padding too large for target canvas")

    bw = bounds.width
    bh = bounds.height

    # Uniform scaling, preserve aspect ratio
    if bw == 0.0 and bh == 0.0:
        scale = 1.0
    else:
        sx = float("inf") if bw == 0.0 else (avail_w / bw)
        sy = float("inf") if bh == 0.0 else (avail_h / bh)
        scale = min(sx, sy)

    cx, cy = bounds.center
    target_cx = float(padding) + avail_w / 2.0
    target_cy = float(padding) + avail_h / 2.0

    def tx(p: tuple[float, float]) -> tuple[float, float]:
        x, y = float(p[0]), float(p[1])
        return ((x - cx) * scale + target_cx, (y - cy) * scale + target_cy)

    return [Segment(start=tx(s.start), end=tx(s.end)) for s in segments]
