from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from lsystem.core import MAX_ITERATIONS, expand
from lsystem.presets import Preset, get_preset, list_presets
from lsystem.render_svg import render_svg, save_svg
from lsystem.turtle import interpret


DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
DEFAULT_STROKE = "#228B22"  # forest green
DEFAULT_STROKE_WIDTH = 1.0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lsystem",
        description="Generate plant-like L-system SVG images.",
    )

    subparsers = parser.add_subparsers(dest="command")

    p_list = subparsers.add_parser("list", help="List available presets")
    p_list.set_defaults(func=_cmd_list)

    p_render = subparsers.add_parser("render", help="Render a preset to an SVG")
    p_render.add_argument("preset", help="Preset name")
    p_render.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: <preset>.svg)",
    )
    p_render.add_argument(
        "--iterations",
        type=int,
        default=None,
        help=f"Override preset iteration count (max {MAX_ITERATIONS})",
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
    p_render.add_argument(
        "--width",
        type=int,
        default=DEFAULT_WIDTH,
        help=f"Canvas width in pixels (default: {DEFAULT_WIDTH})",
    )
    p_render.add_argument(
        "--height",
        type=int,
        default=DEFAULT_HEIGHT,
        help=f"Canvas height in pixels (default: {DEFAULT_HEIGHT})",
    )
    p_render.add_argument(
        "--stroke",
        type=str,
        default=DEFAULT_STROKE,
        help=f"Stroke color (default: {DEFAULT_STROKE})",
    )
    p_render.add_argument(
        "--stroke-width",
        type=float,
        default=DEFAULT_STROKE_WIDTH,
        help=f"Line thickness (default: {DEFAULT_STROKE_WIDTH})",
    )
    p_render.set_defaults(func=_cmd_render)

    return parser


def _validate_writable_path(path: Path) -> None:
    # Disallow directories as output.
    if path.exists() and path.is_dir():
        raise ValueError(f"output path is a directory: {path}")

    parent = path.parent if str(path.parent) != "" else Path(".")

    # Ensure parent exists or can be created (we create in save_svg as well,
    # but validate early per requirements).
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise ValueError(f"cannot create output directory: {parent}") from e

    # Check writability by opening the file for write (no truncation side-effects
    # if it already exists). This is the most reliable cross-platform check.
    try:
        with open(path, "a", encoding="utf-8"):
            pass
    except OSError as e:
        raise ValueError(f"output path is not writable: {path}") from e


def _cmd_list(_args: argparse.Namespace) -> int:
    # Print name + description per line.
    for name in list_presets():
        preset = get_preset(name)
        print(f"{preset.name}\t{preset.description}")
    return 0


def _apply_overrides(preset: Preset, args: argparse.Namespace) -> tuple[int, float, float]:
    iterations = preset.iterations if args.iterations is None else args.iterations
    angle = preset.angle if args.angle is None else args.angle
    step = preset.step if args.step is None else args.step
    return iterations, angle, step


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        preset = get_preset(args.preset)
    except KeyError:
        available = ", ".join(list_presets())
        print(
            f"error: unknown preset '{args.preset}'. Available presets: {available}",
            file=sys.stderr,
        )
        return 1

    output = args.output if args.output is not None else Path(f"{preset.name}.svg")

    # Validate output path before any heavy work
    try:
        _validate_writable_path(output)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    # Validate numeric args
    if args.width <= 0 or args.height <= 0:
        print("error: --width and --height must be positive", file=sys.stderr)
        return 1
    if args.stroke_width <= 0:
        print("error: --stroke-width must be positive", file=sys.stderr)
        return 1

    try:
        iterations, angle, step = _apply_overrides(preset, args)
        expanded = expand(preset.system, iterations)
        segments = interpret(expanded, angle=angle, step=step)
        svg = render_svg(
            segments,
            width=args.width,
            height=args.height,
            stroke=args.stroke,
            stroke_width=args.stroke_width,
        )
        save_svg(svg, output)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # internal error
        print(f"internal error: {e}", file=sys.stderr)
        return 2

    print(f"Rendered '{preset.name}' to {output}", file=sys.stderr)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return int(args.func(args))
