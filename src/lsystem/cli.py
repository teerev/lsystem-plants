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
        i = int(value)
    except ValueError as e:  # pragma: no cover
        raise argparse.ArgumentTypeError("must be an integer") from e
    if i <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return i


def _non_negative_int(value: str) -> int:
    try:
        i = int(value)
    except ValueError as e:  # pragma: no cover
        raise argparse.ArgumentTypeError("must be an integer") from e
    if i < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return i


def _positive_float(value: str) -> float:
    try:
        f = float(value)
    except ValueError as e:  # pragma: no cover
        raise argparse.ArgumentTypeError("must be a number") from e
    if f <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return f


def _ensure_writable_file(path: Path) -> None:
    # Validate before doing any heavy work.
    # - If parent exists: must be writable.
    # - If parent does not exist: must be creatable (some existing ancestor writable).
    # - If file exists: must be a file and writable.
    if path.exists():
        if not path.is_file():
            raise ValueError(f"output path is not a file: {path}")
        try:
            with path.open("a", encoding="utf-8"):
                pass
        except OSError as e:
            raise ValueError(f"output file not writable: {path}") from e
        return

    parent = path.parent
    if parent.exists():
        if not parent.is_dir():
            raise ValueError(f"output directory is not a directory: {parent}")
        try:
            # Creating and deleting a temp sibling is overkill; just test we can create the target.
            parent.mkdir(parents=True, exist_ok=True)
            with path.open("w", encoding="utf-8"):
                pass
            path.unlink(missing_ok=True)
        except OSError as e:
            raise ValueError(f"output path not writable: {path}") from e
        return

    # Parent doesn't exist: find nearest existing parent to test writability.
    probe = parent
    while not probe.exists():
        nxt = probe.parent
        if nxt == probe:
            break
        probe = nxt

    if probe.exists() and not probe.is_dir():
        raise ValueError(f"output directory is not a directory: {probe}")

    try:
        parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8"):
            pass
        path.unlink(missing_ok=True)
    except OSError as e:
        raise ValueError(f"output path not writable: {path}") from e


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lsystem",
        description="Generate L-system plant SVGs from built-in presets.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list", help="List available presets")
    p_list.set_defaults(_handler="list")

    p_render = subparsers.add_parser("render", help="Render a preset to an SVG")
    p_render.add_argument("preset", help="Preset name")
    p_render.add_argument(
        "--output",
        default=None,
        help="Output file path (default: <preset>.svg)",
    )
    p_render.add_argument(
        "--iterations",
        type=_non_negative_int,
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
        type=_positive_float,
        default=None,
        help="Override preset step length",
    )
    p_render.add_argument(
        "--width",
        type=_positive_int,
        default=800,
        help="Canvas width in pixels (default: 800)",
    )
    p_render.add_argument(
        "--height",
        type=_positive_int,
        default=600,
        help="Canvas height in pixels (default: 600)",
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
    p_render.set_defaults(_handler="render")

    return parser


def _cmd_list() -> int:
    # Nicely formatted: "name\t- description".
    for name in list_presets():
        try:
            preset = get_preset(name)
        except KeyError:  # pragma: no cover
            continue
        print(f"{preset.name}\t- {preset.description}")
    return 0


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        preset = get_preset(str(args.preset))
    except KeyError as e:
        print(str(e), file=sys.stderr)
        return 1

    output = Path(args.output) if args.output else Path(f"{preset.name}.svg")
    try:
        _ensure_writable_file(output)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    iterations = preset.iterations if args.iterations is None else int(args.iterations)
    angle = preset.angle if args.angle is None else float(args.angle)
    step = preset.step if args.step is None else float(args.step)

    try:
        print(
            f"Rendering preset '{preset.name}' to {output}...",
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
        save_svg(svg, output)
        print(f"Wrote {output}", file=sys.stderr)
        return 0
    except Exception as e:  # internal error
        print(f"internal error: {e}", file=sys.stderr)
        return 2


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    handler = getattr(args, "_handler", None)
    if handler == "list":
        return _cmd_list()
    if handler == "render":
        return _cmd_render(args)

    # Should be unreachable due to required subparser
    parser.print_help()
    return 1
