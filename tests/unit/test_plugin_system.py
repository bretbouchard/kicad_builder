from pathlib import Path

from src.services import plugin_system


def test_discover_and_load(tmp_path: Path):
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    plugin_file = plugins_dir / "p1.py"
    plugin_file.write_text("VALUE = 42\n")

    found = plugin_system.discover(plugins_dir)
    assert plugin_file in found

    mod = plugin_system.load(plugin_file)
    assert hasattr(mod, "VALUE")
    assert getattr(mod, "VALUE") == 42
