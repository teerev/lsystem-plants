from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lsystem.core import expand
from lsystem.presets import get_preset, list_presets
from lsystem.render_svg import render_svg, save_svg
from lsystem.turtle import interpret


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lsystem",
        description="Generate plant-like SVG images using deterministic L-systems.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List available presets")
    p_list.set_defaults(_cmd="list")

    p_render = sub.add_parser("render", help="Render a preset to an SVG file")
    p_render.add_argument("preset", help="Preset name (see: lsystem list)")
    p_render.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output SVG path (default: <preset>.svg)",
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
    p_render.add_argument("--width", type=int, default=800, help="Canvas width")
    p_render.add_argument("--height", type=int, default=600, help="Canvas height")
    p_render.add_argument(
        "--stroke",
        type=str,
        default="#228B22",
        help="Stroke color",
    )
    p_render.add_argument(
        "--stroke-width",
        type=float,
        default=1.0,
        help="Line thickness",
    )
    p_render.set_defaults(_cmd="render")

    return parser


def _validate_writable_path(path: Path) -> None:
    # Ensure parent exists or can be created; ensure file can be written.
    parent = path.parent if str(path.parent) not in ("", ".") else Path(".")
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise ValueError(f"cannot create output directory: {parent}") from e

    if parent.exists() and not parent.is_dir():
        raise ValueError(f"output directory is not a directory: {parent}")

    try:
        # Try opening for write without clobbering content for long.
        with open(path, "a", encoding="utf-8"):
            pass
    except OSError as e:
        raise ValueError(f"output path is not writable: {path}") from e


def _cmd_list() -> int:
    for name in list_presets():
        preset = get_preset(name)
        print(f"{preset.name}: {preset.description}")
    return 0


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        preset = get_preset(args.preset)
    except KeyError:
        raise ValueError(f"unknown preset: {args.preset}")

    out_path = Path(args.output) if args.output else Path(f"{preset.name}.svg")

    iterations = preset.iterations if args.iterations is None else int(args.iterations)
    angle = preset.angle if args.angle is None else float(args.angle)
    step = preset.step if args.step is None else float(args.step)

    width = int(args.width)
    height = int(args.height)
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    if iterations < 0:
        raise ValueError("iterations must be >= 0")
    if step <= 0:
        raise ValueError("step must be positive")

    _validate_writable_path(out_path)

    print(
        f"Rendering preset '{preset.name}' -> {out_path} (iterations={iterations})",
        file=sys.stderr,
    )

    expanded = expand(preset.system, iterations)
    segments = interpret(expanded, angle=angle, step=step)
    svg = render_svg(
        segments,
        width=width,
        height=height,
        stroke=args.stroke,
        stroke_width=float(args.stroke_width),
    )
    save_svg(svg, out_path)

    print(f"Wrote {out_path}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
        if args._cmd == "list":
            return _cmd_list()
        if args._cmd == "render":
            return _cmd_render(args)
        # Should be unreachable due to required subcommand.
        parser.print_help()
        return 1
    except SystemExit as e:
        # argparse uses SystemExit for --help and parse errors.
        code = int(getattr(e, "code", 0) or 0)
        return 0 if code == 0 else 1
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    except Exception as e:  # pragma: no cover
        print(f"internal error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
