import pytest

from lsystem.turtle import Segment, interpret


def test_empty_string_returns_empty_list() -> None:
    assert interpret("", angle=90.0, step=1.0) == []


def test_forward_draw_produces_one_segment_up() -> None:
    segs = interpret("F", angle=90.0, step=2.0)
    assert len(segs) == 1
    assert segs[0] == Segment(start=(0.0, 0.0), end=(0.0, 2.0))


def test_forward_no_draw_moves_but_produces_no_segment() -> None:
    segs = interpret("fF", angle=90.0, step=1.0)
    assert len(segs) == 1
    # First 'f' moves from (0,0) to (0,1) without drawing.
    assert segs[0] == Segment(start=(0.0, 1.0), end=(0.0, 2.0))


def test_turn_left_plus_is_counter_clockwise() -> None:
    # Start at 90 degrees (up). Turn left by 90 => 180 degrees (left).
    segs = interpret("+F", angle=90.0, step=1.0)
    assert segs == [Segment(start=(0.0, 0.0), end=(-1.0, 0.0))]


def test_turn_right_minus_is_clockwise() -> None:
    # Start at 90 degrees (up). Turn right by 90 => 0 degrees (right).
    segs = interpret("-F", angle=90.0, step=1.0)
    assert segs == [Segment(start=(0.0, 0.0), end=(1.0, 0.0))]


def test_push_pop_restores_state() -> None:
    # Draw up to (0,1), push, draw up to (0,2), pop back to (0,1),
    # then draw again to (0,2) from the restored state.
    segs = interpret("F[ F ]F".replace(" ", ""), angle=90.0, step=1.0)
    assert len(segs) == 3
    assert segs[0] == Segment(start=(0.0, 0.0), end=(0.0, 1.0))
    assert segs[1] == Segment(start=(0.0, 1.0), end=(0.0, 2.0))
    assert segs[2] == Segment(start=(0.0, 1.0), end=(0.0, 2.0))


def test_turn_180_pipe_reverses_direction() -> None:
    segs = interpret("|F", angle=25.0, step=1.0)
    # 90 + 180 = 270 degrees => down.
    assert segs == [Segment(start=(0.0, 0.0), end=(0.0, -1.0))]


def test_complex_sequence_branching_counts_and_positions() -> None:
    # F[+F][-F]F
    # 1) F: (0,0)->(0,1)
    # 2) [+F]: from (0,1) turn left 90 and draw to (-1,1), then pop
    # 3) [-F]: from (0,1) turn right 90 and draw to (1,1), then pop
    # 4) F: from (0,1)->(0,2)
    segs = interpret("F[+F][-F]F", angle=90.0, step=1.0)
    assert len(segs) == 4
    assert segs[0] == Segment(start=(0.0, 0.0), end=(0.0, 1.0))
    assert segs[1] == Segment(start=(0.0, 1.0), end=(-1.0, 1.0))
    assert segs[2] == Segment(start=(0.0, 1.0), end=(1.0, 1.0))
    assert segs[3] == Segment(start=(0.0, 1.0), end=(0.0, 2.0))


def test_determinism_same_input_same_output() -> None:
    a = interpret("F[+F][-F]F", angle=90.0, step=1.0)
    b = interpret("F[+F][-F]F", angle=90.0, step=1.0)
    assert a == b


def test_unknown_symbols_are_ignored() -> None:
    segs = interpret("XFYZ", angle=90.0, step=1.0)
    assert segs == [Segment(start=(0.0, 0.0), end=(0.0, 1.0))]


def test_unbalanced_pop_raises_value_error() -> None:
    with pytest.raises(ValueError):
        interpret("]", angle=90.0, step=1.0)
