from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


MAX_ITERATIONS: int = 15
"""Maximum allowed iteration count to prevent runaway expansion."""

MAX_OUTPUT_LENGTH: int = 10_000_000
"""Maximum allowed length of an expanded string."""


@dataclass(frozen=True)
class LSystem:
    """Immutable deterministic L-system definition.

    Parameters
    ----------
    axiom:
        Non-empty starting string.
    rules:
        Mapping of single-character keys to replacement strings.

    Examples
    --------
    >>> system = LSystem(axiom="F", rules={"F": "FF"})
    >>> expand(system, 3)
    'FFFFFFFF'
    """

    axiom: str
    rules: dict[str, str]

    def __post_init__(self) -> None:
        if not isinstance(self.axiom, str) or self.axiom == "":
            raise ValueError("axiom must be a non-empty string")
        if not isinstance(self.rules, dict) or len(self.rules) == 0:
            raise ValueError("rules must be a non-empty dict[str, str]")
        for k, v in self.rules.items():
            if not isinstance(k, str) or len(k) != 1:
                raise ValueError("rules keys must be single-character strings")
            if not isinstance(v, str):
                raise ValueError("rules values must be strings")


def expand(system: LSystem, iterations: int) -> str:
    """Expand an L-system deterministically for a given number of iterations.

    Characters not present in the system rules are preserved unchanged.

    Safety limits are enforced:
    - iterations must be between 0 and MAX_ITERATIONS (inclusive)
    - the expanded string must not exceed MAX_OUTPUT_LENGTH characters

    Parameters
    ----------
    system:
        The L-system definition.
    iterations:
        The number of expansion steps to apply.

    Returns
    -------
    str
        The expanded string.

    Raises
    ------
    ValueError
        If iterations is negative, exceeds MAX_ITERATIONS, or if output would
        exceed MAX_OUTPUT_LENGTH.

    Examples
    --------
    >>> system = LSystem(axiom="XAX", rules={"A": "AB"})
    >>> expand(system, 1)
    'XABX'
    """

    if not isinstance(iterations, int):
        raise ValueError("iterations must be an int")
    if iterations < 0:
        raise ValueError("iterations must be >= 0")
    if iterations > MAX_ITERATIONS:
        raise ValueError(f"iterations must be <= {MAX_ITERATIONS}")

    s = system.axiom
    if len(s) > MAX_OUTPUT_LENGTH:
        raise ValueError(f"output length exceeds max of {MAX_OUTPUT_LENGTH}")

    rules: Mapping[str, str] = system.rules
    for _ in range(iterations):
        parts: list[str] = []
        out_len = 0
        for ch in s:
            repl = rules.get(ch, ch)
            out_len += len(repl)
            if out_len > MAX_OUTPUT_LENGTH:
                raise ValueError(f"output length exceeds max of {MAX_OUTPUT_LENGTH}")
            parts.append(repl)
        s = "".join(parts)
    return s
