"""Tests for hierarchical schematic generation functionality."""

import os
import sys
import tempfile

import pytest

# Add the tools directory to the path so we can import kicad_helpers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from kicad_helpers import (
    HierarchicalPin,
    HierarchicalSchematic,
    Schematic,
    Sheet,
    Symbol,
)


class TestHierarchicalPin:
    """Test HierarchicalPin data class and functionality."""

    def test_hierarchical_pin_creation(self):
        """Test creating a hierarchical pin with default values."""
        pin = HierarchicalPin(name="VCC", direction="out", sheet_ref="power")
        assert pin.name == "VCC"
        assert pin.direction == "out"
        assert pin.sheet_ref is None

    def test_hierarchical_pin_with_sheet_ref(self):
        """Test creating a hierarchical pin with sheet reference."""
        pin = HierarchicalPin(name="SDA", direction="in", sheet_ref="i2c")
        assert pin.name == "SDA"
        assert pin.direction == "in"
        assert pin.sheet_ref == "i2c"

    def test_invalid_direction_raises_error(self):
        """Test that invalid pin directions raise appropriate errors."""
        with pytest.raises(ValueError, match="Invalid direction"):
            HierarchicalPin(name="TEST", direction="invalid")


class TestSheet:
    """Test Sheet class and functionality."""

    def test_sheet_creation(self):
        """Test creating a sheet with default values."""
        sheet = Sheet(name="power")
        assert sheet.name == "power"
        assert sheet.schematic.title == "test_sheet"
        assert len(sheet.hierarchical_pins) == 0

    def test_add_hierarchical_pin(self):
        """Test adding hierarchical pins to a sheet."""
        sch = Schematic("test_sheet")
        sheet = Sheet(name="power")

        sheet.add_hier_pin("VCC", direction="out")
        sheet.add_hier_pin("GND", direction="in")

        assert len(sheet.hierarchical_pins) == 2
        assert sheet.hierarchical_pins[0].name == "VCC"
        assert sheet.hierarchical_pins[0].direction == "out"
        assert sheet.hierarchical_pins[1].name == "GND"
        assert sheet.hierarchical_pins[1].direction == "in"

    def test_duplicate_sheet_name_raises_error(self):
        """Test that adding a sheet with duplicate name raises error."""
        sch = Schematic("test")
        sheet1 = Sheet(name="power", schematic=sch)
        sheet2 = Sheet(name="power", schematic=sch)

        hier_sch = HierarchicalSchematic("test_hier")
        hier_sch.add_sheet(sheet1)

        with pytest.raises(ValueError, match="Sheet with name 'power' already exists"):
            hier_sch.add_sheet(sheet2)


