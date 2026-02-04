from __future__ import annotations

"""Curated plant-like L-system presets.

This module provides a small library of deterministic, plant-inspired L-systems
that work with the project's supported alphabet:

- F: draw forward
- f: move forward (no draw)
- + / -: turn
- [ / ]: push/pop turtle state
- |: turn 180 degrees

Each preset includes a recommended iteration count that stays within the core
engine's safety limit.
"""

from dataclasses import dataclass

from lsystem.core import LSystem


@dataclass(frozen=True)
class Preset:
    """A bundled, ready-to-render L-system preset."""

    name: str
    system: LSystem
    angle: float
    step: float
    iterations: int
    description: str


# NOTE: All rules use only supported symbols.
_PRESETS: dict[str, Preset] = {
    "weed": Preset(
        name="weed",
        system=LSystem(
            axiom="F",
            rules={
                # Small and fast: a simple repeatedly-branching stem.
                "F": "F[+F]F[-F]F",
            },
        ),
        angle=25.0,
        step=5.0,
        iterations=3,
        description="Small, fast branching weed-like plant with a central stem and short side shoots.",
    ),
    "fern": Preset(
        name="fern",
        system=LSystem(
            axiom="F",
            rules={
                # Classic fern-like structure using only supported symbols.
                "F": "F[+F]F[-F]F",
            },
        ),
        angle=20.0,
        step=4.0,
        iterations=5,
        description="Medium-complexity fern/fractal plant with alternating pinnae-like branching.",
    ),
    "bush": Preset(
        name="bush",
        system=LSystem(
            axiom="F",
            rules={
                # Dense bush: produces a fuller, rounder canopy.
                "F": "FF+[+F-F-F]-[-F+F+F]",
            },
        ),
        angle=22.5,
        step=3.0,
        iterations=4,
        description="Larger, denser bushy plant with many short branches and a fuller silhouette.",
    ),
}


def get_preset(name: str) -> Preset:
    """Return a preset by name.

    Raises
    ------
    KeyError
        If the preset name is unknown.
    """

    if name in _PRESETS:
        return _PRESETS[name]
    raise KeyError(f"unknown preset: {name}")


def list_presets() -> list[str]:
    """List available preset names."""

    return sorted(_PRESETS.keys())
