import importlib
import json


def test_autoregister_error_format_and_failures():
    auto_register = importlib.import_module("src.services.auto_register")
    # Construct an error with sample failures
    failures = [
        {"path": "a.py", "type": "import", "message": "nope"},
        {"path": "b.py", "type": "no_entrypoint", "message": "missing"},
    ]
    err = auto_register.AutoRegisterError(failures)
    assert hasattr(err, "failures")
    assert err.failures == failures
    # Ensure message contains at least one path
    assert "a.py" in str(err)


def test_diagnostics_file_written(tmp_path):
    # Create a module that will trigger a no_entrypoint failure
    m = tmp_path / "nobody.py"
    m.write_text("# empty module\nX=1\n", encoding="utf8")

    auto_register = importlib.import_module("src.services.auto_register")
    diagnostics = tmp_path / "diag.json"

    try:
        auto_register.auto_register_generators(search_paths=[tmp_path], diagnostics_path=diagnostics)
    except auto_register.AutoRegisterError:
        # diagnostics file should be created
        assert diagnostics.exists()
        data = json.loads(diagnostics.read_text(encoding="utf8"))
        assert isinstance(data, list)
        assert any(d.get("type") == "no_entrypoint" for d in data)
    else:
        assert False, "auto_register should have raised AutoRegisterError"
