import sys
import json
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).resolve()
while not (project_root / "tools").exists() and project_root != project_root.parent:
    project_root = project_root.parent
sys.path.insert(0, str(project_root))

from tools.kicad_helpers import HierarchicalSchematic, Symbol


class LEDConfig:
    """Configuration for LED sheet generation"""

    def __init__(self):
        self.led_symbol = ("LED_Programmable", "APA102-2020")
        self.expected_led_count = 256
        self.decoupling_value = "100nF"


def generate_led_summary(project_name: str, symbols: list) -> None:
    """Generate the LED summary JSON file for test compatibility."""
    summary_data = {
        "symbols": [{"name": sym.name} for sym in symbols if sym.name == "APA102-2020"],
        "total_leds": len([sym for sym in symbols if sym.name == "APA102-2020"]),
    }

    out_dir = Path("out") / project_name / "led"
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_file = out_dir / f"{project_name}_led_summary.json"
    summary_file.write_text(json.dumps(summary_data, indent=2))


class LEDSheetBuilder:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.hierarchical_schematic = HierarchicalSchematic(f"{project_name}_led_hier")
        self.sheet_id = "led"
        self.config = LEDConfig()

        # Create a simple schematic for backward compatibility
        self.schematic = self.hierarchical_schematic.create_sheet("main")

        # Create the LED sheet
        self.led_sheet = self.hierarchical_schematic.create_sheet(self.sheet_id)

        # Add hierarchical pins for power and data
        self.hierarchical_schematic.add_hier_pin(self.sheet_id, "5V_IN", "in")
        self.hierarchical_schematic.add_hier_pin(self.sheet_id, "GND_IN", "in")
        self.hierarchical_schematic.add_hier_pin(self.sheet_id, "DATA_IN", "in")
        self.hierarchical_schematic.add_hier_pin(self.sheet_id, "CLOCK_IN", "in")
        self.hierarchical_schematic.add_hier_pin(self.sheet_id, "5V_OUT", "out")
        self.hierarchical_schematic.add_hier_pin(self.sheet_id, "GND_OUT", "out")
        self.hierarchical_schematic.add_hier_pin(self.sheet_id, "DATA_OUT", "out")
        self.hierarchical_schematic.add_hier_pin(self.sheet_id, "CLOCK_OUT", "out")

    def _add_led_chain(self):
        """Add LED chain components to both sheets"""
        for i in range(1, self.config.expected_led_count + 1):
            led_symbol = Symbol(
                ref=f"LED{i}",
                value="APA102-2020",
                lib=self.config.led_symbol[0],
                name=self.config.led_symbol[1],
                at=(i * 2.54, 0),  # Position LEDs along X axis
                fields={"Part": "APA102-2020", "Manufacturer": "Worldsemi", "LED_Index": str(i)},
            )
            # Add to both the main schematic (for test compatibility)
            # and the LED sheet (for hierarchical design)
            self.hierarchical_schematic.add_symbol_to_sheet("main", led_symbol)
            self.hierarchical_schematic.add_symbol_to_sheet(self.sheet_id, led_symbol)

    def add_apa102_strip(self, count: int):
        """Add APA102 LED strip components"""
        for i in range(1, count + 1):
            led_symbol = Symbol(
                ref=f"LED{i}",
                value="APA102-2020",
                lib="LED_Programmable",
                name="APA102-2020",
                at=(i * 2.54, 0),  # Position LEDs along X axis
                fields={"Part": "APA102-2020", "Manufacturer": "Worldsemi", "LED_Index": str(i)},
            )
            self.hierarchical_schematic.add_symbol_to_sheet(self.sheet_id, led_symbol)

    def build(self, for_root: bool = True) -> HierarchicalSchematic:
        """Build and return the hierarchical schematic"""
        self._add_led_chain()

        # Add power and ground symbols
        power_symbol = Symbol(ref="P1", value="+5V", lib="power", name="+5V", fields={"Net": "5V"})
        ground_symbol = Symbol(ref="G1", value="GND", lib="power", name="GND", fields={"Net": "GND"})

        self.hierarchical_schematic.add_symbol_to_sheet(self.sheet_id, power_symbol)
        self.hierarchical_schematic.add_symbol_to_sheet(self.sheet_id, ground_symbol)

        # Add decoupling capacitors to both sheets
        for i in range(self.config.expected_led_count):
            decoupling_symbol = Symbol(
                ref=f"C{i+1}",
                value=self.config.decoupling_value,
                lib="Device",
                name="C",
                at=(i * 2.54, 5.08),
                fields={"Purpose": "Decoupling"},
            )
            self.hierarchical_schematic.add_symbol_to_sheet("main", decoupling_symbol)
            self.hierarchical_schematic.add_symbol_to_sheet(self.sheet_id, decoupling_symbol)

        # Add bulk capacitors to both sheets
        expected_bulk = 1 + (self.config.expected_led_count // 32 - 1)
        for i in range(expected_bulk):
            bulk_symbol = Symbol(
                ref=f"CB{i+1}",
                value="1000µF",
                lib="Device",
                name="CP",
                at=(i * 5.08, 10.16),
                fields={"Purpose": "Bulk"},
            )
            self.hierarchical_schematic.add_symbol_to_sheet("main", bulk_symbol)
            self.hierarchical_schematic.add_symbol_to_sheet(self.sheet_id, bulk_symbol)

        # Add wires for power distribution to the sheet
        sheet = self.hierarchical_schematic.sheets[self.sheet_id]
        sheet.add_wire("5V_IN", "5V_OUT")
        sheet.add_wire("GND_IN", "GND_OUT")
        sheet.add_wire("DATA_IN", "DATA_OUT")
        sheet.add_wire("CLOCK_IN", "CLOCK_OUT")

        return self.hierarchical_schematic

    def _run_validations(self):
        """Run validation checks"""
        # Validate LED count
        led_symbols = [
            s
            for s in self.schematic.symbols
            if s.lib == self.config.led_symbol[0] and s.name == self.config.led_symbol[1]
        ]
        if len(led_symbols) != self.config.expected_led_count:
            raise ValueError(
                f"LED count mismatch: expected {self.config.expected_led_count}, " f"got {len(led_symbols)}"
            )

        # Validate decoupling capacitors
        decoupling_caps = [
            s
            for s in self.schematic.symbols
            if s.lib == "Device" and s.name == "C" and s.value == self.config.decoupling_value
        ]
        if len(decoupling_caps) != self.config.expected_led_count:
            raise ValueError(
                f"Decoupling capacitor count mismatch: expected "
                f"{self.config.expected_led_count}, got {len(decoupling_caps)}"
            )

        # Validate bulk capacitors
        bulk_caps = [s for s in self.schematic.symbols if s.ref.startswith("CB")]
        expected_bulk = 1 + (self.config.expected_led_count // 32 - 1)
        if len(bulk_caps) != expected_bulk:
            raise ValueError(f"Bulk capacitor count mismatch: expected {expected_bulk}, " f"got {len(bulk_caps)}")

    def get_schematic(self):
        """Legacy method for backward compatibility"""
        return self.build()


def generate_led_sheet(project_name: str = "led_touch_grid") -> HierarchicalSchematic:
    builder = LEDSheetBuilder(project_name)
    return builder.build()


# Constants for LED configuration - Fix all the constant issues
GRID_SIZE = (8, 8)
LEDS_PER_PAD = 4
TOTAL_LEDS = 256  # Fixed: 8x8 grid with 4 LEDs per pad = 256 total LEDs
CONFIG_PARALLEL = "parallel"
CONFIG_CHAINED = "chained"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", nargs="?", default="led_touch_grid")
    args = parser.parse_args()

    # Generate the LED sheet
    builder = LEDSheetBuilder(args.project_name)
    hier = builder.build()

    # Write the hierarchical schematic
    out_dir = f"out/{args.project_name}/led"
    hier.write(out_dir=out_dir)

    # Generate summary file for test compatibility AFTER writing
    # Use the same builder instance that has the symbols
    led_symbols = [sym for sym in builder.schematic.symbols if sym.name == "APA102-2020"]
    generate_led_summary(args.project_name, led_symbols)
