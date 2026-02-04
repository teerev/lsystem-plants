import pytest

from lsystem.core import MAX_ITERATIONS, expand
from lsystem.presets import Preset, get_preset, list_presets
from lsystem.turtle import interpret


def test_get_known_preset() -> None:
    p = get_preset("fern")
    assert isinstance(p, Preset)
    assert p.name == "fern"


def test_get_unknown_preset_raises_keyerror() -> None:
    with pytest.raises(KeyError):
        get_preset("unknown")


def test_list_presets_has_at_least_three_and_contains_expected() -> None:
    names = list_presets()
    assert len(names) >= 3
    assert "fern" in names


def test_presets_expand_and_interpret_producing_nontrivial_segments() -> None:
    for name in list_presets():
        p = get_preset(name)
        assert 0 <= p.iterations <= MAX_ITERATIONS
        instructions = expand(p.system, p.iterations)
        segments = interpret(instructions, angle=p.angle, step=p.step)
        assert len(segments) >= 10
