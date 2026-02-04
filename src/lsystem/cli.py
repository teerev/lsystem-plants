from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lsystem.core import MAX_ITERATIONS, expand
from lsystem.presets import get_preset, list_presets
from lsystem.render_svg import render_svg, save_svg
from lsystem.turtle import interpret


def _positive_int(value: str) -> int:
    try:
        n = int(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"invalid int value: {value!r}") from e
    if n <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return n


def _nonnegative_int(value: str) -> int:
    try:
        n = int(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"invalid int value: {value!r}") from e
    if n < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return n


def _positive_float(value: str) -> float:
    try:
        n = float(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"invalid float value: {value!r}") from e
    if n <= 0:
        raise argparse.ArgumentTypeError("must be a positive number")
    return n


def _validate_output_path(path: Path) -> None:
    # Validate writability before doing any heavy work.
    # - If parent doesn't exist, ensure we can create it.
    # - If file exists, ensure it's writable.
    # - If file doesn't exist, ensure parent dir is writable.
    parent = path.parent
    if str(path) == "":
        raise ValueError("output path must be non-empty")

    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise ValueError(f"cannot create output directory: {parent}") from e

    if path.exists():
        if path.is_dir():
            raise ValueError(f"output path is a directory: {path}")
        try:
            with path.open("a", encoding="utf-8"):
                pass
        except OSError as e:
            raise ValueError(f"output file is not writable: {path}") from e
    else:
        # Check parent directory is writable by attempting to create a temp file name.
        # We avoid creating the actual output file here.
        try:
            test = parent / (".lsystem_write_test")
            with test.open("w", encoding="utf-8") as f:
                f.write("test")
            test.unlink(missing_ok=True)
        except OSError as e:
            raise ValueError(f"output directory is not writable: {parent}") from e


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lsystem",
        description="Generate L-system plant SVG images.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list", help="List available presets")
    p_list.set_defaults(_handler=_cmd_list)

    p_render = subparsers.add_parser("render", help="Render a preset to an SVG")
    p_render.add_argument("preset", help="Preset name (see: lsystem list)")
    p_render.add_argument(
        "--output",
        default=None,
        help="Output file path (default: <preset>.svg)",
    )
    p_render.add_argument(
        "--iterations",
        type=_nonnegative_int,
        default=None,
        help=f"Override preset iteration count (max {MAX_ITERATIONS})",
    )
    p_render.add_argument(
        "--angle",
        type=float,
        default=None,
        help="Override preset turning angle in degrees",
    )
    p_render.add_argument(
        "--step",
        type=_positive_float,
        default=None,
        help="Override preset step length",
    )
    p_render.add_argument("--width", type=_positive_int, default=800, help="Canvas width")
    p_render.add_argument("--height", type=_positive_int, default=600, help="Canvas height")
    p_render.add_argument(
        "--stroke",
        default="#228B22",
        help='Stroke color (default: "#228B22" / forest green)',
    )
    p_render.add_argument(
        "--stroke-width",
        type=_positive_float,
        default=1.0,
        dest="stroke_width",
        help="Line thickness",
    )
    p_render.set_defaults(_handler=_cmd_render)

    return parser


def _cmd_list(args: argparse.Namespace) -> int:
    for name in list_presets():
        preset = get_preset(name)
        print(f"{name}\t{preset.description}")
    return 0


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        preset = get_preset(args.preset)
    except KeyError:
        available = ", ".join(list_presets())
        raise ValueError(f"unknown preset: {args.preset!r}. Available: {available}")

    iterations = preset.iterations if args.iterations is None else int(args.iterations)
    angle = preset.angle if args.angle is None else float(args.angle)
    step = preset.step if args.step is None else float(args.step)

    out_path = Path(f"{preset.name}.svg") if args.output is None else Path(args.output)
    _validate_output_path(out_path)

    # Work
    print(
        f"Rendering preset '{preset.name}' to {out_path}...",
        file=sys.stderr,
    )

    expanded = expand(preset.system, iterations)
    segments = interpret(expanded, angle=angle, step=step)
    svg = render_svg(
        segments,
        width=int(args.width),
        height=int(args.height),
        stroke=str(args.stroke),
        stroke_width=float(args.stroke_width),
    )
    save_svg(svg, out_path)

    print(f"Wrote {out_path}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        handler = getattr(args, "_handler")
        return int(handler(args))
    except SystemExit as e:
        # argparse uses SystemExit(0/2). Treat parse errors as user errors (1)
        # per project contract.
        code = int(getattr(e, "code", 0) or 0)
        if code == 0:
            return 0
        return 1
    except (ValueError, TypeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # pragma: no cover
        print(f"internal error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
