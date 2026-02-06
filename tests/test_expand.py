import pytest

from lsysviz.expand import expand
from lsysviz.types import Grammar


def test_expand_zero_iterations_returns_axiom_unchanged():
    g = Grammar(axiom="A", rules={"A": "AB"})
    assert expand(g, 0) == "A"


@pytest.mark.parametrize(
    "iterations, expected",
    [
        (1, "AB"),
        (2, "ABA"),
        (3, "ABAAB"),
    ],
)
def test_expand_fibonacci_lsystem(iterations, expected):
    g = Grammar(axiom="A", rules={"A": "AB", "B": "A"})
    assert expand(g, iterations) == expected


def test_expand_preserves_characters_not_in_rules():
    g = Grammar(axiom="F+F", rules={"F": "FF"})
    assert expand(g, 1) == "FF+FF"


def test_expand_empty_rules_leaves_axiom_unchanged():
    g = Grammar(axiom="F+F", rules={})
    assert expand(g, 5) == "F+F"