class TestHierarchicalSchematic:
    """Test HierarchicalSchematic class functionality."""

    def test_hierarchical_schematic_creation(self):
        """Test creating a hierarchical schematic."""
        hier_sch = HierarchicalSchematic("test_hierarchy")
        assert hier_sch.title == "test_hierarchy"
        assert len(hier_sch.sheets) == 0
        assert len(hier_sch.hier_connections) == 0

    def test_add_sheet(self):
        """Test adding sheets to hierarchical schematic."""
        hier_sch = HierarchicalSchematic("test_hierarchy")
        sch = Schematic("power_sheet")
        sheet = Sheet(name="power")

        hier_sch.add_sheet(sheet)
        assert "power" in hier_sch.sheets
        assert hier_sch.sheets["power"] == sheet

    def test_connect_hier_pins(self):
        """Test connecting hierarchical pins between sheets."""
        hier_sch = HierarchicalSchematic("test_hierarchy")

        # Create parent and child sheets
        parent_sch = Schematic("parent")
        child_sch = Schematic("child")

        parent_sheet = Sheet(name="parent", schematic=parent_sch)
        child_sheet = Sheet(name="child", schematic=child_sch)

        # Add hierarchical pins
        parent_sheet.add_hier_pin("VCC_OUT", direction="out")
        child_sheet.add_hier_pin("VCC_IN", direction="in")

        hier_sch.add_sheet(parent_sheet)
        hier_sch.add_sheet(child_sheet)

        # Connect pins
        hier_sch.connect_hier_pins("parent", "VCC_OUT", "child", "VCC_IN")

        assert len(hier_sch.hier_connections) == 1
        connection = hier_sch.hier_connections[0]
        assert connection == ("parent.VCC_OUT", "child.VCC_IN")

    def test_find_pin(self):
        """Test finding hierarchical pins in sheets."""
        hier_sch = HierarchicalSchematic("test")
        sch = Schematic("test_sheet")
        sheet = Sheet(name="test", schematic=sch)
        sheet.add_hier_pin("VCC", direction="out")

        hier_sch.add_sheet(sheet)

        # Test finding existing pin
        pin = hier_sch._find_pin("test", "VCC")
        assert pin is not None
        assert pin.name == "VCC"
        assert pin.direction == "out"

        # Test finding non-existing pin
        pin = hier_sch._find_pin("test", "NONEXISTENT")
        assert pin is None

        # Test finding non-existing sheet
        pin = hier_sch._find_pin("nonexistent", "VCC")
        assert pin is None

    def test_validate_hierarchy_valid_connections(self):
        """Test validation of valid hierarchical connections."""
        hier_sch = HierarchicalSchematic("test")

        # Create sheets with compatible pins
        parent_sch = Schematic("parent")
        child_sch = Schematic("child")

        parent_sheet = Sheet(name="parent", schematic=parent_sch)
        child_sheet = Sheet(name="child", schematic=child_sch)

        parent_sheet.add_hier_pin("DATA_OUT", direction="out")
        child_sheet.add_hier_pin("DATA_IN", direction="in")

        hier_sch.add_sheet(parent_sheet)
        hier_sch.add_sheet(child_sheet)
        hier_sch.connect_hier_pins("parent", "DATA_OUT", "child", "DATA_IN")

        # Should not raise any errors
        hier_sch.validate_hierarchy()

    def test_validate_hierarchy_invalid_format(self):
        """Test validation catches invalid connection format."""
        hier_sch = HierarchicalSchematic("test")
        hier_sch.hier_connections = [("invalid_format", "also_invalid")]

        with pytest.raises(ValueError, match="Invalid hierarchical connection format"):
            hier_sch.validate_hierarchy()

    def test_validate_hierarchy_missing_parent_pin(self):
        """Test validation catches missing parent pin."""
        hier_sch = HierarchicalSchematic("test")

        child_sch = Schematic("child")
        child_sheet = Sheet(name="child", schematic=child_sch)
        child_sheet.add_hier_pin("DATA_IN", direction="in")

        hier_sch.add_sheet(child_sheet)
        hier_sch.connect_hier_pins("parent", "NONEXISTENT", "child", "DATA_IN")

        with pytest.raises(ValueError, match="Parent pin 'NONEXISTENT' not found"):
            hier_sch.validate_hierarchy()

    def test_validate_hierarchy_missing_child_pin(self):
        """Test validation catches missing child pin."""
        hier_sch = HierarchicalSchematic("test")

        parent_sch = Schematic("parent")
        parent_sheet = Sheet(name="parent", schematic=parent_sch)
        parent_sheet.add_hier_pin("DATA_OUT", direction="out")

        hier_sch.add_sheet(parent_sheet)
        hier_sch.connect_hier_pins("parent", "DATA_OUT", "child", "NONEXISTENT")

        with pytest.raises(ValueError, match="Child pin 'NONEXISTENT' not found"):
            hier_sch.validate_hierarchy()

    def test_validate_hierarchy_direction_mismatch(self):
        """Test validation catches direction mismatches."""
        hier_sch = HierarchicalSchematic("test")

        parent_sch = Schematic("parent")
        child_sch = Schematic("child")

        parent_sheet = Sheet(name="parent", schematic=parent_sch)
        child_sheet = Sheet(name="child", schematic=child_sch)

        # Incompatible directions: parent cannot receive, child cannot send
        parent_sheet.add_hier_pin("DATA_IN", direction="in")
        child_sheet.add_hier_pin("DATA_OUT", direction="out")

        hier_sch.add_sheet(parent_sheet)
        hier_sch.add_sheet(child_sheet)
        hier_sch.connect_hier_pins("parent", "DATA_IN", "child", "DATA_OUT")

        with pytest.raises(ValueError, match="cannot drive"):
            hier_sch.validate_hierarchy()

    def test_summary_includes_hierarchy_info(self):
        """Test that summary includes hierarchical information."""
        hier_sch = HierarchicalSchematic("test")

        # Add a sheet
        sch = Schematic("power_sheet")
        sheet = Sheet(name="power", schematic=sch)
        sheet.add_hier_pin("VCC", direction="out")

        hier_sch.add_sheet(sheet)

        summary = hier_sch.summary()
        assert "sheets" in summary
        assert "power" in summary["sheets"]
        assert summary["sheets"]["power"]["title"] == "power_sheet"
        assert len(summary["sheets"]["power"]["pins"]) == 1
        assert summary["sheets"]["power"]["pins"][0]["name"] == "VCC"

    def test_write_generates_output_files(self):
        """Test that writing hierarchical schematic generates expected files."""
        hier_sch = HierarchicalSchematic("test_hierarchy")

        # Add a simple sheet
        sch = Schematic("power_sheet")
        sheet = Sheet(name="power", schematic=sch)
        sheet.add_hier_pin("VCC", direction="out")

        hier_sch.add_sheet(sheet)

        with tempfile.TemporaryDirectory() as temp_dir:
            hier_sch.write(out_dir=temp_dir)

            # Check that root schematic files were created
            assert os.path.exists(os.path.join(temp_dir, "test_hierarchy.sch.txt"))
            assert os.path.exists(os.path.join(temp_dir, "test_hierarchy.kicad_sch"))
            assert os.path.exists(os.path.join(temp_dir, "test_hierarchy_summary.json"))

            # Check that hierarchy file was created
            assert os.path.exists(os.path.join(temp_dir, "test_hierarchy_hierarchy.json"))

            # Check that sheet files were created
            assert os.path.exists(os.path.join(temp_dir, "sheets", "power_sheet.sch.txt"))
            assert os.path.exists(os.path.join(temp_dir, "sheets", "power_sheet.kicad_sch"))


