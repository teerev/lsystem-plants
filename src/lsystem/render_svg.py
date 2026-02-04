from __future__ import annotations

from pathlib import Path

from lsystem.bounds import transform_segments
from lsystem.turtle import Segment


def _fmt(value: float) -> str:
    # Canonical float format: exactly 4 decimals
    return f"{float(value):.4f}"


def _clamp_padding(width: float, height: float, padding: float) -> float:
    """Clamp padding so that 2*padding < min(width, height).

    This prevents transform_segments() from raising for small canvases while
    keeping output deterministic.
    """
    if padding < 0:
        raise ValueError("padding must be non-negative")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    max_padding = (min(width, height) / 2.0) - 1e-9
    if max_padding < 0:
        return 0.0
    return min(float(padding), max_padding)


def render_svg(
    segments: list[Segment],
    width: int = 800,
    height: int = 600,
    stroke: str = "#228B22",
    stroke_width: float = 1.0,
    padding: float = 20.0,
) -> str:
    """Render line segments as a canonical SVG string."""

    w = float(width)
    h = float(height)
    pad = _clamp_padding(w, h, float(padding))

    transformed = transform_segments(
        segments,
        width=w,
        height=h,
        padding=pad,
    )

    # Canonical SVG output:
    # - stable element ordering (input segment order)
    # - stable attribute ordering (alphabetical)
    # - stable float formatting (4 decimals)
    lines: list[str] = []
    lines.append(
        f'<svg height="{int(width * 0 + height)}" width="{int(width)}" xmlns="http://www.w3.org/2000/svg">'
    )

    for seg in transformed:
        x1, y1 = seg.start
        x2, y2 = seg.end
        lines.append(
            "  "
            + "<line "
            + " ".join(
                [
                    f'stroke="{stroke}"',
                    f'stroke-width="{_fmt(stroke_width)}"',
                    f'x1="{_fmt(x1)}"',
                    f'x2="{_fmt(x2)}"',
                    f'y1="{_fmt(y1)}"',
                    f'y2="{_fmt(y2)}"',
                ]
            )
            + " />"
        )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def save_svg(content: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
