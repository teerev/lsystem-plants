import pytest

from lsystem.core import LSystem, expand


def test_simple_expansion() -> None:
    system = LSystem(axiom="F", rules={"F": "FF"})
    assert expand(system, 1) == "FF"


def test_multi_iteration() -> None:
    system = LSystem(axiom="F", rules={"F": "FF"})
    assert expand(system, 3) == "F" * (2**3)


def test_unknown_chars_preserved() -> None:
    system = LSystem(axiom="XAX", rules={"A": "AB"})
    assert expand(system, 1) == "XABX"


def test_determinism() -> None:
    system = LSystem(axiom="F+F", rules={"F": "F-F"})
    a = expand(system, 4)
    b = expand(system, 4)
    assert a == b


def test_max_iterations_enforced() -> None:
    system = LSystem(axiom="F", rules={"F": "FF"})
    with pytest.raises(ValueError):
        expand(system, 20)


def test_max_length_enforced() -> None:
    # Grow fast enough to exceed 10,000,000 within allowed iterations.
    system = LSystem(axiom="A", rules={"A": "A" * 100})
    with pytest.raises(ValueError):
        expand(system, 4)  # 100**4 = 100,000,000


def test_empty_axiom_rejected() -> None:
    with pytest.raises(ValueError):
        LSystem(axiom="", rules={"F": "FF"})


def test_empty_rules_rejected() -> None:
    with pytest.raises(ValueError):
        LSystem(axiom="F", rules={})


def test_complex_rules_applied_in_single_pass() -> None:
    system = LSystem(axiom="AB", rules={"A": "BA", "B": "A"})
    assert expand(system, 1) == "BAA"