def test_hierarchical_schematic_integration():
    """Integration test for complete hierarchical schematic workflow."""
    hier_sch = HierarchicalSchematic("led_touch_grid")

    # Create power sheet
    power_sch = Schematic("power_distribution")
    power_sheet = Sheet(name="power", schematic=power_sch)
    power_sheet.add_hier_pin("5V_IN", direction="in")
    power_sheet.add_hier_pin("3V3_OUT", direction="out")
    power_sheet.add_hier_pin("GND", direction="inout")

    # Create MCU sheet
    mcu_sch = Schematic("mcu_control")
    mcu_sheet = Sheet(name="mcu", schematic=mcu_sch)
    mcu_sheet.add_hier_pin("3V3_IN", direction="in")
    mcu_sheet.add_hier_pin("GND_IN", direction="in")
    mcu_sheet.add_hier_pin("TOUCH_DATA", direction="out")

    # Add sheets to hierarchical schematic
    hier_sch.add_sheet(power_sheet)
    hier_sch.add_sheet(mcu_sheet)

    # Connect hierarchical pins
    hier_sch.connect_hier_pins("power", "3V3_OUT", "mcu", "3V3_IN")
    hier_sch.connect_hier_pins("power", "GND", "mcu", "GND_IN")

    # Add some symbols to the schematics
    power_sch.add_symbol(Symbol(lib="Device", name="C", ref="C1", at=(10, 20)))
    mcu_sch.add_symbol(Symbol(lib="MCU", name="RP2040", ref="U1", at=(30, 40)))

    # Add a wire
    mcu_sch.add_wire("U1.1", "U1.2")

    # Validate and write
    with tempfile.TemporaryDirectory() as temp_dir:
        hier_sch.write(out_dir=temp_dir)

        # Check all expected files exist
        assert os.path.exists(os.path.join(temp_dir, "led_touch_grid.sch.txt"))
        assert os.path.exists(os.path.join(temp_dir, "led_touch_grid.kicad_sch"))
        assert os.path.exists(os.path.join(temp_dir, "led_touch_grid_hierarchy.json"))

        # Check hierarchy JSON content
        import json

        with open(os.path.join(temp_dir, "led_touch_grid_hierarchy.json"), "r") as f:
            hier_data = json.load(f)

        assert "sheets" in hier_data
        assert "connections" in hier_data
        assert len(hier_data["connections"]) == 2


