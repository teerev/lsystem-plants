from __future__ import annotations

from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Regenerate golden fixture files under tests/fixtures/golden/",
    )


@pytest.fixture(scope="session")
def update_golden(pytestconfig: pytest.Config) -> bool:
    return bool(pytestconfig.getoption("--update-golden"))


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def golden_dir(fixtures_dir: Path) -> Path:
    return fixtures_dir / "golden"
