import importlib

import pytest


def test_validation_engine_contract():
    try:
        validation_engine = importlib.import_module("src.services.validation_engine")
    except Exception:
        pytest.skip("validation_engine module not importable")

    assert hasattr(validation_engine, "validate_project_config")

    # Build a ProjectConfig instance and call the validator
    from src.models.project_config import ProjectConfig

    cfg = ProjectConfig(project_name="t", project_type="test")
    assert validation_engine.validate_project_config(cfg) is True
