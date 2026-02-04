"""Core L-system model and deterministic expansion.

The L-system (Lindenmayer system) is represented by an axiom (starting string)
and a set of deterministic rewrite rules.

Only deterministic, context-free, single-character rules are supported.

Examples
--------
>>> from lsystem.core import LSystem, expand
>>> system = LSystem(axiom="F", rules={"F": "FF"})
>>> expand(system, 3)
'FFFFFFFF'

Characters not present in the rules pass through unchanged:

>>> system = LSystem(axiom="XAX", rules={"A": "AB"})
>>> expand(system, 1)
'XABX'
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

MAX_ITERATIONS = 15
MAX_OUTPUT_LENGTH = 10_000_000


@dataclass(frozen=True)
class LSystem:
    """Immutable representation of a deterministic, context-free L-system.

    Parameters
    ----------
    axiom:
        Starting string for expansion. Must be non-empty.
    rules:
        Mapping of single-character symbols to replacement strings. Must be
        non-empty. Keys must be 1-character strings. Values must be strings.

    Examples
    --------
    >>> LSystem(axiom="F", rules={"F": "FF"})
    LSystem(axiom='F', rules={'F': 'FF'})
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

    Rules are applied in parallel per iteration: each character in the current
    string is replaced by rules.get(char, char).

    Safety limits:
    - iterations is capped at MAX_ITERATIONS (15)
    - output length is capped at MAX_OUTPUT_LENGTH (10,000,000)

    Parameters
    ----------
    system:
        The L-system to expand.
    iterations:
        Number of iterations to apply.

    Returns
    -------
    str
        The expanded string.

    Raises
    ------
    ValueError
        If iterations is negative, exceeds MAX_ITERATIONS, or expansion exceeds
        MAX_OUTPUT_LENGTH.

    Examples
    --------
    >>> from lsystem.core import LSystem, expand
    >>> expand(LSystem(axiom="F", rules={"F": "FF"}), 1)
    'FF'
    """

    if not isinstance(iterations, int):
        raise ValueError("iterations must be an int")
    if iterations < 0:
        raise ValueError("iterations must be >= 0")
    if iterations > MAX_ITERATIONS:
        raise ValueError(f"iterations must be <= {MAX_ITERATIONS}")

    current = system.axiom
    rules: Mapping[str, str] = system.rules

    if len(current) > MAX_OUTPUT_LENGTH:
        raise ValueError(
            f"expanded string exceeds maximum length {MAX_OUTPUT_LENGTH}"
        )

    for _ in range(iterations):
        parts: list[str] = []
        total_len = 0
        for ch in current:
            rep = rules.get(ch, ch)
            total_len += len(rep)
            if total_len > MAX_OUTPUT_LENGTH:
                raise ValueError(
                    f"expanded string exceeds maximum length {MAX_OUTPUT_LENGTH}"
                )
            parts.append(rep)
        current = "".join(parts)

    return current
