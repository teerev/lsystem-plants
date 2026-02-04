"""2D turtle graphics interpreter for L-system instruction strings.

This module converts an instruction string into a list of line segments.

Conventions
-----------
- Coordinates are 2D (x, y)
- Angles are in degrees
- 0 degrees points right (+X)
- 90 degrees points up (+Y)
- The initial state is at (0, 0) with heading 90 degrees

Supported symbols
-----------------
F: move forward and draw
f: move forward without drawing
+: turn left (counter-clockwise) by `angle`
-: turn right (clockwise) by `angle`
[: push state
]: pop state (raises ValueError if stack is empty)
|: turn 180 degrees

Unknown symbols are ignored.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import NamedTuple, Tuple, List


class Segment(NamedTuple):
    start: Tuple[float, float]
    end: Tuple[float, float]


@dataclass
class TurtleState:
    x: float
    y: float
    angle: float


def _round6(v: float) -> float:
    # Stabilize results for deterministic tests and downstream processing.
    return round(v, 6)


def interpret(instructions: str, angle: float, step: float) -> List[Segment]:
    """Interpret a turtle instruction string into 2D line segments.

    Parameters
    ----------
    instructions:
        L-system output string to interpret.
    angle:
        Turn angle in degrees for '+' and '-'.
    step:
        Forward step size for 'F' and 'f'.

    Returns
    -------
    list[Segment]
        Line segments drawn by 'F' commands.

    Raises
    ------
    ValueError
        If a ']' is encountered with an empty stack.
    """

    if not isinstance(instructions, str):
        raise ValueError("instructions must be a str")
    if not isinstance(angle, (int, float)):
        raise ValueError("angle must be a number")
    if not isinstance(step, (int, float)):
        raise ValueError("step must be a number")

    state = TurtleState(0.0, 0.0, 90.0)
    stack: list[TurtleState] = []
    segments: list[Segment] = []

    for ch in instructions:
        if ch in ("F", "f"):
            rad = math.radians(state.angle)
            nx = state.x + float(step) * math.cos(rad)
            ny = state.y + float(step) * math.sin(rad)

            start = (_round6(state.x), _round6(state.y))
            end = (_round6(nx), _round6(ny))

            if ch == "F":
                segments.append(Segment(start=start, end=end))

            state.x, state.y = nx, ny

        elif ch == "+":
            state.angle = float(state.angle) + float(angle)
        elif ch == "-":
            state.angle = float(state.angle) - float(angle)
        elif ch == "|":
            state.angle = float(state.angle) + 180.0
        elif ch == "[":
            # Copy the state so future mutation doesn't affect the stored snapshot.
            stack.append(TurtleState(state.x, state.y, state.angle))
        elif ch == "]":
            if not stack:
                raise ValueError("unbalanced ']' (pop from empty stack)")
            state = stack.pop()
        else:
            # Ignore unknown symbols (decorative or variables like X).
            continue

    return segments
