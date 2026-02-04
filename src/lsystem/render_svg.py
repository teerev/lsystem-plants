from __future__ import annotations

from pathlib import Path

from lsystem.bounds import transform_segments
from lsystem.turtle import Segment


def _fmt4(value: float) -> str:
    # Canonical float formatting: exactly 4 decimal places.
    return f"{float(value):.4f}"


def _svg_line(seg: Segment, stroke: str, stroke_width: float) -> str:
    (x1, y1) = seg.start
    (x2, y2) = seg.end

    # Canonical attribute ordering: alphabetical.
    attrs = (
        f'x1="{_fmt4(x1)}" '
        f'x2="{_fmt4(x2)}" '
        f'y1="{_fmt4(y1)}" '
        f'y2="{_fmt4(y2)}" '
        f'stroke="{stroke}" '
        f'stroke-width="{_fmt4(stroke_width)}"'
    )
    return f"  <line {attrs} />"


def render_svg(
    segments: list[Segment],
    width: int = 800,
    height: int = 600,
    stroke: str = "#228B22",
    stroke_width: float = 1.0,
    padding: float = 20.0,
) -> str:
    """Render a list of line segments to a canonical SVG string.

    Canonical output guarantees deterministic serialization:
    - fixed 4dp float formatting
    - stable attribute ordering (alphabetical)
    - consistent whitespace/newlines

    Segments are auto-scaled to fit the canvas using bounds.transform_segments.

    For empty segments, returns a valid SVG container with no lines.
    """

    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if stroke_width <= 0:
        raise ValueError("stroke_width must be positive")
    if padding < 0:
        raise ValueError("padding must be non-negative")

    # Canonical container attributes: alphabetical order.
    svg_open = (
        f'<svg height="{int(height)}" '
        f'viewBox="0 0 {int(width)} {int(height)}" '
        f'width="{int(width)}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    )

    if not segments:
        return f"{svg_open}\n</svg>\n"

    segs = transform_segments(segments, float(width), float(height), float(padding))

    lines = [svg_open]
    lines.extend(_svg_line(seg, stroke=stroke, stroke_width=stroke_width) for seg in segs)
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def save_svg(content: str, path: Path) -> None:
    """Write SVG content to a file."""

    path.write_text(content, encoding="utf-8")
