import pytest

from lsystem.turtle import Segment, TurtleState, interpret


def test_state_and_segment_types() -> None:
    s = TurtleState(1.0, 2.0, 30.0)
    assert (s.x, s.y, s.angle) == (1.0, 2.0, 30.0)

    seg = Segment((0.0, 0.0), (0.0, 1.0))
    assert seg.start == (0.0, 0.0)
    assert seg.end == (0.0, 1.0)


def test_empty_string_returns_empty() -> None:
    assert interpret("", angle=90.0, step=1.0) == []


def test_forward_draw() -> None:
    segs = interpret("F", angle=90.0, step=2.0)
    assert len(segs) == 1
    assert segs[0] == Segment((0.0, 0.0), (0.0, 2.0))


def test_forward_no_draw() -> None:
    segs = interpret("fF", angle=90.0, step=1.0)
    assert len(segs) == 1
    assert segs[0] == Segment((0.0, 1.0), (0.0, 2.0))


def test_turn_left() -> None:
    # start at 90 deg (up); '+' adds 90 => 180 deg (left)
    segs = interpret("+F", angle=90.0, step=1.0)
    assert segs == [Segment((0.0, 0.0), (-1.0, 0.0))]


def test_turn_right() -> None:
    # start at 90 deg (up); '-' subtracts 90 => 0 deg (right)
    segs = interpret("-F", angle=90.0, step=1.0)
    assert segs == [Segment((0.0, 0.0), (1.0, 0.0))]


def test_push_pop_restores_state() -> None:
    # [F] draws up to y=1 but pops back to origin before the final F
    segs = interpret("[F]F", angle=90.0, step=1.0)
    assert segs == [
        Segment((0.0, 0.0), (0.0, 1.0)),
        Segment((0.0, 0.0), (0.0, 1.0)),
    ]


def test_turn_180() -> None:
    # '|' flips 180 degrees: 90 -> 270, so move down
    segs = interpret("|F", angle=90.0, step=1.0)
    assert segs == [Segment((0.0, 0.0), (0.0, -1.0))]


def test_complex_sequence() -> None:
    # F (up)
    # [ +F ] (branch left from y=1)
    # [ -F ] (branch right from y=1)
    # F (up from y=1)
    segs = interpret("F[+F][-F]F", angle=90.0, step=1.0)
    assert segs == [
        Segment((0.0, 0.0), (0.0, 1.0)),
        Segment((0.0, 1.0), (-1.0, 1.0)),
        Segment((0.0, 1.0), (1.0, 1.0)),
        Segment((0.0, 1.0), (0.0, 2.0)),
    ]


def test_determinism_same_input_same_output() -> None:
    instr = "F[+F][-F]F|FfF"
    a = interpret(instr, angle=25.0, step=1.234)
    b = interpret(instr, angle=25.0, step=1.234)
    assert a == b


def test_unknown_symbols_ignored() -> None:
    segs = interpret("FXYF", angle=90.0, step=1.0)
    assert segs == [
        Segment((0.0, 0.0), (0.0, 1.0)),
        Segment((0.0, 1.0), (0.0, 2.0)),
    ]


def test_unbalanced_pop_raises() -> None:
    with pytest.raises(ValueError):
        interpret("]", angle=90.0, step=1.0)
