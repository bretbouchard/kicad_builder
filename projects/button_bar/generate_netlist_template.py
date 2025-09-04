"""Generate a simple netlist template CSV mapping component refdes to nets

This script reads `bom.csv` and `pinmap.json` and emits a basic mapping for
U1 (RP2040), J1 (USB connector) and the matrix switches (SW1..SW8) mapping
U1 GPIOs to ROW/COL nets per the pinmap rows/cols.

Outputs: projects/button_bar/netlist_template.csv
"""

import csv
import json
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
project = repo / "projects" / "button_bar"

bom = project / "bom.csv"
pinmap = project / "pinmap.json"
out = project / "netlist_template.csv"

pm = json.loads(pinmap.read_text())
rows = pm.get("rows", {})
cols = pm.get("cols", {})

with bom.open() as f:
    reader = csv.DictReader(f)
    parts = list(reader)

with out.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["refdes", "component", "nets"])
    for p in parts:
        ref = p["refdes"]
        comp = p["component"]
        if ref.startswith("U1"):
            # map U1 GPIOs used by rows/cols
            nets = []
            for rname, gpio in rows.items():
                nets.append(f"{gpio}:{rname}")
            for cname, gpio in cols.items():
                nets.append(f"{gpio}:{cname}")
            w.writerow([ref, comp, ";".join(nets)])
        elif ref.startswith("J1"):
            w.writerow([ref, comp, "VBUS;USB_DPLUS;USB_DMINUS;GND"])
        elif ref.startswith("SW"):
            # individual switches are grouped ranges in BOM (SW1-SW8)
            w.writerow([ref, comp, "ROWn;COLn"])
        else:
            w.writerow([ref, comp, ""])

print(f"Wrote {out}")
