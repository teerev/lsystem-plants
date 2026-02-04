import pytest

from lsystem.core import LSystem, expand
from lsystem.core import MAX_ITERATIONS, MAX_OUTPUT_LENGTH


def test_simple_expansion() -> None:
    system = LSystem(axiom="F", rules={"F": "FF"})
    assert expand(system, 1) == "FF"


def test_multi_iteration_doubling() -> None:
    system = LSystem(axiom="F", rules={"F": "FF"})
    assert expand(system, 3) == "F" * 8


def test_unknown_chars_preserved() -> None:
    system = LSystem(axiom="XAX", rules={"A": "AB"})
    assert expand(system, 1) == "XABX"


def test_determinism() -> None:
    system = LSystem(axiom="F+F", rules={"F": "F-F"})
    out1 = expand(system, 5)
    out2 = expand(system, 5)
    assert out1 == out2


def test_max_iterations_enforced() -> None:
    system = LSystem(axiom="F", rules={"F": "FF"})
    with pytest.raises(ValueError):
        expand(system, MAX_ITERATIONS + 1)


def test_max_length_enforced() -> None:
    # Create a rule that grows extremely fast so we can exceed MAX_OUTPUT_LENGTH
    # within the MAX_ITERATIONS limit.
    # After n iterations, length will be (growth_factor**n).
    growth_factor = 1000
    system = LSystem(axiom="F", rules={"F": "F" * growth_factor})

    # Find smallest n <= MAX_ITERATIONS such that growth_factor**n > MAX_OUTPUT_LENGTH.
    n = 0
    length = 1
    while length <= MAX_OUTPUT_LENGTH and n < MAX_ITERATIONS:
        n += 1
        length *= growth_factor

    assert n <= MAX_ITERATIONS
    assert length > MAX_OUTPUT_LENGTH

    with pytest.raises(ValueError):
        expand(system, n)


def test_empty_axiom_rejected() -> None:
    with pytest.raises(ValueError):
        LSystem(axiom="", rules={"F": "FF"})


def test_empty_rules_rejected() -> None:
    with pytest.raises(ValueError):
        LSystem(axiom="F", rules={})


def test_invalid_rule_key_rejected() -> None:
    with pytest.raises(ValueError):
        LSystem(axiom="F", rules={"FF": "F"})


def test_complex_rules_single_pass() -> None:
    # Ensure multiple rules apply in a single iteration based on the original string.
    system = LSystem(axiom="AB", rules={"A": "BA", "B": "A"})
    assert expand(system, 1) == "BAA"
