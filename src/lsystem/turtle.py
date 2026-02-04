from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, NamedTuple, Tuple


Point = Tuple[float, float]


class Segment(NamedTuple):
    start: Point
    end: Point


@dataclass
class TurtleState:
    x: float
    y: float
    angle: float


def _round_point(x: float, y: float, precision: int = 6) -> Point:
    return (round(x, precision), round(y, precision))


def interpret(instructions: str, angle: float, step: float) -> List[Segment]:
    """Interpret a 2D turtle instruction string into line segments.

    Parameters
    ----------
    instructions:
        The expanded L-system string.
    angle:
        Turn angle in degrees for '+' and '-'.
    step:
        Forward step length for 'F' and 'f'.

    Returns
    -------
    list[Segment]
        Line segments of drawn moves.

    Notes
    -----
    - Initial state: position (0, 0), heading up (90 degrees).
    - Unknown symbols are ignored.
    - Unbalanced ']' raises ValueError.
    """

    if not isinstance(instructions, str):
        raise TypeError("instructions must be a str")
    if not isinstance(angle, (int, float)):
        raise TypeError("angle must be a number")
    if not isinstance(step, (int, float)):
        raise TypeError("step must be a number")

    state = TurtleState(0.0, 0.0, 90.0)
    stack: list[TurtleState] = []
    segments: list[Segment] = []

    def forward(draw: bool) -> None:
        nonlocal state
        rad = math.radians(state.angle)
        nx = state.x + float(step) * math.cos(rad)
        ny = state.y + float(step) * math.sin(rad)
        if draw:
            segments.append(
                Segment(
                    start=_round_point(state.x, state.y),
                    end=_round_point(nx, ny),
                )
            )
        state = TurtleState(nx, ny, state.angle)

    for ch in instructions:
        if ch == "F":
            forward(draw=True)
        elif ch == "f":
            forward(draw=False)
        elif ch == "+":
            state = TurtleState(state.x, state.y, state.angle + float(angle))
        elif ch == "-":
            state = TurtleState(state.x, state.y, state.angle - float(angle))
        elif ch == "|":
            state = TurtleState(state.x, state.y, state.angle + 180.0)
        elif ch == "[":
            stack.append(state)
        elif ch == "]":
            if not stack:
                raise ValueError("unbalanced ']' (pop from empty stack)")
            state = stack.pop()
        else:
            # ignore unknown symbols
            continue

    return segments
