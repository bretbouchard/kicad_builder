#!/usr/bin/env python3
"""
Tests for the MCU sheet generator (gen/mcu_sheet.py).

Covers:
- Successful generation with expected symbols (dual RP2040), crystals,
  load capacitors, decoupling caps
- Presence of required hierarchical pins
- Decoupling validation failure (insufficient 100nF capacitors)

Usage:
  pytest hardware/projects/led_touch_grid/tests/test_mcu_sheet.py -q
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root for imports (tools/)
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from hardware.projects.led_touch_grid.gen.mcu_sheet import (  # noqa: E402
    generate_mcu_sheet,
    validate_mcu_power_decoupling,
)
from tools.kicad_helpers import (  # noqa: E402
    Schematic,
    Symbol,
)


def load_hierarchy(project_name: str):
    """Load the hierarchy JSON emitted by generate_mcu_sheet."""
    out_dir = Path("out") / project_name / "mcu"
    title = f"{project_name}_mcu_hier"
    hierarchy_path = out_dir / f"{title}_hierarchy.json"
    missing_msg = f"Hierarchy JSON missing: {hierarchy_path}"
    assert hierarchy_path.exists(), missing_msg
    return json.loads(hierarchy_path.read_text())


class TestMCUSheetGeneratorSuccess:
    def test_generate_mcu_sheet_success(self):
        project_name = "led_touch_grid_mcu_test"
        generate_mcu_sheet(project_name=project_name)

        hierarchy = load_hierarchy(project_name)
        sheets = hierarchy["sheets"]
        assert "mcu" in sheets, "MCU sheet missing in hierarchy export"

        mcu_symbols = sheets["mcu"]["symbols"]

        # Dual RP2040 symbols
        rp2040_refs = {
            s.get("ref")
            for s in mcu_symbols
            if ((s.get("value") and "RP2040" in s.get("value")) or s.get("name") == "RP2040")
        }
        rp2040_msg = f"Expected U1/U2 RP2040 symbols, found: {rp2040_refs}"
        assert {"U1", "U2"}.issubset(rp2040_refs), rp2040_msg

        # Crystal + load caps (Y1/Y2 + four 22pF caps)
        crystal_refs = {s.get("ref") for s in mcu_symbols if s.get("ref", "").startswith("Y")}
        assert {"Y1", "Y2"}.issubset(crystal_refs), "Missing crystals Y1/Y2"

        load_caps = [s for s in mcu_symbols if (s.get("value") or "").startswith("22pF")]
        assert len(load_caps) >= 4, f"Expected >=4 load capacitors, found {len(load_caps)}"

        # Decoupling capacitors (100nF) aggregate (>=8 for two MCUs)
        decoupling_caps = [s for s in mcu_symbols if "100nF" in (s.get("value") or "")]
        decap_msg = f"Expected >=8 total 100nF decoupling capacitors for two MCUs, found {len(decoupling_caps)}"
        assert len(decoupling_caps) >= 8, decap_msg

        # Hierarchical pins
        mcu_pins = sheets["mcu"]["hierarchical_pins"]
        pin_names = {p["name"] for p in mcu_pins}
        expected_pins = {
            "TOUCH_GPIO_BUS",
            "LED_SPI_BUS",
            "I2C_SDA",
            "I2C_SCL",
            "RESET",
            "ENABLE",
            "3.3V_IN",
            "GND",
        }
        pins_msg = f"Missing hierarchical pins: {expected_pins - pin_names}"
        assert expected_pins.issubset(pin_names), pins_msg

    def test_decoupling_validation_passes(self):
        """Validate rule on a schematic with one RP2040 and 4 decoupling caps."""
        sch = Schematic("single_rp2040_ok")
        sch.add_symbol(
            Symbol(
                lib="RP2040",
                name="RP2040",
                ref="U1",
                value="RP2040",
            )
        )
        for i in range(4):
            sch.add_symbol(Symbol(lib="Device", name="C", ref=f"C{i + 1}", value="100nF 50V"))
        # Should not raise
        validate_mcu_power_decoupling(sch)


class TestMCUSheetFailureCases:
    def test_decoupling_validation_failure(self):
        """Insufficient decoupling capacitors should raise ValueError."""
        sch = Schematic("single_rp2040_insufficient")
        sch.add_symbol(Symbol(lib="RP2040", name="RP2040", ref="U1", value="RP2040"))
        # Only 2 caps instead of required 4
        for ref in ("C1", "C2"):
            sch.add_symbol(Symbol(lib="Device", name="C", ref=ref, value="100nF 50V"))

        with pytest.raises(ValueError, match="Insufficient decoupling"):
            validate_mcu_power_decoupling(sch)


# Run directly
if __name__ == "__main__":
    pytest.main([__file__, "-q"])
