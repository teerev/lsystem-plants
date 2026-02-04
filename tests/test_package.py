import re


def test_package_importable():
    import lsystem  # noqa: F401


def test_version_defined_semver():
    import lsystem

    assert isinstance(lsystem.__version__, str)
    # Basic semver (MAJOR.MINOR.PATCH)
    assert re.fullmatch(r"\d+\.\d+\.\d+", lsystem.__version__) is not None
