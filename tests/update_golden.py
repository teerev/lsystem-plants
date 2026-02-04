from __future__ import annotations

# Optional helper for developers. The work order's acceptance uses pytest
# with --update-golden, but this module provides an explicit entrypoint too.

import subprocess
import sys


def main() -> int:
    cmd = [sys.executable, "-m", "pytest", "tests/test_golden.py", "-v", "--update-golden"]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
