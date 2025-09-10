import pytest


def test_project_type_model_exists():
    try:
        from src.models import project_type  # type: ignore
    except Exception as e:
        pytest.fail(f"src.models.project_type import failed: {e}")

    assert hasattr(project_type, "ProjectType")


def test_generator_model_exists():
    try:
        from src.models import generator  # type: ignore
    except Exception as e:
        pytest.fail(f"src.models.generator import failed: {e}")

    assert hasattr(generator, "Generator")
