from pathlib import Path


def test_skidl_import_available():
    """Ensure SKiDL is importable and reports a version string."""
    try:
        import skidl  # type: ignore
    except Exception as e:  # pragma: no cover - environment dependent
        raise AssertionError("SKiDL not available in test environment") from e

    assert getattr(skidl, "__version__", None)


def test_generator_runs_with_skidl():
    """Ensure the existing generator can run when SKiDL is available."""
    gen = Path(__file__).resolve().parents[1] / "gen" / "netlist.py"
    # run generator in-process by importing (it guards with if __name__)
    ns = {}
    exec(gen.read_text(), ns)
    # expect build_netlist exists
    assert "build_netlist" in ns
    nl = ns["build_netlist"]()
    assert isinstance(nl, dict)
    # If the generator exposes lightweight checks, run them too
    if "check_decoupling" in ns:
        assert ns["check_decoupling"](nl)
    if "check_i2c_pullups" in ns:
        assert ns["check_i2c_pullups"](nl)
