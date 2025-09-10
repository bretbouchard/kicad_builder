import json
from importlib import import_module
from pathlib import Path

from src import cli
from src.lib import generator_registry as registry
from src.services import auto_register

# ensure submodule is loaded so linters and runtime have `generate` available
import_module("src.cli.generate")


def _write_config(path: Path, project_type: str):
    cfg = {"project_name": "integration-test", "project_type": project_type}
    path.write_text(json.dumps(cfg), encoding="utf8")


def test_generate_template(tmp_path: Path):
    # ensure a clean registry and register repo generators for this test
    registry.clear_registry()
    auto_register.auto_register_generators(search_paths=[Path("src/lib/generators")])

    cfg_path = tmp_path / "cfg.json"
    _write_config(cfg_path, "template")
    out_dir = tmp_path / "out"

    # import of src.cli triggers auto-registration
    rc = cli.generate.main(["--config", str(cfg_path), "--out", str(out_dir)])
    assert rc == 0
    assert (out_dir / "template.txt").exists()


def test_generate_vendor_example(tmp_path: Path):
    # ensure a clean registry and register repo generators for this test
    registry.clear_registry()
    auto_register.auto_register_generators(search_paths=[Path("src/lib/generators")])

    cfg_path = tmp_path / "cfg.json"
    _write_config(cfg_path, "vendor:example")
    out_dir = tmp_path / "out"

    rc = cli.generate.main(["--config", str(cfg_path), "--out", str(out_dir)])
    assert rc == 0
    assert (out_dir / "vendor.txt").exists()
