import json
from pathlib import Path


from tools.kicad_helpers import (
    Schematic,
    HierarchicalSchematic,
    Sheet,
    Symbol,
)


def test_hierarchical_basic(tmp_path: Path) -> None:
    out: Path = tmp_path / "out"
    root = HierarchicalSchematic(title="root_test")

    # create a power sheet
    p_sch = Schematic(title="power")
    p_sch.add_symbol(Symbol(lib="Device", name="C", ref="C1", at=(1, 1)))
    power_sheet = Sheet(name="power", schematic=p_sch)
    power_sheet.add_hier_pin("V5", direction="out")

    # create an mcu sheet that consumes power
    m_sch = Schematic(title="mcu")
    m_sch.add_symbol(Symbol(lib="MCU", name="RP2040", ref="U1", at=(2, 2)))
    mcu_sheet = Sheet(name="mcu", schematic=m_sch)
    mcu_sheet.add_hier_pin("V5", direction="in")

    root.add_sheet(power_sheet)
    root.add_sheet(mcu_sheet)
    root.connect_hier_pins(
        parent_sheet="power",
        parent_pin="V5",
        child_sheet="mcu",
        child_pin="V5",
    )

    root.write(out_dir=str(out))

    # verify hierarchy file exists and has expected keys
    hier = out / "root_test_hierarchy.json"
    assert hier.exists()
    data = json.loads(hier.read_text())
    assert "sheets" in data
    assert "connections" in data
    assert ("power.V5", "mcu.V5") in [tuple(x) for x in data["connections"]]


def test_hierarchy_direction_validation(tmp_path: Path) -> None:
    out: Path = tmp_path / "out"
    root = HierarchicalSchematic(title="root_dir_test")

    p_sch = Schematic(title="power2")
    p_sch.add_symbol(Symbol(lib="Device", name="C", ref="C2", at=(1, 1)))
    power_sheet = Sheet(name="power2", schematic=p_sch)
    # intentionally incorrect: parent pin is 'in' (cannot drive)
    power_sheet.add_hier_pin("V5", direction="in")

    m_sch = Schematic(title="mcu2")
    m_sch.add_symbol(Symbol(lib="MCU", name="RP2040", ref="U2", at=(2, 2)))
    mcu_sheet = Sheet(name="mcu2", schematic=m_sch)
    mcu_sheet.add_hier_pin("V5", direction="in")

    root.add_sheet(power_sheet)
    root.add_sheet(mcu_sheet)
    root.connect_hier_pins(
        parent_sheet="power2",
        parent_pin="V5",
        child_sheet="mcu2",
        child_pin="V5",
    )

    # write() should raise due to invalid parent pin direction
    import pytest

    with pytest.raises(ValueError):
        root.write(out_dir=str(out))
