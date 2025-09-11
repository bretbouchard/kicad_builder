import sys
from pathlib import Path

# ruff: noqa: E402

# Add project root to path for imports
project_root = Path(__file__).resolve()
while not (project_root / "tools").exists() and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

import json
from typing import Any, List

# Defer importing project helpers until after sys.path is set to avoid
# import-time side effects and satisfy linters (E402).


def generate_mcu_summary(project_name: str, symbols: List[Any]) -> None:
    """Generate the MCU summary JSON file for test compatibility."""
    summary_data = {
        "symbols": [{"name": sym.name} for sym in symbols if "RP2040" in sym.name],
        "total_mcus": len([sym for sym in symbols if "RP2040" in sym.name]),
    }

    out_dir = Path("out") / project_name / "mcu"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_file = out_dir / f"{project_name}_mcu_summary.json"
    summary_file.write_text(json.dumps(summary_data, indent=2))


def generate_mcu_sheet(project_name: str = "led_touch_grid") -> Any:
    from tools.kicad_helpers import HierarchicalSchematic, Symbol

    hier = HierarchicalSchematic(f"{project_name}_mcu_hier")
    # Create the mcu sheet
    hier.create_sheet("mcu")

    # MCU Components using Symbol class
    mcu_components = [
        Symbol(ref="U1", value="RP2040", lib="MCU_RaspberryPi", name="RP2040-QFN56", sheet="mcu"),
        Symbol(ref="U2", value="RP2040", lib="MCU_RaspberryPi", name="RP2040-QFN56", sheet="mcu"),
        *[Symbol(ref=f"C{i}", value="100nF 50V", lib="Device", name="Capacitor_SMD", sheet="mcu") for i in range(1, 9)],
        Symbol(ref="Y1", value="12MHz", lib="Device", name="Crystal", sheet="mcu"),
        Symbol(ref="Y2", value="12MHz", lib="Device", name="Crystal", sheet="mcu"),
        # Load capacitors for crystals (22pF)
        *[
            Symbol(ref=f"C{i + 20}", value="22pF 50V", lib="Device", name="Capacitor_SMD", sheet="mcu")
            for i in range(1, 5)
        ],
    ]

    for symbol in mcu_components:
        hier.add_symbol_to_sheet("mcu", symbol)

    # Interface Pins
    interface_pins = [
        ("LED_SPI_BUS", "out"),
        ("TOUCH_GPIO_BUS", "inout"),
        ("I2C_SDA", "inout"),
        ("I2C_SCL", "inout"),
        ("RESET", "in"),
        ("ENABLE", "in"),
        ("3.3V_IN", "in"),
        ("GND", "power_in"),
    ]

    for name, dir in interface_pins:
        hier.add_hier_pin("mcu", name, dir)

    # Generate summary file for test compatibility
    generate_mcu_summary(project_name, mcu_components)

    return hier


def validate_mcu_power_decoupling(hier_schematic: object) -> None:
    """Validate MCU power decoupling rules.

    Args:
        hier_schematic: Either a HierarchicalSchematic object with sheets["mcu"]
                        or a Schematic object directly.
    """
    # Handle both HierarchicalSchematic and Schematic objects
    if hasattr(hier_schematic, "sheets") and "mcu" in hier_schematic.sheets:
        # This is a HierarchicalSchematic object
        symbols = hier_schematic.sheets["mcu"].symbols
    elif hasattr(hier_schematic, "symbols"):
        # This is a Schematic object directly
        symbols = hier_schematic.symbols
    else:
        raise ValueError("Invalid schematic object type")

    # Count MCUs and calculate required decoupling capacitors (4 per MCU)
    mcus = [symbol for symbol in symbols if symbol.lib in ["MCU", "RP2040"] or "RP2040" in getattr(symbol, "name", "")]
    required_decaps = len(mcus) * 4

    decaps = [symbol for symbol in symbols if "100nF" in symbol.value]
    if len(decaps) < required_decaps:
        raise ValueError("Insufficient decoupling")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", nargs="?", default="led_touch_grid")
    args = parser.parse_args()

    schematic = generate_mcu_sheet(args.project_name)
    # Run local validation (raise non-zero exit on validation failure) so
    # tests that patch this generator can detect missing required parts.
    try:
        validate_mcu_power_decoupling(schematic)
    except Exception as e:
        print(f"ERC/validation error: {e}", file=sys.stderr)
        sys.exit(1)

    schematic.write(f"out/{args.project_name}/mcu")