class TestPowerDecouplingValidation:
    """Tests for validate_power_decoupling in HierarchicalSchematic."""

    def test_missing_decoupling_cap_raises(self):
        hier_sch = HierarchicalSchematic("decouple_test")
        mcu_sheet = Sheet(name="mcu", schematic=Schematic("mcu"))
        mcu_sheet.add_hier_pin("3V3_IN", direction="in")
        hier_sch.add_sheet(mcu_sheet)

        # Add MCU symbol but no 100nF capacitor
        mcu_sheet.schematic.add_symbol(Symbol(lib="MCU", name="RP2040", ref="U1"))
        with pytest.raises(ValueError, match="Missing 100nF decoupling capacitor"):
            hier_sch.validate_power_decoupling()

    def test_with_decoupling_and_bulk_caps_passes(self):
        hier_sch = HierarchicalSchematic("decouple_ok")
        power_sheet = Sheet(name="power", schematic=Schematic("power"))
        power_sheet.add_hier_pin("3V3_OUT", direction="out")
        hier_sch.add_sheet(power_sheet)

        # Add MCU + LED + required capacitors
        power_sheet.schematic.add_symbol(Symbol(lib="MCU", name="RP2040", ref="U1"))
        power_sheet.schematic.add_symbol(Symbol(lib="LED", name="APA102", ref="D1"))
        power_sheet.schematic.add_symbol(Symbol(lib="Device", name="C", ref="C1", value="100nF"))
        power_sheet.schematic.add_symbol(Symbol(lib="Device", name="C", ref="C2", value="470uF"))
        hier_sch.validate_power_decoupling()  # should not raise


class TestI2CPullupValidation:
    """Tests for validate_i2c_pullups in HierarchicalSchematic."""

    def _base_i2c_schematic(self):
        hier_sch = HierarchicalSchematic("i2c_test")
        sheet = Sheet(name="mcu", schematic=Schematic("mcu"))
        hier_sch.add_sheet(sheet)
        return hier_sch, sheet

    def test_missing_pullups_raises(self):
        hier_sch, sheet = self._base_i2c_schematic()
        # Add an I2C net but no pullups
        sheet.schematic.add_net("I2C_SDA", ["U1.1"])
        with pytest.raises(ValueError, match="Missing pull-up resistors"):
            hier_sch.validate_i2c_pullups()

    def test_valid_pullups_pass(self):
        hier_sch, sheet = self._base_i2c_schematic()
        sheet.schematic.add_net("I2C_SDA", ["U1.1", "R1.1"])
        sheet.schematic.add_net("I2C_SCL", ["U1.2", "R2.1"])
        sheet.schematic.add_symbol(Symbol(lib="Device", name="R", ref="R1", value="4.7k", fields={"Net": "I2C_SDA"}))
        sheet.schematic.add_symbol(Symbol(lib="Device", name="R", ref="R2", value="10k", fields={"Net": "I2C_SCL"}))
        hier_sch.validate_i2c_pullups()

    def test_multiple_pullup_sets_raises(self):
        hier_sch, sheet = self._base_i2c_schematic()
        sheet.schematic.add_net("I2C_SDA", ["U1.1", "R1.1", "R3.1", "R4.1"])
        sheet.schematic.add_symbol(Symbol(lib="Device", name="R", ref="R1", value="4.7k", fields={"Net": "I2C_SDA"}))
        sheet.schematic.add_symbol(Symbol(lib="Device", name="R", ref="R3", value="4.7k", fields={"Net": "I2C_SDA"}))
        sheet.schematic.add_symbol(Symbol(lib="Device", name="R", ref="R4", value="4.7k", fields={"Net": "I2C_SDA"}))
        with pytest.raises(ValueError, match="Multiple pull-up sets"):
            hier_sch.validate_i2c_pullups()

    def test_invalid_pullup_value_raises(self):
        hier_sch, sheet = self._base_i2c_schematic()
        sheet.schematic.add_net("I2C_SCL", ["U1.2", "R1.1"])
        sheet.schematic.add_symbol(Symbol(lib="Device", name="R", ref="R1", value="0.5k", fields={"Net": "I2C_SCL"}))
        with pytest.raises(ValueError, match="Invalid pull-up value"):
            hier_sch.validate_i2c_pullups()
