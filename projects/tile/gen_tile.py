"""Generator for a single RP2040 tile schematic (starter).

This script uses `tools.kicad_helpers.Schematic` to create a small
schematic description and writes `out/tile_summary.json` and a human-readable
`.sch.txt` file. It's a starting point — later we'll extend the helper to
emit true KiCad 9 `.kicad_sch` S-expressions.
"""

import json
import sys
from pathlib import Path

try:
    from kicad_helpers import Schematic, Symbol
except Exception:
    # when running from repo root, ensure tools/ is on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
    from kicad_helpers import Schematic, Symbol


def build_tile():
    sch = Schematic("tile")

    # Add an RP2040 symbol placeholder
    sch.add_symbol(Symbol(lib="MCU", name="RP2040", ref="U1", at=(20.0, 30.0)))

    # Add power symbols
    sch.add_symbol(Symbol(lib="Power", name="VCC", ref="PWR1", at=(5.0, 5.0)))
    sch.add_symbol(Symbol(lib="Power", name="GND", ref="GND1", at=(5.0, 0.0)))

    # Add a few pad symbols (8x8 grid simplified to a 2x2 for starter)
    pad_coords = [(10, 50), (20, 50), (10, 40), (20, 40)]
    for i, at in enumerate(pad_coords, start=1):
        sch.add_symbol(Symbol(lib="Device", name="PAD", ref=f"PAD{i}", at=at))

    # Add a couple of LEDs (as placeholders)
    sch.add_symbol(Symbol(lib="LEDs", name="APA102", ref="D1", at=(40, 50)))
    sch.add_symbol(Symbol(lib="LEDs", name="APA102", ref="D2", at=(40, 40)))

    # Nets (logical grouping)
    # Use numeric pin references for the RP2040 QFN-56 symbol
    # Mapping (placeholder): VCC -> pin 4, GND -> pin 5, GP0 -> pin 13
    sch.add_net("VCC", ["U1.4", "PWR1.1"])
    sch.add_net("GND", ["U1.5", "GND1.1"])
    sch.add_net("LED_DATA", ["D1.DATA", "U1.13"])

    # Power flags
    sch.add_power_flag("VCC", at=(5.0, 5.0))
    sch.add_gnd(at=(5.0, 0.0))

    return sch


def main():
    out = Path("out")
    out.mkdir(exist_ok=True)
    sch = build_tile()
    # write human readable + JSON summary
    sch.write(out_dir=str(out))
    # write minimal KiCad-like .kicad_sch
    sch.write_kicad_sch(out_dir=str(out))

    summary = sch.summary()
    with open(out / "tile_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("Generated: out/tile.sch.txt and out/tile_summary.json")


if __name__ == "__main__":
    main()
