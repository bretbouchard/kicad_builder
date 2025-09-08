#!/usr/bin/env python3
"""gen_symbol.py

Generate a minimal KiCad symbol library entry from a pinmap JSON.

Usage:
  python3 gen_symbol.py pinmap.json out.lib --footprint "LIB:FOO" --package RP2040
"""

from pathlib import Path
import argparse
import json


TEMPLATE_HEADER = "(kicad_symbol_lib (version 20211014) (generator gen_symbol))\n"


from typing import Dict, Any


def make_symbol(name: str, pinmap: Dict[str, Any], footprint: str = "REPO-MCU:REPO-MCU-QFN56") -> str:
    pins: Dict[str, str] = pinmap.get("pin_to_signal", {})
    lines = []
    lines.append(f'(symbol "{name}")')
    lines.append("  (pin_numbers_have_shape)")
    lines.append('  (property "Value" "' + name + '")')
    lines.append(f'  (property "Footprint" "{footprint}")')
    lines.append('  (property "Package" "QFN-56")')
    lines.append('  (property "Note" "Generated symbol — review pin names")')
    # pins
    for pnum, sig in pins.items():
        lines.append(f'  (pin {pnum} passive line (at 0 0) (length 1) (name "{sig}"))')
    lines.append(")")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Generate a KiCad symbol from a pinmap JSON")
    p.add_argument("pinmap")
    p.add_argument("out")
    p.add_argument("--footprint", default="REPO-MCU:REPO-MCU-QFN56", help="Footprint lib:name to embed")
    p.add_argument("--package", default=None, help="Override package name in symbol")
    args = p.parse_args()

    pinmap_path = Path(args.pinmap)
    if not pinmap_path.exists() or not pinmap_path.is_file() or pinmap_path.stat().st_size == 0:
        print(f"Pinmap {pinmap_path} not found or empty; skipping generation.")
        return
    try:
        pm = json.loads(pinmap_path.read_text())
    except json.JSONDecodeError:
        print(f"Pinmap {pinmap_path} contains invalid JSON; skipping generation.")
        return
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    name = pm.get("description", "PART").split()[0]
    if args.package:
        pm["package"] = args.package
    content = TEMPLATE_HEADER + make_symbol(name, pm, footprint=args.footprint)
    out_path.write_text(content)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
