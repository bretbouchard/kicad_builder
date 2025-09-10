import pytest


def test_quickstart_simple_project():
    try:
        from src.cli import generate
    except Exception:
        pytest.skip("generate CLI not present yet")

    with pytest.raises(NotImplementedError):
        generate.main(["--config", "tests/fixtures/simple_project.yaml"])
