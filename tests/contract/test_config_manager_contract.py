import importlib

import pytest


def test_config_manager_contract_api():
    try:
        config_manager = importlib.import_module("src.services.config_manager")
    except Exception:
        pytest.skip("src.services.config_manager not importable")

    assert hasattr(config_manager, "load")
    assert hasattr(config_manager, "save")
    assert hasattr(config_manager, "validate")

    # Try validating a minimal dict to ensure validate returns a ProjectConfig
    from src.models.project_config import ProjectConfig

    sample = {"project_name": "x", "project_type": "test"}
    validated = config_manager.validate(sample)
    assert isinstance(validated, ProjectConfig)
