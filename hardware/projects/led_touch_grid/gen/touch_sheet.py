#!/usr/bin/env python3
"""
Touch sheet generator for LED Touch Grid.

Creates an 8x8 (64 pad) capacitive touch matrix (logical/abstract layer).

Features:
- 64 touch pad symbols (P1..P64) laid out in an 8x8 grid (row-major)
- Optional RC/ESD placeholder components (future extension – not yet enforced)
- Hierarchical pins exporting touch bus + power/ground
- Validation ensuring expected pad count (64)
- Integration with existing hierarchical + ERC pipeline (run_full_erc)

NOTE:
Physical geometry (19mm spacing, pad size) is handled later in PCB placement
generation (not in schematic symbol generation).
"""

import sys
import json
from pathlib import Path
from typing import List, Tuple

# Add project root for imports (before local import)  # noqa: E402
project_root = Path(__file__).resolve()
while not (project_root / "tools").exists() and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

from tools.kicad_helpers import (  # noqa: E402
    Schematic,
    HierarchicalSchematic,
    Symbol,
)

GRID_ROWS = 8
GRID_COLS = 8
EXPECTED_PAD_COUNT = GRID_ROWS * GRID_COLS

# Simple placement spacing (purely informational coordinates)
PAD_SPACING_X = 20.0
PAD_SPACING_Y = 20.0
START_X = 50.0
START_Y = 50.0


def create_touch_pad_symbols() -> List[Symbol]:
    """Create 64 abstract touch pad symbols."""
    symbols: List[Symbol] = []
    ref_idx = 1
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            x = START_X + c * PAD_SPACING_X
            y = START_Y + r * PAD_SPACING_Y
            symbols.append(
                Symbol(
                    lib="Device",
                    name="PAD",
                    ref=f"P{ref_idx}",
                    at=(x, y),
                    value="TouchPad",
                    footprint="",  # Not assigned at schematic stage
                    fields={
                        "Row": str(r),
                        "Col": str(c),
                        "Group": "TOUCH",
                    },
                )
            )
            ref_idx += 1
    return symbols


def create_touch_nets(symbols: List[Symbol]) -> List[Tuple[str, str]]:
    """Map each pad reference to a logical bus net.

    Strategy:
      - Each pad Pn connects to a net GPIO0..GPIO63 (for netlist compatibility)
      - All GPIO nets are then tied to a single bus net TOUCH_GRID_BUS
        via a star connection (abstract; real design may fan out to MCU pins).
    """
    wires: List[Tuple[str, str]] = []
    for idx, sym in enumerate(symbols):
        gpio_net = f"GPIO{idx}"
        # Connect symbol pad (abstract .1) to its net
        wires.append((gpio_net, f"{sym.ref}.1"))
        # Connect net to the aggregated bus
        wires.append(("TOUCH_GRID_BUS", gpio_net))
    return wires


def validate_touch_pad_count(sch: Schematic) -> None:
    """Ensure the schematic contains the expected number of pad symbols."""
    pads = [s for s in sch.symbols if s.name == "PAD" and s.ref.startswith("P")]
    if len(pads) != EXPECTED_PAD_COUNT:
        raise ValueError(f"Touch pad count mismatch: have {len(pads)} expected {EXPECTED_PAD_COUNT}")
    print("Touch pad count validation passed.")


def generate_touch_summary(project_name: str, symbols: List[Symbol]) -> None:
    """Generate the touch summary JSON file for test compatibility."""
    summary_data = {
        "symbols": [{"name": sym.name} for sym in symbols if sym.name == "PAD"],
        "total_pads": len([sym for sym in symbols if sym.name == "PAD"]),
    }

    out_dir = Path("out") / project_name / "touch"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_file = out_dir / f"{project_name}_touch_summary.json"
    summary_file.write_text(json.dumps(summary_data, indent=2))


class TouchSchematicBuilder:
    def __init__(self, project_name: str = "led_touch_grid"):
        self.project_name = project_name
        self.sheets = {}

    def build(self, for_root: bool = False):
        # Create hierarchical schematic
        hier_schematic = HierarchicalSchematic(title=f"{self.project_name}_touch_hier")

        # Create touch sheet
        touch_sheet = hier_schematic.create_sheet("touch")

        # Add hierarchical pins
        hier_schematic.add_hier_pin("touch", "TOUCH_GRID_BUS", "inout")
        hier_schematic.add_hier_pin("touch", "3.3V_IN", "in")
        hier_schematic.add_hier_pin("touch", "GND", "inout")

        # Symbols
        pad_syms = create_touch_pad_symbols()
        for sym in pad_syms:
            hier_schematic.add_symbol_to_sheet("touch", sym)

        # Power / reference
        power_symbol = Symbol(ref="P1", value="+3.3V", lib="power", name="+3.3V", fields={"Net": "3.3V"})
        ground_symbol = Symbol(ref="G1", value="GND", lib="power", name="GND", fields={"Net": "GND"})

        hier_schematic.add_symbol_to_sheet("touch", power_symbol)
        hier_schematic.add_symbol_to_sheet("touch", ground_symbol)

        # Wires (abstract connectivity)
        for a, b in create_touch_nets(pad_syms):
            touch_sheet.add_wire(a, b)

        self.sheets["touch"] = touch_sheet

        if for_root:
            # For root integration, return a simple wrapper
            class Result:
                sheets = {"touch": touch_sheet}

            return Result()
        else:
            # Write output and validate
            out_dir = Path("out") / self.project_name / "touch"
            out_dir.mkdir(parents=True, exist_ok=True)
            hier_schematic.write(out_dir=str(out_dir))
            validate_touch_pad_count(touch_sheet)

            # Generate summary file for test compatibility
            generate_touch_summary(self.project_name, pad_syms)

            return hier_schematic


def generate_touch_sheet(project_name: str = "led_touch_grid") -> None:
    """Generate touch sheet artifacts + run validations."""
    builder = TouchSchematicBuilder(project_name=project_name)
    hier = builder.build(for_root=False)
    try:
        hier.run_full_erc()
        print("Touch sheet generated; ERC + pad count OK.")
    except ValueError as e:
        print(f"Validation error:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", nargs="?", default="led_touch_grid")
    args = parser.parse_args()
    generate_touch_sheet(args.project_name)


# TODO: Make configurable (Issue #45)

GRID_SIZE = (8, 8)


GRID_SIZE = (8, 8)
PAD_SIZE_MM = (19.0, 19.0)
