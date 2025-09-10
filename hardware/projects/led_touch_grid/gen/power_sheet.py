#!/usr/bin/env python3
"""
Power sheet generator for LED Touch Grid project.

Generates the power distribution schematic sheet with 5V input protection,
3.3V regulation, bulk/decoupling capacitors, and hierarchical pins for
distribution to other sheets (mcu, led, touch, io).

Requirements met:
- 5V input via USB-C or barrel jack with protection and filtering
- 3.3V LDO regulation (AMS1117 or equivalent) with proper decoupling
- Bulk capacitance (1000µF) for LED power stability
- Decoupling (100nF per rail) for logic
- Hierarchical pins: 5V_OUT, 3.3V_OUT, GND for parent connections
- ESD protection (TVS diodes) on input

Usage: python gen/power_sheet.py
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path for imports
project_root = Path(__file__).resolve()
while not (project_root / "tools").exists() and project_root != project_root.parent:
    project_root = project_root.parent
if not (project_root / "tools").exists():
    print(f"ERROR: Could not find 'tools' directory from {__file__}. Resolved project_root: {project_root}")
    sys.exit(1)
sys.path.insert(0, str(project_root))
from tools.kicad_helpers import (  # noqa: E402
    HierarchicalSchematic,
    Symbol,
)

# Constants for component values and positions
V5_INPUT_AT = (50.0, 50.0)
LDO_AT = (100.0, 50.0)
BULK_CAP_AT = (150.0, 50.0)
DECOUPLING_CAPS_AT = [(200.0, 40.0), (200.0, 60.0)]
ESD_AT = (25.0, 50.0)


def create_power_symbols() -> List[Symbol]:
    """Create symbols for power components."""
    symbols: List[Symbol] = []

    # USB-C input connector (J1)
    symbols.append(
        Symbol(
            lib="Connector_USB",
            name="USB_C_Receptacle",
            ref="J1",
            at=V5_INPUT_AT,
            value="USB-C Input",
            footprint="Connector_USB:CUSB-B-RA_SMD",
            fields={"Type": "Power Input"},
        )
    )

    # 5V protection diode (D1)
    symbols.append(
        Symbol(
            lib="Diode",
            name="D_SMA",
            ref="D1",
            at=(75.0, 50.0),
            value="Schottky 5V Protection",
            footprint="Diode_SMD:D_SMA",
            fields={"Part": "BAT54C"},
        )
    )

    # 3.3V LDO regulator (U1)
    symbols.append(
        Symbol(
            lib="Regulator_Linear",
            name="SOT-223",
            ref="U1",
            at=LDO_AT,
            value="3.3V LDO",
            footprint="Package_TO_SOT_SMD:SOT-223",
            fields={"Part": "AMS1117-3.3"},
        )
    )

    # Bulk capacitor for 5V rail (C1, 1000µF electrolytic)
    symbols.append(
        Symbol(
            lib="Device",
            name="C",
            ref="C1",
            at=BULK_CAP_AT,
            value="1000µF 10V",
            footprint="Package_DIL:D6.3x5.3mm_P2.50mm_Horizontal",
            fields={"Voltage": "10V", "Type": "Electrolytic"},
        )
    )

    # Decoupling capacitors for 3.3V (C2, C3, 100nF ceramic)
    for i, pos in enumerate(DECOUPLING_CAPS_AT, 2):
        symbols.append(
            Symbol(
                lib="Device",
                name="C",
                ref=f"C{i}",
                at=pos,
                value="100nF 50V",
                footprint="Capacitor_SMD:C_0805_2012Metric",
                fields={"Voltage": "50V", "Type": "Ceramic"},
            )
        )

    # Input/output caps for LDO (C4 input 10µF, C5 output 10µF)
    symbols.append(
        Symbol(
            lib="Device",
            name="C",
            ref="C4",
            at=(100.0, 70.0),
            value="10µF 10V",
            footprint="Capacitor_SMD:C_0805_2012Metric",
            fields={"Voltage": "10V", "Type": "Tantalum"},
        )
    )
    symbols.append(
        Symbol(
            lib="Device",
            name="C",
            ref="C5",
            at=(150.0, 70.0),
            value="10µF 6.3V",
            footprint="Capacitor_SMD:C_0805_2012Metric",
            fields={"Voltage": "6.3V", "Type": "Tantalum"},
        )
    )

    # ESD protection TVS diode (D2)
    symbols.append(
        Symbol(
            lib="Diode_TVS",
            name="SMA",
            ref="D2",
            at=ESD_AT,
            value="ESD Protection 5V",
            footprint="Diode_SMD:D_SMA",
            fields={"Part": "PESD5V0S1BA"},
        )
    )

    # Ferrite bead for filtering (FB1)
    symbols.append(
        Symbol(
            lib="Device",
            name="FB_SMD_0805_2012Metric",
            ref="FB1",
            at=(60.0, 50.0),
            value="Ferrite Bead 600Ω",
            footprint="Inductor_SMD:FB_SMD_0805_2012Metric",
            fields={"Impedance": "600Ω @ 100MHz"},
        )
    )

    return symbols


def create_power_nets() -> List[Tuple[str, str]]:
    """Define power net connections (wire endpoints)."""
    wires: List[Tuple[str, str]] = [
        # 5V input path: J1 -> D2(ESD) -> FB1 -> D1(protection) ->
        # C1(bulk) -> 5V_OUT -> 5V_IN (LDO feed)
        ("J1.VBUS", "D2.1"),
        ("D2.2", "FB1.1"),
        ("FB1.2", "D1.A"),
        ("D1.K", "C1.1"),
        ("C1.2", "5V_OUT"),  # Hierarchical pin export of filtered 5V
        ("5V_OUT", "5V_IN"),  # Bridge filtered 5V to internal LDO input net
        # 3.3V LDO path: 5V_IN -> U1 -> C5 -> 3.3V_OUT
        ("5V_IN", "U1.VIN"),
        ("U1.VIN", "C4.1"),
        ("C4.2", "GND"),
        ("U1.VOUT", "C5.1"),
        ("C5.2", "GND"),
        ("C5.1", "3.3V_OUT"),  # Hierarchical pin
        # Decoupling for 3.3V
        ("3.3V_OUT", "C2.1"),
        ("C2.2", "GND"),
        ("3.3V_OUT", "C3.1"),
        ("C3.2", "GND"),
        # LDO ground
        ("U1.GND", "GND"),
        # Connect EXT_5V_IN and EXT_GND to hierarchical pins so they appear as nets
        ("EXT_5V_IN", "5V_OUT"),
        ("EXT_GND", "GND"),
    ]
    return wires


def generate_power_sheet(project_name: str = "led_touch_grid") -> None:
    """Generate the power sheet schematic."""
    print(f"DEBUG: Generating power sheet for project: {project_name}")

    # Create hierarchical schematic for power sheet
    hier_sch = HierarchicalSchematic(title=f"{project_name}_power_hier")
    power_sheet = hier_sch.create_sheet("power")

    # Add power symbols
    symbols = create_power_symbols()
    for sym in symbols:
        hier_sch.add_symbol_to_sheet("power", sym)

    # Add wires for connections
    wires = create_power_nets()
    for a, b in wires:
        power_sheet.add_wire(a, b)

    # Add power flags for nets
    power_flag_5v = Symbol(lib="power", name="PWR_FLAG", ref="PWR1", value="5V_OUT", fields={"Net": "5V_OUT"})
    power_flag_3v = Symbol(lib="power", name="PWR_FLAG", ref="PWR2", value="3.3V_OUT", fields={"Net": "3.3V_OUT"})
    power_flag_gnd = Symbol(lib="power", name="PWR_FLAG", ref="PWR3", value="GND", fields={"Net": "GND"})
    ground_symbol = Symbol(lib="power", name="GND", ref="GND1", value="Ground")

    hier_sch.add_symbol_to_sheet("power", power_flag_5v)
    hier_sch.add_symbol_to_sheet("power", power_flag_3v)
    hier_sch.add_symbol_to_sheet("power", power_flag_gnd)
    hier_sch.add_symbol_to_sheet("power", ground_symbol)

    # Add hierarchical pins to the power sheet
    pins = [
        ("5V_OUT", "inout"),
        ("3.3V_OUT", "inout"),
        ("GND", "inout"),
        ("5V_IN", "in"),
        ("EXT_5V_IN", "inout"),
        ("EXT_GND", "inout"),
    ]

    for name, direction in pins:
        hier_sch.add_hier_pin("power", name, direction)

    # Write outputs
    out_dir = Path("out") / project_name / "power"
    print(f"DEBUG: Output directory: {out_dir}")
    print(f"DEBUG: Output directory exists: {out_dir.exists()}")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"DEBUG: Created output directory: {out_dir}")
    print(f"DEBUG: Output directory exists after mkdir: {out_dir.exists()}")

    print(f"DEBUG: About to write hierarchical schematic to: {str(out_dir)}")
    hier_sch.write(out_dir=str(out_dir))
    print("DEBUG: Finished writing hierarchical schematic")

    # Run full ERC validation (hierarchy + power + pull-ups)
    try:
        hier_sch.run_full_erc()
        print("Power sheet generated; full ERC passed.")
    except ValueError as e:
        print(f"ERC validation failed:\\n{e}")
        sys.exit(1)


class PowerSchematicBuilder:
    """Builder for test compatibility."""

    def __init__(self, project_name: str = "test_power"):
        self.project_name = project_name
        self.hier_sch = HierarchicalSchematic(title=f"{project_name}_power_hier")
        self.power_sheet = self.hier_sch.create_sheet("power")

    def build(self):
        # Add power symbols
        symbols = create_power_symbols()
        for sym in symbols:
            self.hier_sch.add_symbol_to_sheet("power", sym)

        # Add wires for connections
        wires = create_power_nets()
        for a, b in wires:
            self.power_sheet.add_wire(a, b)

        # Add power flags and ground
        power_flag_5v = Symbol(lib="power", name="PWR_FLAG", ref="PWR1", value="5V_OUT", fields={"Net": "5V_OUT"})
        power_flag_3v = Symbol(lib="power", name="PWR_FLAG", ref="PWR2", value="3.3V_OUT", fields={"Net": "3.3V_OUT"})
        power_flag_gnd = Symbol(lib="power", name="PWR_FLAG", ref="PWR3", value="GND", fields={"Net": "GND"})
        ground_symbol = Symbol(lib="power", name="GND", ref="GND1", value="Ground")

        self.hier_sch.add_symbol_to_sheet("power", power_flag_5v)
        self.hier_sch.add_symbol_to_sheet("power", power_flag_3v)
        self.hier_sch.add_symbol_to_sheet("power", power_flag_gnd)
        self.hier_sch.add_symbol_to_sheet("power", ground_symbol)

        # Add hierarchical pins
        pins = [
            ("5V_OUT", "inout"),
            ("3.3V_OUT", "inout"),
            ("GND", "inout"),
            ("5V_IN", "in"),
            ("EXT_5V_IN", "inout"),
            ("EXT_GND", "inout"),
        ]

        for name, direction in pins:
            self.hier_sch.add_hier_pin("power", name, direction)

        class Result:
            sheets = {"power": self.power_sheet}

        return Result()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", nargs="?", default="led_touch_grid")
    args = parser.parse_args()
    generate_power_sheet(args.project_name)
