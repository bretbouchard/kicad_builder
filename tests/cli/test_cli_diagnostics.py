import importlib
import json


def test_cli_writes_diagnostics_on_autoregister_failure(tmp_path, monkeypatch):
    # Create a minimal config file
    cfg = tmp_path / "cfg.json"
    cfg.write_text('{"project_name": "t", "project_type": "unknown"}', encoding="utf8")

    # Place an empty module in the output search path to force auto-register failure
    gen_dir = tmp_path / "gens"
    gen_dir.mkdir()
    (gen_dir / "empty.py").write_text("# empty\n", encoding="utf8")

    # Monkeypatch the auto_register search path by pointing its discover to our tmp gens

    # Run CLI generate.main and expect exit code 4
    cli = importlib.import_module("src.cli.generate")

    rc = cli.main(["--config", str(cfg), "--out", str(tmp_path)])
    assert rc == 4

    diag = tmp_path / "auto_register_diagnostics.json"
    assert diag.exists()
    data = json.loads(diag.read_text(encoding="utf8"))
    assert isinstance(data, list)
