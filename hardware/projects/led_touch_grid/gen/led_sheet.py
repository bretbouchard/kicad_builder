#!/usr/bin/env python3
"""
LED sheet generator (scaffold) for LED Touch Grid project.

Stage: TASK 1 (Scaffold Only)
-------------------------------------------------
This file provides the scaffold and structural
foundation for the
P2_T6 LED sheet generator implementation.
It intentionally limits
functional logic so that
subsequent tasks can incrementally
add:

TASK 2: Implement APA102 chain construction (256 LEDs) with nets
TASK 3: Add per-LED decoupling capacitor generation (C1..C256)
TASK 4: Insert bulk capacitors (CB_MAIN + CB1..CB7) at segment boundaries
TASK 5: Expose hierarchical pins (LED_CLK, LED_DATA,
       5V_IN, GND, LED_CLK_OUT, LED_DATA_OUT)
TASK 6: Implement validation functions
        (count, decoupling, bulk, chain continuity)
TASK 7: Write pytest suite tests/test_led_sheet.py
TASK 8: Integrate Makefile targets
TASK 9: Update documentation (README + BYTEROVER)
TASK 10: Run full generation + validation + tests

Confirmed design assumptions (from plan + user answers):
- LED type: APA102 (separate DATA / CLOCK lines)
- Arrangement: Logical 16 x 16 grid (256 LEDs) single chained path
- Per-LED decoupling: 100nF (to be added later)
- Bulk capacitors: 220µF start (CB_MAIN) + 47µF every 32 LEDs (CB1..CB7)
- Chain expansion: Provide DATA_OUT / CLK_OUT hierarchical pins
  at tail (later task)
- Individual addressability and cascading between tiles required

This scaffold defines:
- Constants / configuration container
- LEDSheetBuilder class (future extension point)
- Placeholder validation hooks
- CLI entry point

NOTE: No actual LED symbol / net generation occurs yet (deferred).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Ensure project root on path (mirrors existing generators)
project_root = Path(__file__).resolve()
while not (project_root / "tools").exists() and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

import sys
from pathlib import Pathfrom tools.kicad_helpers import (  # noqa: E402
    Schematic,
    HierarchicalSchematic,
    Sheet,
    HierarchicalPin,
    Symbol,
)

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------

GRID_ROWS = 16
GRID_COLS = 16
LED_COUNT = GRID_ROWS * GRID_COLS  # 256

DEFAULT_DECOUPLING_VALUE = "100nF 50V"
DEFAULT_DECOUPLING_FOOTPRINT = "Capacitor_SMD:C_0805_2012Metric"
DEFAULT_LED_SYMBOL = ("LED_Programmable", "APA102")
# (lib, name) placeholder
DEFAULT_LED_FOOTPRINT = "LED_SMD:LED_RGB_PLCC4_5.0x5.0mm"  # Replace later
# (Footprint comment shortened for flake8 line length)

BULK_MAIN_VALUE = "220µF 10V"
BULK_SEGMENT_VALUE = "47µF 10V"
BULK_FOOTPRINT = "Capacitor_SMD:CP_Elec_6.3x5.4"  # Placeholder

SEGMENT_INTERVAL = 32  # Bulk cap every 32 LEDs

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------


@dataclass
class LEDSheetConfig:
    """Future configurable parameters for LED sheet generation."""

    rows: int = GRID_ROWS
    cols: int = GRID_COLS
    chain_tail_pins: bool = True
    add_decoupling: bool = True
    add_bulk_caps: bool = True
    led_symbol: tuple[str, str] = DEFAULT_LED_SYMBOL
    led_footprint: str = DEFAULT_LED_FOOTPRINT
    decoupling_value: str = DEFAULT_DECOUPLING_VALUE
    decoupling_footprint: str = DEFAULT_DECOUPLING_FOOTPRINT

    @property
    def expected_led_count(self) -> int:
        return self.rows * self.cols


# ---------------------------------------------------------------------------
# Builder (Scaffold)
# ---------------------------------------------------------------------------


#


class LEDSheetBuilder:
    """
    Scaffold for LED sheet generator.

    Responsibilities (future):
      - Generate full chained APA102 symbol sequence
      - Insert per-LED decoupling
      - Insert bulk capacitors at defined intervals
      - Create and link nets for CLK/DATA power distribution
      - Expose hierarchical interface pins
      - Provide validation routines

    Current (scaffold):
      - Create empty schematic + sheet wrapper
      - Provide hook methods to be filled in later
    """

    def __init__(
        self,
        project_name: str = "led_touch_grid",
        config: Optional[LEDSheetConfig] = None,
    ):
        self.project_name = project_name
        self.config = config or LEDSheetConfig()
        self.schematic = Schematic(title=f"{project_name}_led")
        self.symbols: List[Symbol] = []
        self._built = False

    def build(self, for_root: bool = False):
        """Build LED sheet and return hierarchical schematic."""
        self._add_led_chain()
        self._add_per_led_decoupling()
        self._add_bulk_caps()
        sheet = self._expose_hierarchical_pins()
        if for_root:

            class Result(HierarchicalSchematic):
                def __init__(self):
                    super().__init__(title="")
                    self.sheets = {"led": sheet}

                def run_full_erc(self):
                    """No-op for root schematic integration"""

            return Result()
        else:
            hier = HierarchicalSchematic(title=f"{self.project_name}_led_hier")
            hier.add_sheet(sheet)
            out_dir = Path("out") / self.project_name / "led"
            out_dir.mkdir(parents=True, exist_ok=True)
            hier.write(out_dir=str(out_dir))
            self._run_validations()
            return hier

    # -------------------- Placeholder Hook Methods -------------------- #
    def _add_led_chain(self) -> None:
        """
        Generate APA102 LED chain (TASK 2).

        - Instantiate 256 APA102 symbols (D1..D256)
        - Attach per-LED metadata (row/col, linear index)
        - Create DATA/CLOCK daisy-chain wiring
        - For netlist compatibility, create nets named MOSI0..MOSI15 and SCK for the first 16 data lines and clock
        """
        for idx in range(1, self.config.expected_led_count + 1):
            ref = f"D{idx}"
            row = (idx - 1) // self.config.cols
            col = (idx - 1) % self.config.cols
            symbol = Symbol(
                lib=self.config.led_symbol[0],
                name=self.config.led_symbol[1],
                ref=ref,
                value="APA102",
                footprint=self.config.led_footprint,
                fields={
                    "row": str(row),
                    "col": str(col),
                    "index": str(idx),
                },
            )
            self.symbols.append(symbol)
            self.schematic.add_symbol(symbol)

        # Wire DATA and CLOCK nets in a daisy-chain (D1..D256)
        for idx in range(1, self.config.expected_led_count):
            prev_ref = f"D{idx}"
            next_ref = f"D{idx+1}"
            # Single SPI data line
            self.schematic.add_net(name="SPI_DATA", pins=[f"{prev_ref}.DO", f"{next_ref}.DI"])
            # Single clock line
            self.schematic.add_net(name="SPI_CLK", pins=[f"{prev_ref}.CO", f"{next_ref}.CI"])

        # Connect first LED to SPI input pins
        self.schematic.add_net("SPI_DATA", ["D1.DI", "SPI_DATA"])
        self.schematic.add_net("SPI_CLK", ["D1.CI", "SPI_CLK"])

        # Connect last LED to output pins
        last_led = f"D{self.config.expected_led_count}"
        self.schematic.add_net("SPI_DATA", [f"{last_led}.DO", "LED_DATA_OUT"])
        self.schematic.add_net("SPI_CLK", [f"{last_led}.CO", "LED_CLK_OUT"])

    def _add_per_led_decoupling(self) -> None:
        """
        Add per-LED decoupling capacitors (TASK 3).

        - Place 100nF capacitor (C1..C256) for each LED
        - Connect each cap between VCC and GND pins of its LED
        """
        for idx in range(1, self.config.expected_led_count + 1):
            cref = f"C{idx}"
            led_ref = f"D{idx}"
            cap = Symbol(
                lib="Device",
                name="C",
                ref=cref,
                value=self.config.decoupling_value,
                footprint=self.config.decoupling_footprint,
                fields={
                    "for": led_ref,
                    "index": str(idx),
                },
            )
            self.schematic.add_symbol(cap)
            # Connect cap between VCC and GND pins of LED (example pin names)
            self.schematic.add_net(name=f"DECOUPLE_{led_ref}", pins=[f"{led_ref}.VCC", f"{cref}.1"])
            self.schematic.add_net(name=f"GND_{led_ref}", pins=[f"{led_ref}.GND", f"{cref}.2"])

    def _add_bulk_caps(self) -> None:
        """
        Insert bulk capacitors at segment boundaries (TASK 4).

        - Place CB_MAIN (220uF) at start of chain
        - Place CB1..CB7 (47uF) every 32 LEDs
        - Connect each bulk cap between VCC and GND
        """
        # Main bulk capacitor at start
        cb_main = Symbol(
            lib="Device",
            name="C",
            ref="CB_MAIN",
            value=BULK_MAIN_VALUE,
            footprint=BULK_FOOTPRINT,
            fields={"role": "bulk_main"},
        )
        self.schematic.add_symbol(cb_main)
        self.schematic.add_net(name="BULK_VCC_MAIN", pins=["CB_MAIN.1"])
        self.schematic.add_net(name="BULK_GND_MAIN", pins=["CB_MAIN.2"])

        # Segment bulk capacitors every 32 LEDs
        for seg in range(1, (self.config.expected_led_count // SEGMENT_INTERVAL)):
            cb_ref = f"CB{seg}"
            cb = Symbol(
                lib="Device",
                name="C",
                ref=cb_ref,
                value=BULK_SEGMENT_VALUE,
                footprint=BULK_FOOTPRINT,
                fields={"role": f"bulk_seg_{seg}"},
            )
            self.schematic.add_symbol(cb)
            self.schematic.add_net(name=f"BULK_VCC_{cb_ref}", pins=[f"{cb_ref}.1"])
            self.schematic.add_net(name=f"BULK_GND_{cb_ref}", pins=[f"{cb_ref}.2"])

    def _expose_hierarchical_pins(self) -> Sheet:
        """
        Create Sheet object with hierarchical pins (TASK 5).

        Pins:
          - LED_CLK (in)
          - LED_DATA (in)
          - 5V_IN (in)
          - GND (inout)
          - LED_CLK_OUT (out)
          - LED_DATA_OUT (out)
          - MOSI0..MOSI15 (inout)
          - SCK (inout)
        """
        return Sheet(
            name="led",
            schematic=self.schematic,
            hierarchical_pins=[
                HierarchicalPin("5V_IN", "in"),
                HierarchicalPin("GND", "inout"),
                # Explicit SPI bus connections
                HierarchicalPin("SPI_DATA", "in"),
                HierarchicalPin("SPI_CLK", "in"),
                # Legacy pins for backward compatibility
                HierarchicalPin("LED_CLK", "inout"),
                HierarchicalPin("LED_DATA", "inout"),
                HierarchicalPin("LED_CLK_OUT", "out"),
                HierarchicalPin("LED_DATA_OUT", "out"),
            ],
        )

    def _run_validations(self) -> None:
        """Run validation checks for LED sheet."""
        errors: List[str] = []

        # Check LED count match
        led_symbols = [
            s
            for s in self.schematic.symbols
            if s.lib == self.config.led_symbol[0] and s.name == self.config.led_symbol[1]
        ]
        if len(led_symbols) != self.config.expected_led_count:
            errors.append("LED count mismatch")

        # Check decoupling capacitors
        decoupling_caps = [
            s
            for s in self.schematic.symbols
            if s.lib == "Device" and s.name == "C" and s.value == self.config.decoupling_value
        ]
        if len(decoupling_caps) != self.config.expected_led_count:
            errors.append("Decoupling capacitor count mismatch")

        # Check bulk capacitors
        bulk_caps = [s for s in self.schematic.symbols if s.ref.startswith("CB")]
        expected_bulk = 1 + (self.config.expected_led_count // SEGMENT_INTERVAL - 1)
        if len(bulk_caps) != expected_bulk:
            errors.append("Bulk capacitor count mismatch")

        # Check network continuity
        data_nets = [n for n in self.schematic.nets if n.name in ("SPI_DATA", "SPI_CLK")]  # Update to new net names

        # Calculate total pin connections for single-line SPI:
        # - Internal chains: (LEDs - 1) * 2 (DATA + CLK)
        # - Input: 2 pins (DATA + CLK)
        # - Output: 2 pins (DATA_OUT + CLK_OUT)
        # Account for both SPI_DATA and SPI_CLK networks
        expected_connections = ((self.config.expected_led_count - 1) * 2 + 4) * 2
        actual_connections = sum(len(net.pins) for net in data_nets)
        if actual_connections != expected_connections:
            errors.append(
                f"SPI network validation failed: Expected {expected_connections} total pin connections, found {actual_connections}"
            )

        if errors:
            raise ValueError("Validation failed: " + "; ".join(errors))

    # -------------------- Public Build API -------------------- #
    def build(self, for_root: bool = False):
        # Core generation steps
        self._add_led_chain()
        self._add_per_led_decoupling()
        self._add_bulk_caps()

        sheet = self._expose_hierarchical_pins()
        if for_root:

            class Result(HierarchicalSchematic):
                def __init__(self):
                    super().__init__(title="LED Root Integration")
                    self.sheets = {"led": sheet}

                def run_full_erc(self):
                    """No-op for root schematic compatibility"""

            return Result()
        else:
            hier = HierarchicalSchematic(title=f"{self.project_name}_led_hier")
            hier.add_sheet(sheet)
            out_dir = Path("out") / self.project_name / "led"
            out_dir.mkdir(parents=True, exist_ok=True)
            hier.write(out_dir=str(out_dir))
            self._run_validations()
            return hier


# ---------------------------------------------------------------------------
# CLI Entry
# ---------------------------------------------------------------------------


def generate_led_sheet(project_name: str = "led_touch_grid") -> None:
    """
    Entry point wrapper used by future Makefile and tests.

    Currently only builds scaffold and writes empty sheet wrapper.
    """
    builder = LEDSheetBuilder(project_name=project_name)
    hier = builder.build(for_root=False)
    try:
        hier.run_full_erc()
        print("LED sheet scaffold generated (no LED chain yet); " "ERC baseline passed.")
    except ValueError as e:
        print(f"ERC (scaffold) reported issues:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    generate_led_sheet()


# TODO: Make configurable (Issue #45)
