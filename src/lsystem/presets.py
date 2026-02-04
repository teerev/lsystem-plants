"""Curated plant-like L-system presets.

This module provides a small library of deterministic, plant-inspired L-systems
that expand quickly and draw recognizable botanical forms using the project's
supported turtle symbols.

Presets are intended to be good-looking defaults:
- small/fast: "weed" (simple branching)
- medium: "fern" (fractal fern-like fronds)
- large: "bush" (dense shrub/tree-like canopy)

All presets only use supported symbols in their expanded output:
F, f, +, -, [, ], |

Notes
-----
The classic plant formulations use the variable symbol 'X' during expansion.
The turtle interpreter ignores unknown symbols, so 'X' is safe in the expanded
string as long as the drawing symbols are supported.
"""

from __future__ import annotations

from dataclasses import dataclass

from lsystem.core import LSystem


@dataclass(frozen=True)
class Preset:
    """Bundle of parameters required to render an L-system plant."""

    name: str
    system: LSystem
    angle: float
    step: float
    iterations: int
    description: str


_PRESETS: dict[str, Preset] = {
    # Small: simple branching "weed" / sprout
    "weed": Preset(
        name="weed",
        system=LSystem(
            axiom="F",
            rules={
                "F": "F[+F]F[-F]F",
            },
        ),
        angle=22.5,
        step=5.0,
        iterations=3,
        description=(
            "Small, fast branching sprout with a few side shoots; "
            "good for quick previews."
        ),
    ),
    # Medium: fern/fractal plant (classic)
    "fern": Preset(
        name="fern",
        system=LSystem(
            axiom="X",
            rules={
                "X": "F[+X]F[-X]+X",
                "F": "FF",
            },
        ),
        angle=20.0,
        step=3.0,
        iterations=5,
        description=(
            "Fractal fern-like plant with repeated fronds; medium complexity "
            "and balanced detail."
        ),
    ),
    # Large: dense bush/shrub (classic)
    "bush": Preset(
        name="bush",
        system=LSystem(
            axiom="F",
            rules={
                "F": "FF+[+F-F-F]-[-F+F+F]",
            },
        ),
        angle=22.5,
        step=2.5,
        iterations=4,
        description=(
            "Dense shrub/bush with many short branches creating a rounded canopy; "
            "more detailed and visually fuller."
        ),
    ),
}


def get_preset(name: str) -> Preset:
    """Return a named preset.

    Raises
    ------
    KeyError
        If the preset name is unknown.
    """

    if not isinstance(name, str):
        raise TypeError("name must be a str")
    return _PRESETS[name]


def list_presets() -> list[str]:
    """List available preset names."""

    return sorted(_PRESETS.keys())
