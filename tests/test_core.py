import pytest

from lsystem.core import LSystem, MAX_ITERATIONS, MAX_OUTPUT_LENGTH, expand


def test_simple_expansion() -> None:
    system = LSystem(axiom="F", rules={"F": "FF"})
    assert expand(system, 1) == "FF"


def test_multi_iteration_doubles_each_step() -> None:
    system = LSystem(axiom="F", rules={"F": "FF"})
    assert expand(system, 3) == "F" * (2**3)


def test_unknown_chars_preserved() -> None:
    system = LSystem(axiom="XAX", rules={"A": "AB"})
    assert expand(system, 1) == "XABX"


def test_determinism_same_inputs_same_output() -> None:
    system = LSystem(axiom="F+F", rules={"F": "F-F"})
    out1 = expand(system, 5)
    out2 = expand(system, 5)
    assert out1 == out2


def test_max_iterations_enforced() -> None:
    system = LSystem(axiom="F", rules={"F": "FF"})
    with pytest.raises(ValueError):
        expand(system, MAX_ITERATIONS + 1)


def test_max_length_enforced() -> None:
    # Ensure we exceed MAX_OUTPUT_LENGTH within allowed iterations.
    # Start length = 1, rule makes length multiply by 4 each iteration.
    # After 12 iterations: 4**12 = 16,777,216 (> 10,000,000)
    system = LSystem(axiom="A", rules={"A": "AAAA"})
    with pytest.raises(ValueError):
        expand(system, 12)


def test_empty_axiom_rejected() -> None:
    with pytest.raises(ValueError):
        LSystem(axiom="", rules={"A": "B"})


def test_empty_rules_rejected() -> None:
    with pytest.raises(ValueError):
        LSystem(axiom="A", rules={})


def test_complex_rules_single_pass_application() -> None:
    # Verify each character expanded based on rules from original string (single pass).
    system = LSystem(axiom="ABX", rules={"A": "BC", "B": "A"})
    assert expand(system, 1) == "BCA X".replace(" ", "")


def test_iterations_zero_returns_axiom() -> None:
    system = LSystem(axiom="ABC", rules={"A": "B"})
    assert expand(system, 0) == "ABC"


def test_negative_iterations_rejected() -> None:
    system = LSystem(axiom="A", rules={"A": "AA"})
    with pytest.raises(ValueError):
        expand(system, -1)


def test_output_length_limit_constant_is_sensible() -> None:
    assert MAX_OUTPUT_LENGTH == 10_000_000
