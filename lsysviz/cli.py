"""Command-line interface for lsysviz.

This is a scaffold-only stub. It exists to freeze the import roots and the
`python -m lsysviz` entry point without implementing L-system behavior yet.
"""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lsysviz")
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        # Keep import local to avoid any future side effects during parsing.
        from . import __version__

        print(__version__)
        return 0

    parser.print_help()
