from __future__ import annotations

import math
from typing import List, Tuple

from .types import Segment


def interpret(lstring: str, angle_deg: float, step_length: float) -> list[Segment]:
    """Interpret an L-system string using turtle-graphics rules.

    The turtle starts at (0.0, 0.0) with heading 90 degrees (up).

    Supported commands:
      - 'F': move forward by step_length and record a Segment
      - '+': turn left (counter-clockwise) by angle_deg
      - '-': turn right (clockwise) by angle_deg
      - '[': push current (x, y, heading_deg) onto a stack
      - ']': pop (x, y, heading_deg) from the stack

    All other characters are ignored.

    This function is pure and deterministic.
    """

    x: float = 0.0
    y: float = 0.0
    heading_deg: float = 90.0

    segments: List[Segment] = []
    stack: List[Tuple[float, float, float]] = []

    for ch in lstring:
        if ch == "F":
            theta = math.radians(heading_deg)
            x1 = x + step_length * math.cos(theta)
            y1 = y + step_length * math.sin(theta)
            segments.append(Segment(x, y, x1, y1))
            x, y = x1, y1
        elif ch == "+":
            heading_deg += angle_deg
        elif ch == "-":
            heading_deg -= angle_deg
        elif ch == "[":
            stack.append((x, y, heading_deg))
        elif ch == "]":
            if stack:
                x, y, heading_deg = stack.pop()
        else:
            # Ignore all other characters
            continue

    return segments
