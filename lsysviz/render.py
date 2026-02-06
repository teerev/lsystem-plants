from __future__ import annotations

from typing import Iterable

from .types import Segment


def render_to_png(segments: list[Segment], width: int, height: int, output_path: str) -> None:
    """Render a list of line segments to a PNG image.

    Creates a white RGB image of the given dimensions, fits all segments into the
    image with padding, draws them as black 1px lines, and saves to output_path.

    The output is deterministic for identical inputs.
    """

    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    # Try Pillow first (preferred). If not available, fall back to a minimal
    # pure-Python PNG writer + line rasterizer.
    try:
        from PIL import Image, ImageDraw  # type: ignore

        img = Image.new("RGB", (width, height), (255, 255, 255))
        if segments:
            draw = ImageDraw.Draw(img)
            mapped = _map_segments_to_image(segments, width, height, margin_frac=0.10)
            for x0, y0, x1, y1 in mapped:
                # Use integer pixel coordinates for determinism.
                draw.line((x0, y0, x1, y1), fill=(0, 0, 0), width=1)

        # Ensure deterministic encoding: disable metadata and use fixed settings.
        img.save(output_path, format="PNG", optimize=False)
        return
    except ModuleNotFoundError:
        pass

    # Fallback: pure-Python deterministic PNG writer.
    pixels = _new_white_pixels(width, height)
    if segments:
        mapped = _map_segments_to_image(segments, width, height, margin_frac=0.10)
        for x0, y0, x1, y1 in mapped:
            _draw_line_bresenham(pixels, width, height, x0, y0, x1, y1)

    _write_png_rgb(output_path, width, height, pixels)


def _map_segments_to_image(
    segments: Iterable[Segment],
    width: int,
    height: int,
    margin_frac: float = 0.10,
) -> list[tuple[int, int, int, int]]:
    segs = list(segments)
    if not segs:
        return []

    xs = [s.x0 for s in segs] + [s.x1 for s in segs]
    ys = [s.y0 for s in segs] + [s.y1 for s in segs]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # Handle degenerate bounds.
    span_x = max_x - min_x
    span_y = max_y - min_y
    if span_x == 0:
        span_x = 1.0
    if span_y == 0:
        span_y = 1.0

    # Padding in pixels.
    pad_x = int(round(width * margin_frac))
    pad_y = int(round(height * margin_frac))
    inner_w = max(1, width - 2 * pad_x)
    inner_h = max(1, height - 2 * pad_y)

    # Uniform scale to preserve aspect ratio.
    scale = min(inner_w / span_x, inner_h / span_y)

    # Center within inner box.
    content_w = span_x * scale
    content_h = span_y * scale
    offset_x = pad_x + (inner_w - content_w) / 2.0
    offset_y = pad_y + (inner_h - content_h) / 2.0

    def map_point(x: float, y: float) -> tuple[int, int]:
        # Map to image coordinates; y increases downward.
        px = offset_x + (x - min_x) * scale
        py = offset_y + (y - min_y) * scale
        # Deterministic rounding.
        ix = int(round(px))
        iy = int(round(py))
        # Clamp to image bounds.
        if ix < 0:
            ix = 0
        elif ix >= width:
            ix = width - 1
        if iy < 0:
            iy = 0
        elif iy >= height:
            iy = height - 1
        return ix, iy

    out: list[tuple[int, int, int, int]] = []
    for s in segs:
        x0, y0 = map_point(s.x0, s.y0)
        x1, y1 = map_point(s.x1, s.y1)
        out.append((x0, y0, x1, y1))
    return out


def _new_white_pixels(width: int, height: int) -> bytearray:
    # RGB packed, row-major.
    return bytearray(b"\xff\xff\xff" * (width * height))


def _set_pixel(pixels: bytearray, width: int, height: int, x: int, y: int, rgb: tuple[int, int, int]) -> None:
    if x < 0 or y < 0 or x >= width or y >= height:
        return
    i = (y * width + x) * 3
    pixels[i] = rgb[0]
    pixels[i + 1] = rgb[1]
    pixels[i + 2] = rgb[2]


def _draw_line_bresenham(
    pixels: bytearray,
    width: int,
    height: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
) -> None:
    # Integer Bresenham line drawing.
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    x, y = x0, y0
    while True:
        _set_pixel(pixels, width, height, x, y, (0, 0, 0))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def _write_png_rgb(path: str, width: int, height: int, pixels: bytearray) -> None:
    """Write an RGB PNG deterministically (no ancillary chunks)."""

    import struct
    import zlib

    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = zlib.crc32(chunk_type)
        crc = zlib.crc32(data, crc) & 0xFFFFFFFF
        return length + chunk_type + data + struct.pack(">I", crc)

    # Build raw scanlines with filter type 0 per row.
    stride = width * 3
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0
        start = y * stride
        raw.extend(pixels[start : start + stride])

    # Deterministic zlib stream: fixed compression level and strategy.
    compressed = zlib.compress(bytes(raw), level=9)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit, truecolor
    data = (
        signature
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )

    with open(path, "wb") as f:
        f.write(data)
