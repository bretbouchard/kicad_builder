#!/usr/bin/env python3
"""
ERC Validation Suite for LED Touch Grid

Implements and tests custom ERC rules for the LED Touch Grid project.

- Power decoupling validation for RP2040 and LED power pins
- IC pull-up resistor validation for inter-tile communication
- Hierarchical pin connection validation between sheets
- Integration-level ERC validation for the complete schematic

See: tools/kicad_helpers.py for validation logic.

"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from hardware.projects.led_touch_grid.gen.power_sheet import PowerSheetBuilder
from hardware.projects.led_touch_grid.gen.mcu_sheet import MCUSheetBuilder
from hardware.projects.led_touch_grid.gen.led_sheet import LEDSheetBuilder
from tools.kicad_helpers import HierarchicalSchematic, Symbol, Schematic, Sheet


def test_power_decoupling_validation_pass():
    """Test that correct decoupling passes ERC."""
    # Build a valid power + MCU + LED sheet
    power = PowerSheetBuilder().build()
    mcu = MCUSheetBuilder().build()
    led = LEDSheetBuilder().build()
    # Compose a root schematic and add all sheets
    hier = HierarchicalSchematic("test_power_decoupling_pass")
    hier.add_sheet(power.sheets["power"])
    hier.add_sheet(mcu.sheets["mcu"])
    hier.add_sheet(led.sheets["led"])
    # Should not raise
    hier.validate_power_decoupling()


def test_power_decoupling_validation_fail_missing_mcu_cap():
    """Test that missing MCU decoupling cap fails ERC."""
    power = PowerSheetBuilder().build()
    mcu = MCUSheetBuilder().build()
    hier = HierarchicalSchematic("test_power_decoupling_fail_mcu")
    hier.add_sheet(power.sheets["power"])
    hier.add_sheet(mcu.sheets["mcu"])
    # Remove all decoupling caps from all sheets (root and children)
    for sheet in [hier] + [s.schematic for s in hier.sheets.values()]:
        sheet.symbols = [
            s for s in sheet.symbols if not (s.lib == "Device" and s.name == "C" and "100nF" in (s.value or ""))
        ]
    # Should raise
    with pytest.raises(ValueError) as excinfo:
        hier.validate_power_decoupling()
    assert "Missing 100nF decoupling capacitor" in str(excinfo.value)


def test_power_decoupling_validation_fail_missing_led_bulk():
    """Test that missing LED bulk cap fails ERC."""
    power = PowerSheetBuilder().build()
    led = LEDSheetBuilder().build()
    hier = HierarchicalSchematic("test_power_decoupling_fail_led")
    hier.add_sheet(power.sheets["power"])
    hier.add_sheet(led.sheets["led"])
    # Remove all bulk caps from all sheets (root and children)
    for sheet in [hier] + [s.schematic for s in hier.sheets.values()]:
        sheet.symbols = [
            s
            for s in sheet.symbols
            if not (
                s.lib == "Device"
                and s.name == "C"
                and any(
                    tag in (s.value or "")
                    for tag in ("470uF", "1000uF", "220uF", "220µF", "47uF", "47µF", "1000µF", "470µF", "220µF")
                )
            )
        ]
    # Should raise
    with pytest.raises(ValueError) as excinfo:
        hier.validate_power_decoupling()
    assert "Missing bulk capacitor" in str(excinfo.value)


def test_i2c_pullup_validation_pass():
    """Test that correct I2C pull-up configuration passes ERC."""
    sch = Schematic("i2c_pullup_pass")
    # Add I2C nets
    sch.add_net("I2C1_SDA", ["U1.1", "R1.1"])
    sch.add_net("I2C1_SCL", ["U1.2", "R2.1"])
    # Add pull-up resistors (3.3kΩ)
    sch.add_symbol(Symbol(lib="Device", name="R", ref="R1", value="3.3k", fields={"Net": "I2C1_SDA"}))
    sch.add_symbol(Symbol(lib="Device", name="R", ref="R2", value="3.3k", fields={"Net": "I2C1_SCL"}))
    hier = HierarchicalSchematic("i2c_pullup_pass")
    hier.add_sheet(Sheet(name="main", schematic=sch))
    # Should not raise
    hier.validate_i2c_pullups()


def test_i2c_pullup_validation_fail_missing():
    """Test that missing I2C pull-up resistors fails ERC."""
    sch = Schematic("i2c_pullup_fail_missing")
    sch.add_net("I2C1_SDA", ["U1.1"])
    sch.add_net("I2C1_SCL", ["U1.2"])
    hier = HierarchicalSchematic("i2c_pullup_fail_missing")
    hier.add_sheet(Sheet(name="main", schematic=sch))
    with pytest.raises(ValueError) as excinfo:
        hier.validate_i2c_pullups()
    assert "Missing pull-up resistors" in str(excinfo.value)


def test_i2c_pullup_validation_fail_multiple():
    """Test that multiple pull-up sets on the same I2C net fails ERC."""
    sch = Schematic("i2c_pullup_fail_multiple")
    sch.add_net("I2C1_SDA", ["U1.1", "R1.1", "R3.1"])
    sch.add_symbol(Symbol(lib="Device", name="R", ref="R1", value="3.3k", fields={"Net": "I2C1_SDA"}))
    sch.add_symbol(Symbol(lib="Device", name="R", ref="R2", value="3.3k", fields={"Net": "I2C1_SDA"}))
    sch.add_symbol(Symbol(lib="Device", name="R", ref="R3", value="3.3k", fields={"Net": "I2C1_SDA"}))
    hier = HierarchicalSchematic("i2c_pullup_fail_multiple")
    hier.add_sheet(Sheet(name="main", schematic=sch))
    with pytest.raises(ValueError) as excinfo:
        hier.validate_i2c_pullups()
    assert "Multiple pull-up sets" in str(excinfo.value)


def test_i2c_pullup_validation_fail_value():
    """Test that invalid pull-up resistor values fail ERC."""
    sch = Schematic("i2c_pullup_fail_value")
    sch.add_net("I2C1_SDA", ["U1.1", "R1.1"])
    sch.add_symbol(Symbol(lib="Device", name="R", ref="R1", value="100", fields={"Net": "I2C1_SDA"}))  # 100Ω, too low
    hier = HierarchicalSchematic("i2c_pullup_fail_value")
    hier.add_sheet(Sheet(name="main", schematic=sch))
    with pytest.raises(ValueError) as excinfo:
        hier.validate_i2c_pullups()
    assert "Invalid pull-up value" in str(excinfo.value)
