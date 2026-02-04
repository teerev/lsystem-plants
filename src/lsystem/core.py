from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


MAX_ITERATIONS = 15
MAX_STRING_LENGTH = 10_000_000


@dataclass(frozen=True)
class LSystem:
    """Immutable L-system definition.

    Parameters
    ----------
    axiom:
        The initial string.
    rules:
        Mapping of single-character symbols to replacement strings.

    Examples
    --------
    >>> from lsystem.core import LSystem, expand
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

    Rules are applied simultaneously per iteration by replacing each character
    with rules.get(char, char). Characters not present in the rules are
    preserved.

    Safety limits:
    - iterations is capped at MAX_ITERATIONS (15)
    - output length is capped at MAX_STRING_LENGTH (10,000,000)

    Examples
    --------
    >>> from lsystem.core import LSystem, expand
    >>> expand(LSystem(axiom="XAX", rules={"A": "AB"}), 1)
    'XABX'
    """

    if not isinstance(iterations, int):
        raise ValueError("iterations must be an int")
    if iterations < 0:
        raise ValueError("iterations must be >= 0")
    if iterations > MAX_ITERATIONS:
        raise ValueError(f"iterations must be <= {MAX_ITERATIONS}")

    current = system.axiom

    for _ in range(iterations):
        parts: list[str] = []
        out_len = 0
        for ch in current:
            repl = system.rules.get(ch, ch)
            out_len += len(repl)
            if out_len > MAX_STRING_LENGTH:
                raise ValueError(
                    f"expanded string exceeds max length {MAX_STRING_LENGTH}"
                )
            parts.append(repl)
        current = "".join(parts)

    return current
