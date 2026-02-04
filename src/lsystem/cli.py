from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lsystem.core import expand
from lsystem.presets import get_preset, list_presets
from lsystem.render_svg import render_svg, save_svg
from lsystem.turtle import interpret


def _positive_int(value: str) -> int:
    try:
        n = int(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError("must be an integer") from e
    if n <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return n


def _positive_float(value: str) -> float:
    try:
        x = float(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError("must be a number") from e
    if x <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return x


def _nonnegative_float(value: str) -> float:
    try:
        x = float(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError("must be a number") from e
    if x < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return x


def _validate_writable_path(path: Path) -> None:
    # If parent doesn't exist -> user error.
    parent = path.parent if path.parent != Path("") else Path(".")
    if not parent.exists():
        raise ValueError(f"output directory does not exist: {parent}")
    if not parent.is_dir():
        raise ValueError(f"output parent is not a directory: {parent}")

    # If file exists and is a directory -> user error.
    if path.exists() and path.is_dir():
        raise ValueError(f"output path is a directory: {path}")

    # Best-effort writability check without creating/truncating the target file.
    # Attempt to open for append in the parent dir by creating a temporary file name.
    # But minimal: rely on OS access check.
    try:
        # Will raise if no permissions.
        _ = list(parent.iterdir())
    except OSError as e:
        raise ValueError(f"output directory is not readable/writable: {parent}") from e


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lsystem",
        description="Generate L-system plant SVGs from bundled presets.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List available presets")
    p_list.set_defaults(func=_cmd_list)

    p_render = sub.add_parser("render", help="Render a preset to an SVG file")
    p_render.add_argument("preset", help="Preset name (see: lsystem list)")
    p_render.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output file path (default: <preset>.svg)",
    )
    p_render.add_argument(
        "--iterations",
        type=int,
        default=None,
        help="Override preset iteration count",
    )
    p_render.add_argument(
        "--angle",
        type=float,
        default=None,
        help="Override preset angle in degrees",
    )
    p_render.add_argument(
        "--step",
        type=float,
        default=None,
        help="Override preset step length",
    )
    p_render.add_argument("--width", type=_positive_int, default=800, help="Canvas width")
    p_render.add_argument(
        "--height", type=_positive_int, default=600, help="Canvas height"
    )
    p_render.add_argument(
        "--stroke",
        default="#228B22",
        help="Stroke color (default: forest green)",
    )
    p_render.add_argument(
        "--stroke-width",
        type=_positive_float,
        default=1.0,
        help="Line thickness",
    )
    p_render.add_argument(
        "--padding",
        type=_nonnegative_float,
        default=20.0,
        help="Padding around drawing (default: 20)",
    )
    p_render.set_defaults(func=_cmd_render)

    return parser


def _cmd_list(args: argparse.Namespace) -> int:
    names = list_presets()
    for name in names:
        # get_preset only raises KeyError if not found; but list_presets comes from same store
        preset = get_preset(name)
        print(f"{preset.name}\t{preset.description}")
    return 0


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        preset = get_preset(args.preset)
    except KeyError:
        raise ValueError(f"unknown preset: {args.preset}")

    out_path = Path(args.output) if args.output is not None else Path(f"{preset.name}.svg")
    _validate_writable_path(out_path)

    iterations = preset.iterations if args.iterations is None else args.iterations
    angle = preset.angle if args.angle is None else args.angle
    step = preset.step if args.step is None else args.step

    if iterations < 0:
        raise ValueError("iterations must be >= 0")

    # Expand and interpret
    expanded = expand(preset.system, iterations)
    segments = interpret(expanded, angle=float(angle), step=float(step))

    svg = render_svg(
        segments,
        width=int(args.width),
        height=int(args.height),
        stroke=str(args.stroke),
        stroke_width=float(args.stroke_width),
        padding=float(args.padding),
    )

    # Status to stderr, keep stdout clean
    print(f"Rendering '{preset.name}' -> {out_path}", file=sys.stderr)
    save_svg(svg, out_path)
    print(f"Wrote {out_path}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return int(args.func(args))
    except argparse.ArgumentError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except SystemExit as e:
        # argparse uses SystemExit for --help and parse errors.
        code = int(e.code) if e.code is not None else 0
        # Normalize parse errors to exit code 1 (help already exits 0).
        return 1 if code != 0 else 0
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # pragma: no cover
        print(f"internal error: {e}", file=sys.stderr)
        return 2
