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

from __future__ import annotations

import sys
from pathlib import Path

project_root = Path(__file__).resolve()
while not (project_root / "tools").exists() and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

import sys
from pathlib import Pathfrom tools.kicad_helpers import (
    HierarchicalSchematic,
)

# Import child sheet generators
from hardware.projects.led_touch_grid.gen.power_sheet import PowerSheetBuilder
from hardware.projects.led_touch_grid.gen.mcu_sheet import MCUSheetBuilder
from hardware.projects.led_touch_grid.gen.touch_sheet import TouchSheetBuilder
from hardware.projects.led_touch_grid.gen.led_sheet import LEDSheetBuilder
from hardware.projects.led_touch_grid.gen.io_sheet import IOSheetBuilder


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
        self.power = PowerSheetBuilder().build()
        self.mcu = MCUSheetBuilder().build()
        self.touch = TouchSheetBuilder().build()
        self.led = LEDSheetBuilder().build()
        self.io = IOSheetBuilder().build()

        self.hier.add_sheet(self.power.sheets["power"])
        self.hier.add_sheet(self.mcu.sheets["mcu"])
        self.hier.add_sheet(self.touch.sheets["touch"])
        self.hier.add_sheet(self.led.sheets["led"])
        self.hier.add_sheet(self.io.sheets["io"])

    def _connect_hierarchical_pins(self):
        """Connect hierarchical pins between sheets for power, data, and control."""

        # Power connections
        self.hier.connect_hier_pins("power", "3.3V_OUT", "mcu", "3.3V_IN")
        self.hier.connect_hier_pins("power", "3.3V_OUT", "touch", "3.3V_IN")
        self.hier.connect_hier_pins("power", "5V_OUT", "led", "5V_IN")
        self.hier.connect_hier_pins("power", "GND", "mcu", "GND")
        self.hier.connect_hier_pins("power", "GND", "touch", "GND")
        self.hier.connect_hier_pins("power", "GND", "led", "GND")
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
        self.hier.connect_hier_pins("io", "5V_IN", "mcu", "5V_IN")
        self.hier.connect_hier_pins("io", "GND", "mcu", "GND")

        # Connect SPI interface
        self.hier.connect_hier_pins("mcu", "MOSI0", "led", "SPI_DATA")
        self.hier.connect_hier_pins("mcu", "SCK", "led", "SPI_CLK")

    def build(self):
        if self._built:
            return self.hier

        self._add_child_sheets()
        self._connect_hierarchical_pins()

        out_dir = Path("out") / self.project_name / "root"
        out_dir.mkdir(parents=True, exist_ok=True)
        self.hier.write(out_dir=str(out_dir))

        self._built = True
        return self.hier


def generate_root_schematic(project_name: str = "led_touch_grid"):
    builder = RootSchematicBuilder(project_name=project_name)
    hier = builder.build()
    try:
        hier.run_full_erc()
        print("Root schematic scaffold generated; ERC baseline passed.")
    except ValueError as e:
        print(f"ERC (scaffold) reported issues (non-fatal):\n{e}")
    return hier


if __name__ == "__main__":
    generate_root_schematic()
