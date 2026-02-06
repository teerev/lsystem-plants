from __future__ import annotations

from .types import Grammar


def expand(grammar: Grammar, iterations: int) -> str:
    """Expand an L-system grammar for a given number of iterations.

    Rules are applied simultaneously per iteration by scanning the current
    string left-to-right and replacing each character if it exists as a key in
    grammar.rules; otherwise the character is kept unchanged.

    This function is pure and deterministic.
    """
    if iterations < 0:
        raise ValueError("iterations must be >= 0")

    current = grammar.axiom
    if iterations == 0:
        return current

    rules = grammar.rules
    for _ in range(iterations):
        current = "".join(rules.get(ch, ch) for ch in current)

    return current
