import pytest


def test_generator_model_exists():
    try:
        from src.models import generator
    except Exception:
        pytest.skip("generator model not present yet")

    assert hasattr(generator, "Generator")
