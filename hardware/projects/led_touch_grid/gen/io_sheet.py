#!/usr/bin/env python3
"""
I/O Connectivity Schematic Generator for LED Touch Grid

Scaffold for Archon Task P3_T7:
- Inter-tile and host connectivity
- Edge connectors for power, SPI, I2C signals
- USB-C host interface with proper signal routing
- Programming connectors (SWD)
- Status indicators (LEDs)
- Mechanical alignment features for tile interconnection

TODOs:
- Implement edge connector symbol instantiation and net mapping
- Add USB-C symbol, nets, and power/signal routing
- Add SWD header and net connections
- Add status indicator LEDs and drivers
- Add mechanical outline/markers (as symbol or annotation)
- Expose hierarchical pins for all relevant signals

Follows conventions from other sheet generators (see power_sheet.py, mcu_sheet.py, led_sheet.py).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

project_root = Path(__file__).resolve()
while not (project_root / "tools").exists() and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

from tools.kicad_helpers import (
    HierarchicalSchematic,
    Symbol,
)


@dataclass
class IOSchematicConfig:
    """Configurable parameters for I/O sheet generation."""

    edge_connector_type: str = "Edge_Conn_20"  # Placeholder
    usb_c_type: str = "USB_C_Receptacle"
    swd_header_type: str = "SWD_2x5"
    status_led_type: str = "LED_SMD"
    add_mechanical: bool = True


class IOSchematicBuilder:
    """
    Scaffold for I/O connectivity sheet generator.

    Responsibilities:
      - Instantiate edge connectors for power/SPI/I2C
      - Add USB-C host interface and route signals
      - Add SWD programming header
      - Add status indicator LEDs
      - Add mechanical alignment features
      - Expose hierarchical pins for all relevant signals
    """

    def __init__(
        self,
        project_name: str = "led_touch_grid",
        config: Optional[IOSchematicConfig] = None,
    ):
        self.project_name = project_name
        self.config = config or IOSchematicConfig()
        self.hier_schematic = HierarchicalSchematic(title=f"{project_name}_io_hier")
        self.io_sheet = self.hier_schematic.create_sheet("io")
        self.symbols: List[Symbol] = []
        self._built = False

    def _add_edge_connectors(self):
        """TODO: Instantiate edge connectors and connect power/SPI/I2C nets."""
        pass

    def _add_usb_c(self):
        """TODO: Add USB-C symbol and route power/data nets."""
        pass

    def _add_swd_header(self):
        """TODO: Add SWD programming header and connect to MCU."""
        pass

    def _add_status_indicators(self):
        """TODO: Add status indicator LEDs and drivers."""
        pass

    def _add_mechanical_features(self):
        """TODO: Add mechanical outline/markers as symbol or annotation."""
        pass

    def _expose_hierarchical_pins(self):
        """
        Expose hierarchical pins for all I/O signals.
        """
        pins = [
            ("5V_IN", "out"),
            ("3.3V_IN", "out"),
            ("GND", "inout"),
            ("SPI_MOSI", "inout"),
            ("SPI_MISO", "inout"),
            ("SPI_SCK", "inout"),
            ("I2C_SDA", "inout"),
            ("I2C_SCL", "inout"),
            ("USB_D_P", "inout"),
            ("USB_D_N", "inout"),
            ("SWDIO", "inout"),
            ("SWCLK", "inout"),
            ("STATUS_LED", "out"),
            ("RESET", "out"),
        ]

        for name, direction in pins:
            self.hier_schematic.add_hier_pin("io", name, direction)

    def build(self, for_root: bool = False):
        # Scaffold: call placeholder methods
        self._add_edge_connectors()
        self._add_usb_c()
        self._add_swd_header()
        self._add_status_indicators()
        self._add_mechanical_features()

        self._expose_hierarchical_pins()

        if for_root:

            class Result:
                sheets = {"io": self.io_sheet}

            return Result()
        else:
            out_dir = Path("out") / self.project_name / "io"
            out_dir.mkdir(parents=True, exist_ok=True)
            self.hier_schematic.write(out_dir=str(out_dir))
            return self.hier_schematic


def generate_io_sheet(project_name: str = "led_touch_grid") -> None:
    builder = IOSchematicBuilder(project_name=project_name)
    hier = builder.build(for_root=False)
    try:
        hier.run_full_erc()
        print("I/O sheet scaffold generated; ERC baseline passed.")
    except ValueError as e:
        print(f"ERC (scaffold) reported issues:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", nargs="?", default="led_touch_grid")
    args = parser.parse_args()
    generate_io_sheet(args.project_name)
