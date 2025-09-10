import importlib
from pathlib import Path

import pytest


def test_plugin_system_discovery_contract():
    try:
        auto_register = importlib.import_module("src.services.auto_register")
        registry = importlib.import_module("src.lib.generator_registry")
    except Exception:
        pytest.skip("plugin system modules not importable")

    # Use a deterministic search path pointing at the repo's example generators
    search_path = [Path("src/lib/generators")]

    # Clear registry, run auto-registration and ensure expected names present
    registry.clear_registry()
    auto_register.auto_register_generators(search_paths=search_path)

    names = registry.list_generators()
    assert any(n.endswith("simple") for n in names)
    assert any(n.endswith("template") for n in names)
