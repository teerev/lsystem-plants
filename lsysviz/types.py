from __future__ import annotations

from typing import NamedTuple


class Grammar(NamedTuple):
    axiom: str
    rules: dict[str, str]


class Segment(NamedTuple):
    x0: float
    y0: float
    x1: float
    y1: float
