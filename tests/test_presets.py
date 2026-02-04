from __future__ import annotations

import pytest

from lsystem.core import expand, MAX_ITERATIONS
from lsystem.presets import Preset, get_preset, list_presets
from lsystem.turtle import interpret


def test_get_known_preset_returns_preset() -> None:
    p = get_preset("fern")
    assert isinstance(p, Preset)
    assert p.name == "fern"
    assert isinstance(p.system.axiom, str)
    assert isinstance(p.system.rules, dict)


def test_get_unknown_preset_raises_keyerror() -> None:
    with pytest.raises(KeyError):
        get_preset("unknown")


def test_list_presets_has_at_least_three_and_is_sorted() -> None:
    names = list_presets()
    assert isinstance(names, list)
    assert len(names) >= 3
    assert names == sorted(names)


def test_all_presets_expand_and_interpret_producing_segments() -> None:
    allowed = set("Ff+-[]|")

    for name in list_presets():
        p = get_preset(name)
        assert 0 <= p.iterations <= MAX_ITERATIONS

        s = expand(p.system, p.iterations)
        # expansion should produce some drawing commands
        assert s.count("F") >= 10

        # expanded output should not contain unsupported drawing symbols
        # (variables like 'X' are permitted and ignored by the turtle)
        illegal = set(ch for ch in s if ch.isalpha() and ch not in ("F", "f", "X"))
        assert illegal == set()

        segments = interpret(s, angle=p.angle, step=p.step)
        assert len(segments) >= 10

        # ensure segments are well-formed tuples of floats
        start0 = segments[0].start
        end0 = segments[0].end
        assert len(start0) == 2 and len(end0) == 2
        assert all(isinstance(v, float) for v in (*start0, *end0))
