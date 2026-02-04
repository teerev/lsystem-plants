import pytest

from lsystem.turtle import Segment, interpret


def test_empty_string_returns_empty_list() -> None:
    assert interpret("", angle=25.0, step=1.0) == []


def test_forward_draw() -> None:
    segs = interpret("F", angle=90.0, step=2.0)
    assert segs == [Segment((0.0, 0.0), (0.0, 2.0))]


def test_forward_no_draw() -> None:
    segs = interpret("fF", angle=90.0, step=1.0)
    # after 'f' the turtle is at (0,1); then 'F' draws from there to (0,2)
    assert segs == [Segment((0.0, 1.0), (0.0, 2.0))]


def test_turn_left_then_forward_draws_left() -> None:
    # start angle 90; +90 => 180 (left)
    segs = interpret("+F", angle=90.0, step=1.0)
    assert segs == [Segment((0.0, 0.0), (-1.0, 0.0))]


def test_turn_right_then_forward_draws_right() -> None:
    # start angle 90; -90 => 0 (right)
    segs = interpret("-F", angle=90.0, step=1.0)
    assert segs == [Segment((0.0, 0.0), (1.0, 0.0))]


def test_push_pop_restores_state() -> None:
    # [F] draws one segment inside the branch, then pop back to origin
    # final F draws again from origin
    segs = interpret("[F]F", angle=25.0, step=1.0)
    assert segs == [
        Segment((0.0, 0.0), (0.0, 1.0)),
        Segment((0.0, 0.0), (0.0, 1.0)),
    ]


def test_turn_180_reverses_direction() -> None:
    segs = interpret("|F", angle=25.0, step=3.0)
    # 90 + 180 = 270 => down
    assert segs == [Segment((0.0, 0.0), (0.0, -3.0))]


def test_complex_sequence_segments_count_and_positions() -> None:
    # F[+F][-F]F with angle=90 and step=1
    segs = interpret("F[+F][-F]F", angle=90.0, step=1.0)
    assert len(segs) == 4
    assert segs[0] == Segment((0.0, 0.0), (0.0, 1.0))
    assert segs[1] == Segment((0.0, 1.0), (-1.0, 1.0))
    assert segs[2] == Segment((0.0, 1.0), (1.0, 1.0))
    assert segs[3] == Segment((0.0, 1.0), (0.0, 2.0))


def test_determinism_same_input_same_output() -> None:
    instr = "F[+F][-F]F|Ff+F-X"
    a = interpret(instr, angle=22.5, step=1.25)
    b = interpret(instr, angle=22.5, step=1.25)
    assert a == b


def test_unknown_symbols_are_ignored() -> None:
    segs = interpret("FXF", angle=90.0, step=1.0)
    assert segs == [
        Segment((0.0, 0.0), (0.0, 1.0)),
        Segment((0.0, 1.0), (0.0, 2.0)),
    ]


def test_unbalanced_pop_raises_value_error() -> None:
    with pytest.raises(ValueError):
        interpret("]", angle=25.0, step=1.0)
