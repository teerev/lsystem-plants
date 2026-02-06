import os
import tempfile

import pytest

from lsysviz.render import render_to_png
from lsysviz.types import Segment


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def test_render_non_empty_creates_valid_png() -> None:
    out_dir = tempfile.mkdtemp()
    out_path = os.path.join(out_dir, "non_empty.png")

    segments = [Segment(0.0, 0.0, 10.0, 10.0), Segment(10.0, 0.0, 0.0, 10.0)]
    render_to_png(segments=segments, width=64, height=64, output_path=out_path)

    assert os.path.exists(out_path)
    data = _read_bytes(out_path)
    assert data.startswith(PNG_MAGIC)


def test_render_empty_creates_file_blank_white_image() -> None:
    out_dir = tempfile.mkdtemp()
    out_path = os.path.join(out_dir, "empty.png")

    render_to_png(segments=[], width=32, height=16, output_path=out_path)

    assert os.path.exists(out_path)
    data = _read_bytes(out_path)
    assert data.startswith(PNG_MAGIC)

    # If Pillow is available, verify dimensions.
    try:
        from PIL import Image  # type: ignore

        with Image.open(out_path) as im:
            assert im.size == (32, 16)
    except ModuleNotFoundError:
        pass


def test_render_determinism_byte_identical_outputs() -> None:
    out_dir = tempfile.mkdtemp()
    out_path1 = os.path.join(out_dir, "det1.png")
    out_path2 = os.path.join(out_dir, "det2.png")

    segments = [
        Segment(0.0, 0.0, 10.0, 0.0),
        Segment(10.0, 0.0, 10.0, 10.0),
        Segment(10.0, 10.0, 0.0, 10.0),
        Segment(0.0, 10.0, 0.0, 0.0),
    ]

    render_to_png(segments=segments, width=80, height=60, output_path=out_path1)
    render_to_png(segments=segments, width=80, height=60, output_path=out_path2)

    b1 = _read_bytes(out_path1)
    b2 = _read_bytes(out_path2)
    assert b1 == b2


def test_render_negative_coordinates_no_error() -> None:
    out_dir = tempfile.mkdtemp()
    out_path = os.path.join(out_dir, "negative_coords.png")

    segments = [
        Segment(-10.0, -10.0, -5.0, -5.0),
        Segment(-20.0, 5.0, 15.0, -25.0),
    ]

    # Should not raise; renderer must map arbitrary coordinate ranges.
    render_to_png(segments=segments, width=64, height=64, output_path=out_path)

    assert os.path.exists(out_path)
    data = _read_bytes(out_path)
    assert data.startswith(PNG_MAGIC)
