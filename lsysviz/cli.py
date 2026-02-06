from __future__ import annotations

import argparse

from . import __version__
from .expand import expand
from .render import render_to_png
from .turtle import interpret
from .types import Grammar


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lsysviz")
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version information and exit.",
    )

    parser.add_argument(
        "--axiom",
        type=str,
        required=True,
        help="Starting axiom string for the L-system.",
    )
    parser.add_argument(
        "--rule",
        type=str,
        action="append",
        required=True,
        help="Rewrite rule in the form 'SYMBOL=REPLACEMENT' (repeatable).",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        required=True,
        help="Number of expansion iterations.",
    )
    parser.add_argument(
        "--angle",
        type=float,
        required=True,
        help="Turn angle in degrees.",
    )
    parser.add_argument(
        "--step",
        type=float,
        required=True,
        help="Step length for forward moves.",
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="Output PNG path.",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=800,
        help="Output image width in pixels (default: 800).",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=600,
        help="Output image height in pixels (default: 600).",
    )

    return parser


def _parse_rules(rule_args: list[str]) -> dict[str, str]:
    rules: dict[str, str] = {}
    for raw in rule_args:
        if "=" not in raw:
            raise ValueError(f"Invalid --rule '{raw}': expected format SYMBOL=REPLACEMENT")
        symbol, replacement = raw.split("=", 1)
        if symbol == "":
            raise ValueError(f"Invalid --rule '{raw}': SYMBOL must be non-empty")
        rules[symbol] = replacement
    return rules


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    rules = _parse_rules(args.rule)
    grammar = Grammar(axiom=args.axiom, rules=rules)

    lstring = expand(grammar, iterations=args.iterations)
    segments = interpret(lstring, angle_deg=args.angle, step_length=args.step)
    render_to_png(segments, width=args.width, height=args.height, output_path=args.output)

    return 0
