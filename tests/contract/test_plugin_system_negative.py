import importlib
from pathlib import Path

import pytest


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf8")


def test_auto_register_fails_on_module_without_exports(tmp_path):
    """If a module doesn't export GENERATOR or register(), auto-register must
    report a clear failure."""
    mod = tmp_path / "no_export.py"
    _write(mod, "# intentionally empty\nX = 1\n")

    auto_register = importlib.import_module("src.services.auto_register")

    with pytest.raises(auto_register.AutoRegisterError) as excinfo:
        auto_register.auto_register_generators(search_paths=[tmp_path])

    # Ensure structured failures are present
    failures = excinfo.value.failures
    assert any(f["type"] == "no_entrypoint" for f in failures)


def test_auto_register_reports_register_callable_exceptions(tmp_path):
    """If a plugin's register() raises, auto-register should include the
    raised message in the aggregated RuntimeError."""
    mod = tmp_path / "bad_register.py"
    _write(mod, "def register(reg):\n    raise ValueError('boom')\n")

    auto_register = importlib.import_module("src.services.auto_register")

    with pytest.raises(auto_register.AutoRegisterError) as excinfo:
        auto_register.auto_register_generators(search_paths=[tmp_path])

    failures = excinfo.value.failures
    assert any(f["type"] == "register_callable" for f in failures)
    assert any("boom" in f["message"] for f in failures)


def test_auto_register_detects_duplicate_generator_names(tmp_path):
    """Two modules exporting GENERATOR with the same name should cause a
    duplicate registration failure to be reported."""
    # Create two modules exporting GENERATOR objects with identical names.
    mod1 = tmp_path / "dup1.py"
    mod2 = tmp_path / "dup2.py"
    # Minimal generator-like objects with required attributes
    content = (
        "class G:\n"
        "    def __init__(self):\n"
        "        self.name = 'dup'\n"
        "    def generate(self, c, o):\n"
        "        pass\n"
        "    def validate(self, c):\n"
        "        return True\n"
        "GENERATOR = G()\n"
    )
    _write(mod1, content)
    _write(mod2, content)

    # Ensure fresh import context so modules load from tmp_path files
    auto_register = importlib.import_module("src.services.auto_register")
    registry = importlib.import_module("src.lib.generator_registry")
    registry.clear_registry()

    with pytest.raises(auto_register.AutoRegisterError) as excinfo:
        auto_register.auto_register_generators(search_paths=[tmp_path])

    failures = excinfo.value.failures
    assert any(f["type"] == "register" for f in failures) or any(f["type"] == "import" for f in failures)
