#!/usr/bin/env python3
"""
Root Schematic Generator for LED Touch Grid

Scaffold for Archon Task P3_T8:
- Integrate all child sheets (power, MCU, touch, LED, I/O) into hierarchical design
- Connect hierarchical pins between sheets for power, data, and control signals
- Generate complete KiCad project file (.kicad_pro) with proper sheet references
- Write integration tests for complete schematic generation workflow

TODOs:
- Import and instantiate all child sheet generators
- Add each sheet as a child to the root schematic
- Connect hierarchical pins between sheets (power, SPI, I2C, etc.)
- Generate and export the root schematic and project files
- Add integration validation and test hooks

Follows conventions from other sheet generators (see power_sheet.py, mcu_sheet.py, led_sheet.py, io_sheet.py).
"""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve()
while not (project_root / "tools").exists() and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

from hardware.projects.led_touch_grid.gen.io_sheet import IOSchematicBuilder
from hardware.projects.led_touch_grid.gen.led_sheet import LEDSheetBuilder
from hardware.projects.led_touch_grid.gen.mcu_sheet import generate_mcu_sheet

# Import child sheet generators
from hardware.projects.led_touch_grid.gen.power_sheet import PowerSchematicBuilder
from hardware.projects.led_touch_grid.gen.touch_sheet import TouchSchematicBuilder
from tools.kicad_helpers import (
    HierarchicalSchematic,
)


class RootSchematicBuilder:
    """
    Scaffold for root schematic generator.

    Responsibilities:
      - Instantiate and integrate all child sheets
      - Connect hierarchical pins between sheets
      - Export root schematic and project files
      - Provide integration validation hooks
    """

    def __init__(self, project_name: str = "led_touch_grid"):
        self.project_name = project_name
        self.hier = HierarchicalSchematic(title=f"{project_name}_root")
        self._built = False

    def _add_child_sheets(self):
        """Instantiate and add all child sheets."""
        # Generate each child sheet and add to root
        self.power_sheet = PowerSchematicBuilder(self.project_name).build()
        self.mcu_sheet = generate_mcu_sheet(self.project_name)
        self.touch_sheet = TouchSchematicBuilder(self.project_name).build()
        self.led_sheet = LEDSheetBuilder(self.project_name).build()
        self.io_sheet = IOSchematicBuilder(self.project_name).build()

        # Add sheets to root hierarchical schematic
        self.hier.add_sheet(self.power_sheet.sheets["power"])
        self.hier.add_sheet(self.mcu_sheet.sheets["mcu"])
        self.hier.add_sheet(self.touch_sheet.sheets["touch"])
        self.hier.add_sheet(self.led_sheet.sheets["led"])
        self.hier.add_sheet(self.io_sheet.sheets["io"])

    def _connect_hierarchical_pins(self) -> None:
        """Connect hierarchical pins between sheets for power, data, and control."""

        # Power connections - use correct pin names for each sheet
        self.hier.connect_hier_pins("power", "3.3V_OUT", "mcu", "3.3V_IN")
        self.hier.connect_hier_pins("power", "3.3V_OUT", "touch", "3.3V_IN")
        self.hier.connect_hier_pins("power", "5V_OUT", "led", "5V_IN")
        self.hier.connect_hier_pins("power", "GND", "mcu", "GND")
        self.hier.connect_hier_pins("power", "GND", "touch", "GND")
        self.hier.connect_hier_pins("power", "GND", "led", "GND_IN")  # LED sheet uses GND_IN
        self.hier.connect_hier_pins("power", "GND", "io", "GND")

        # Data/control connections
        self.hier.connect_hier_pins("mcu", "TOUCH_GPIO_BUS", "touch", "TOUCH_GRID_BUS")
        # Connect I2C bus
        self.hier.connect_hier_pins("mcu", "I2C_SDA", "io", "I2C_SDA")
        self.hier.connect_hier_pins("mcu", "I2C_SCL", "io", "I2C_SCL")
        # Add backup connection using legacy pin names
        self.hier.connect_hier_pins("io", "I2C_SDA", "mcu", "I2C_SDA")
        self.hier.connect_hier_pins("io", "I2C_SCL", "mcu", "I2C_SCL")
        self.hier.connect_hier_pins("io", "RESET", "mcu", "RESET")
        self.hier.connect_hier_pins("io", "3.3V_IN", "mcu", "3.3V_IN")
        # Remove 5V_IN connection to MCU since MCU doesn't have 5V_IN pin
        self.hier.connect_hier_pins("io", "GND", "mcu", "GND")

        # Connect SPI interface - MCU has LED_SPI_BUS, LED has DATA_IN/CLOCK_IN
        self.hier.connect_hier_pins("mcu", "LED_SPI_BUS", "led", "DATA_IN")

    def build(self) -> HierarchicalSchematic:
        if self._built:
            return self.hier

        self._add_child_sheets()
        self._connect_hierarchical_pins()

        out_dir = Path("out") / self.project_name / "root"
        out_dir.mkdir(parents=True, exist_ok=True)
        self.hier.write(out_dir=str(out_dir))

        self._built = True
        return self.hier


def generate_root_schematic(project_name: str = "led_touch_grid") -> HierarchicalSchematic:
    builder = RootSchematicBuilder(project_name=project_name)
    hier = builder.build()
    try:
        hier.run_full_erc()
        print("Root schematic scaffold generated; ERC baseline passed.")
    except ValueError as e:
        print(f"ERC (scaffold) reported issues (non-fatal):\n{e}")
    return hier


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", nargs="?", default="led_touch_grid")
    args = parser.parse_args()
    generate_root_schematic(args.project_name)
