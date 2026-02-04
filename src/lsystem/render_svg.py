from __future__ import annotations

from pathlib import Path
from typing import Iterable

from lsystem.bounds import transform_segments
from lsystem.turtle import Segment


def _fmt4(v: float) -> str:
    """Format a number to exactly 4 decimal places for canonical SVG output."""

    return f"{float(v):.4f}"


def _sanitize_stroke(stroke: str) -> str:
    if not isinstance(stroke, str) or not stroke:
        raise ValueError("stroke must be a non-empty string")
    # Keep minimal constraints: deterministic output and basic SVG safety.
    # Disallow characters that could break attribute quoting.
    if any(ch in stroke for ch in ['"', "'", "<", ">", "\n", "\r", "\t"]):
        raise ValueError("stroke contains invalid characters")
    return stroke


def render_svg(
    segments: list[Segment],
    width: int = 800,
    height: int = 600,
    stroke: str = "#228B22",
    stroke_width: float = 1.0,
    padding: float = 20.0,
) -> str:
    """Render line segments as a canonical SVG string.

    Canonical properties:
    - Stable element/attribute ordering
    - Fixed float precision (4 decimals)
    - Predictable whitespace/newlines
    """

    if not isinstance(width, int) or not isinstance(height, int):
        raise ValueError("width and height must be ints")
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    if not isinstance(stroke_width, (int, float)):
        raise ValueError("stroke_width must be a number")
    if float(stroke_width) <= 0:
        raise ValueError("stroke_width must be positive")
    if not isinstance(padding, (int, float)):
        raise ValueError("padding must be a number")
    if float(padding) < 0:
        raise ValueError("padding must be non-negative")

    stroke = _sanitize_stroke(stroke)

    # Normalize/transform for output size.
    transformed = transform_segments(segments, float(width), float(height), float(padding))

    # SVG header and container.
    # Attribute order is alphabetical for determinism.
    lines: list[str] = []
    lines.append(
        (
            f'<svg height="{height}" '
            f'viewBox="0 0 {width} {height}" '
            f'width="{width}" '
            f'xmlns="http://www.w3.org/2000/svg">'
        )
    )

    # Render each segment as a <line> with canonical attribute ordering.
    # Attributes alphabetical: x1 x2 y1 y2 then stroke stroke-width.
    for seg in transformed:
        x1, y1 = seg.start
        x2, y2 = seg.end
        lines.append(
            (
                f'<line x1="{_fmt4(x1)}" x2="{_fmt4(x2)}" '
                f'y1="{_fmt4(y1)}" y2="{_fmt4(y2)}" '
                f'stroke="{stroke}" stroke-width="{_fmt4(stroke_width)}" />'
            )
        )

    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def save_svg(content: str, path: Path) -> None:
    if not isinstance(content, str):
        raise ValueError("content must be a str")
    if not isinstance(path, Path):
        raise ValueError("path must be a pathlib.Path")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
