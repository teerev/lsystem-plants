import pytest

from lsystem.core import MAX_ITERATIONS, expand
from lsystem.presets import Preset, get_preset, list_presets
from lsystem.turtle import interpret


def test_get_known_preset() -> None:
    p = get_preset("fern")
    assert isinstance(p, Preset)
    assert p.name == "fern"


def test_get_unknown_preset() -> None:
    with pytest.raises(KeyError):
        get_preset("unknown")


def test_list_presets_has_at_least_three() -> None:
    names = list_presets()
    assert isinstance(names, list)
    assert len(names) >= 3
    assert "fern" in names


def test_presets_expand_and_interpret_and_nontrivial() -> None:
    # Each preset should expand and interpret without error, and produce segments.
    for name in list_presets():
        p = get_preset(name)
        assert 0 <= p.iterations <= MAX_ITERATIONS

        expanded = expand(p.system, p.iterations)
        assert isinstance(expanded, str)
        # Non-trivial: should draw more than 10 segments.
        segs = interpret(expanded, angle=p.angle, step=p.step)
        assert len(segs) >= 10


def test_presets_use_supported_symbols_only() -> None:
    allowed = set("Ff+-[]|")
    for name in list_presets():
        p = get_preset(name)
        corpus = p.system.axiom + "".join(p.system.rules.keys()) + "".join(p.system.rules.values())
        assert set(corpus).issubset(allowed)
