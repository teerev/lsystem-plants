from __future__ import annotations

from dataclasses import dataclass

from lsystem.core import LSystem, MAX_ITERATIONS, expand


@dataclass(frozen=True)
class Preset:
    """Bundled configuration for a curated plant-like L-system.

    Attributes
    ----------
    name:
        Preset identifier used in :func:`get_preset`.
    system:
        The underlying deterministic :class:`lsystem.core.LSystem`.
    angle:
        Turn angle in degrees used by the turtle interpreter.
    step:
        Forward step length used by the turtle interpreter.
    iterations:
        Recommended expansion iterations (kept within safety limits).
    description:
        Brief visual description of what the preset tends to resemble.
    """

    name: str
    system: LSystem
    angle: float
    step: float
    iterations: int
    description: str


def _validate_symbols(preset: Preset) -> None:
    """Best-effort validation that the preset uses only supported symbols.

    Note: the engine itself can expand arbitrary symbols, but the turtle
    interpreter only understands F f + - [ ] |.
    """

    allowed = set("Ff+-[]|")
    # Allow non-drawing symbols in the *axiom/rules* only if they will be expanded
    # away by the time we render. For curated presets we keep them to supported set.
    for s in [preset.system.axiom, *preset.system.rules.keys(), *preset.system.rules.values()]:
        for ch in s:
            if ch not in allowed:
                raise ValueError(
                    f"preset '{preset.name}' contains unsupported symbol {ch!r}; "
                    "only 'F', 'f', '+', '-', '[', ']', '|' are allowed"
                )

    if not (0 <= preset.iterations <= MAX_ITERATIONS):
        raise ValueError(
            f"preset '{preset.name}' iterations must be within [0, {MAX_ITERATIONS}]"
        )

    # Ensure it can expand at least once without violating core safety checks.
    _ = expand(preset.system, preset.iterations)


# Curated presets.
# All rules/axioms use only supported turtle symbols.
_PRESETS: dict[str, Preset] = {}


def _register(preset: Preset) -> None:
    _validate_symbols(preset)
    _PRESETS[preset.name] = preset


# 1) Small / fast: simple branching weed.
_register(
    Preset(
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
        description="Simple branching weed with a main stem and small side shoots.",
    )
)

# 2) Medium complexity: fern-like fronds.
_register(
    Preset(
        name="fern",
        system=LSystem(
            axiom="F",
            rules={
                "F": "F[+F]F[-F]F",
            },
        ),
        angle=20.0,
        step=4.0,
        iterations=4,
        description="Fern-like fronds; repeating pinnae along a central rachis.",
    )
)

# 3) Larger / more detailed: bushy shrub.
_register(
    Preset(
        name="bush",
        system=LSystem(
            axiom="F",
            rules={
                "F": "FF+[+F-F-F]-[-F+F+F]",
            },
        ),
        angle=22.5,
        step=3.0,
        iterations=4,
        description="Dense bush/shrub with many branchlets and clustered growth.",
    )
)


def get_preset(name: str) -> Preset:
    """Return a preset by name.

    Raises
    ------
    KeyError
        If the preset name is not known.
    """

    if not isinstance(name, str):
        raise TypeError("name must be a str")
    return _PRESETS[name]


def list_presets() -> list[str]:
    """List available preset names."""

    return sorted(_PRESETS.keys())
