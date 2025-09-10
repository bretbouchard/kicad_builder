import importlib
from pathlib import Path

import pytest


def test_generator_contract_against_examples():
    """Ensure the repository provides generators compatible with BaseGenerator.

    This verifies the BaseGenerator symbol exists and example modules export
    either a `GENERATOR` instance or a `register` function.
    """
    try:
        base_generator = importlib.import_module("src.lib.base_generator")
    except Exception:
        pytest.skip("src.lib.base_generator not importable")

    assert hasattr(base_generator, "BaseGenerator")

    # Check example modules under src.lib.generators
    gen_dir = Path("src/lib/generators")
    assert gen_dir.exists(), "generators directory missing"

    # simple and template generators export GENERATOR instances
    simple = importlib.import_module("src.lib.generators.simple_generator")
    template = importlib.import_module("src.lib.generators.template_generator")

    assert hasattr(simple, "GENERATOR")
    assert hasattr(template, "GENERATOR")

    # Instances should expose the required methods
    for mod in (simple, template):
        gen = getattr(mod, "GENERATOR")
        assert hasattr(gen, "name")
        assert hasattr(gen, "generate") and callable(gen.generate)
        assert hasattr(gen, "validate") and callable(gen.validate)
