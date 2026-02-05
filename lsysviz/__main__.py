"""Module entry point for `python -m lsysviz`.

Behavior is intentionally minimal; CLI wiring is frozen for later expansion.
"""

from __future__ import annotations

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())
