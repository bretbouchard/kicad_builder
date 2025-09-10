from pathlib import Path

from src.services import auto_register
from src.lib import generator_registry as registry


def test_auto_register_happy_and_failure(tmp_path: Path):
    registry.clear_registry()

    good = tmp_path / "good.py"
    bad = tmp_path / "bad.py"

    # good exports GENERATOR
    good.write_text(
        "from src.lib.generators.template_generator import GENERATOR\n",
        encoding="utf8",
    )

    # bad module has syntax error
    bad.write_text("def oops(:\n", encoding="utf8")

    # Run auto register and expect it to raise because bad.py is broken
    try:
        auto_register.auto_register_generators(search_paths=[tmp_path])
        raise AssertionError("expected auto_register to raise on broken module")
    except RuntimeError as e:
        msg = str(e)
        assert "failed to import" in msg or "does not export" in msg

    # Fix bad file and rerun: should succeed
    bad.write_text("# fixed\n", encoding="utf8")
    # Remove the broken module and clear registry, then rerun: should succeed
    bad.unlink()
    registry.clear_registry()
    auto_register.auto_register_generators(search_paths=[tmp_path])
    # At least one registered generator should be the template
    names = registry.list_generators()
    assert any("template" in n for n in names)
