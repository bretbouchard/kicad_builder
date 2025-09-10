import pytest


def test_plugin_system_api():
    try:
        from src.services import auto_register  # type: ignore
    except Exception as e:
        pytest.fail(f"auto_register import failed: {e}")

    assert hasattr(auto_register, "auto_register_generators")
    assert hasattr(auto_register, "AutoRegisterError")


def test_config_manager_interface():
    try:
        from src.services import config_manager  # type: ignore
    except Exception as e:
        pytest.fail(f"config_manager import failed: {e}")

    for fn in ("load", "save", "validate"):
        assert hasattr(config_manager, fn), f"config_manager must implement {fn}()"


def test_validation_engine_api():
    try:
        from src.services import validation_engine  # type: ignore
    except Exception as e:
        pytest.fail(f"validation_engine import failed: {e}")

    assert hasattr(validation_engine, "validate_project_config")
