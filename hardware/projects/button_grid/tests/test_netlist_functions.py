from pathlib import Path
from typing import Any, Dict


def _load_netlist_ns() -> Dict[str, Any]:
    gen = Path(__file__).resolve().parents[1] / "gen" / "netlist.py"
    ns: Dict[str, Any] = {}
    exec(gen.read_text(), ns)
    return ns


def test_build_netlist_structure() -> None:
    ns = _load_netlist_ns()
    nl = ns["build_netlist"]()
    assert "nets" in nl and "components" in nl
    names = [n.get("name") for n in nl["nets"]]
    for expected in ("GND", "3V3", "5V", "SDA", "SCL", "LED_VCC"):
        assert expected in names
    refs = [c.get("ref") for c in nl["components"]]
    assert "U1" in refs and "C1" in refs and "J1" in refs


def test_check_decoupling_pass_and_fail() -> None:
    ns = _load_netlist_ns()
    nl = ns["build_netlist"]()
    assert ns["check_decoupling"](nl)
    # remove decoupling caps to simulate missing caps
    nl2 = {
        "nets": nl["nets"],
        "components": [c for c in nl["components"] if c.get("ref") not in ("C1", "C3")],
    }
    assert not ns["check_decoupling"](nl2)


def test_check_i2c_pullups_pass_and_fail() -> None:
    ns = _load_netlist_ns()
    nl = ns["build_netlist"]()
    assert ns["check_i2c_pullups"](nl)
    nl2 = {
        "nets": nl["nets"],
        "components": [c for c in nl["components"] if c.get("ref") != "R_PU_1"],
    }
    assert not ns["check_i2c_pullups"](nl2)


def test_write_outputs_creates_files(tmp_path: Path, monkeypatch: Any) -> None:
    ns = _load_netlist_ns()
    nl = ns["build_netlist"]()
    monkeypatch.chdir(tmp_path)
    ns["write_outputs"](nl)
    assert (tmp_path / "out" / "button_grid.net.json").exists()
    assert (tmp_path / "out" / "button_grid.net").exists()
