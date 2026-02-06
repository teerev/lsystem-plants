import pytest

from lsysviz.turtle import interpret
from lsysviz.types import Segment


def test_single_F_produces_one_segment_up() -> None:
    segs = interpret(lstring="F", angle_deg=90, step_length=10)
    assert len(segs) == 1
    assert segs[0].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].x1 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y1 == pytest.approx(10.0, abs=1e-9)


def test_FF_produces_two_segments() -> None:
    segs = interpret(lstring="FF", angle_deg=90, step_length=10)
    assert len(segs) == 2
    assert segs[0] == Segment(0.0, 0.0, pytest.approx(0.0, abs=1e-9), pytest.approx(10.0, abs=1e-9))
    assert segs[1].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[1].y0 == pytest.approx(10.0, abs=1e-9)
    assert segs[1].x1 == pytest.approx(0.0, abs=1e-9)
    assert segs[1].y1 == pytest.approx(20.0, abs=1e-9)


def test_F_plus_F_turns_left_second_segment_goes_left() -> None:
    segs = interpret(lstring="F+F", angle_deg=90, step_length=10)
    assert len(segs) == 2

    # First segment: up
    assert segs[0].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].x1 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y1 == pytest.approx(10.0, abs=1e-9)

    # Second segment: left from (0,10) to (-10,10)
    assert segs[1].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[1].y0 == pytest.approx(10.0, abs=1e-9)
    assert segs[1].x1 == pytest.approx(-10.0, abs=1e-9)
    assert segs[1].y1 == pytest.approx(10.0, abs=1e-9)


def test_F_minus_F_turns_right_second_segment_goes_right() -> None:
    segs = interpret(lstring="F-F", angle_deg=90, step_length=10)
    assert len(segs) == 2

    # First segment: up
    assert segs[0].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].x1 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y1 == pytest.approx(10.0, abs=1e-9)

    # Second segment: right from (0,10) to (10,10)
    assert segs[1].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[1].y0 == pytest.approx(10.0, abs=1e-9)
    assert segs[1].x1 == pytest.approx(10.0, abs=1e-9)
    assert segs[1].y1 == pytest.approx(10.0, abs=1e-9)


def test_push_pop_F_bracket_plus_F_bracket_minus_F_third_starts_after_first() -> None:
    # After first F: at (0,10). Push. Then +F draws left to (-10,10).
    # Pop returns to (0,10) with original heading. Then -F draws right to (10,10).
    segs = interpret(lstring="F[+F]-F", angle_deg=90, step_length=10)
    assert len(segs) == 3

    # First: up
    assert segs[0].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].x1 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y1 == pytest.approx(10.0, abs=1e-9)

    # Second: left from (0,10)
    assert segs[1].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[1].y0 == pytest.approx(10.0, abs=1e-9)
    assert segs[1].x1 == pytest.approx(-10.0, abs=1e-9)
    assert segs[1].y1 == pytest.approx(10.0, abs=1e-9)

    # Third: must start from (0,10) (after first F), not from (-10,10)
    assert segs[2].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[2].y0 == pytest.approx(10.0, abs=1e-9)
    assert segs[2].x1 == pytest.approx(10.0, abs=1e-9)
    assert segs[2].y1 == pytest.approx(10.0, abs=1e-9)


def test_unknown_characters_are_ignored() -> None:
    segs = interpret(lstring="FXF", angle_deg=90, step_length=10)
    assert len(segs) == 2
    assert segs[0].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y0 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].x1 == pytest.approx(0.0, abs=1e-9)
    assert segs[0].y1 == pytest.approx(10.0, abs=1e-9)

    assert segs[1].x0 == pytest.approx(0.0, abs=1e-9)
    assert segs[1].y0 == pytest.approx(10.0, abs=1e-9)
    assert segs[1].x1 == pytest.approx(0.0, abs=1e-9)
    assert segs[1].y1 == pytest.approx(20.0, abs=1e-9)
