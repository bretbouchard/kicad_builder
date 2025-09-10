from __future__ import annotations

import json

from src.lib.generator_registry import clear_registry, register


def test_cli_generate_simple(tmp_path, monkeypatch):
    # register simple generator lazily
    from src.lib.generators.simple_generator import SimpleGenerator

    clear_registry()
    register("simple", SimpleGenerator())

    cfg = {"project_name": "demo", "project_type": "simple", "metadata": {}}
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(json.dumps(cfg), encoding="utf-8")

    out_dir = tmp_path / "out"

    # call the CLI main directly
    from src.cli.generate import main as gen_main

    rc = gen_main(["--config", str(cfg_file), "--out", str(out_dir)])
    assert rc == 0
    generated = out_dir / "simple.txt"
    assert generated.exists()
    assert "project: demo" in generated.read_text()
