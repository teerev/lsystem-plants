from __future__ import annotations

import math
from dataclasses import dataclass
from typing import NamedTuple


@dataclass
class TurtleState:
    """2D turtle state.

    Angles are in degrees.

    Attributes
    ----------
    x, y:
        Current position.
    angle:
        Current heading angle in degrees where 0 is +X and 90 is +Y.
    """

    x: float
    y: float
    angle: float


class Segment(NamedTuple):
    """A 2D line segment."""

    start: tuple[float, float]
    end: tuple[float, float]


def _round_point(x: float, y: float, ndigits: int = 6) -> tuple[float, float]:
    return (round(x, ndigits), round(y, ndigits))


def interpret(instructions: str, angle: float, step: float) -> list[Segment]:
    """Interpret L-system turtle instructions into 2D line segments.

    Supported symbols
    -----------------
    F: move forward and draw
    f: move forward without drawing
    +: turn left by `angle` degrees
    -: turn right by `angle` degrees
    [: push current state onto stack
    ]: pop state from stack (raises ValueError if stack is empty)
    |: turn 180 degrees

    Unknown symbols are ignored.

    Parameters
    ----------
    instructions:
        Instruction string.
    angle:
        Turn angle in degrees.
    step:
        Forward step length.

    Returns
    -------
    list[Segment]
        The list of drawn segments.
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
        if ch == "+":
            state.angle += float(angle)
        elif ch == "-":
            state.angle -= float(angle)
        elif ch == "|":
            state.angle += 180.0
        elif ch == "[":
            # copy current state
            stack.append(TurtleState(state.x, state.y, state.angle))
        elif ch == "]":
            if not stack:
                raise ValueError("unbalanced ']' (pop from empty stack)")
            state = stack.pop()
        elif ch == "F" or ch == "f":
            rad = math.radians(state.angle)
            nx = state.x + float(step) * math.cos(rad)
            ny = state.y + float(step) * math.sin(rad)

            if ch == "F":
                segments.append(
                    Segment(
                        start=_round_point(state.x, state.y),
                        end=_round_point(nx, ny),
                    )
                )

            state.x = nx
            state.y = ny
        else:
            # ignore unknown symbols
            continue

    return segments
