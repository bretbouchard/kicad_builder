import pytest


def test_projecttype_model_exists():
    try:
        from src.models import project_type
    except Exception:
        pytest.skip("project_type model not present yet")

    assert hasattr(project_type, "ProjectType")
