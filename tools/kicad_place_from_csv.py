"""
Apply placements from a CSV into a KiCad PCB file using pcbnew.

This script is intended to be run inside KiCad's python environment where
`pcbnew` is available. Example use inside KiCad's scripting console:

    from tools.kicad_place_from_csv import apply_from_csv
    apply_from_csv(
            '/path/to/board.kicad_pcb',
            'projects/button_bar/placements/grid_placements.csv',
    )

    The script will attempt to find modules by reference (ref) or by
    footprint name.
It will move matching modules to the XY locations (in mm) and set rotation.

    It will NOT create modules. You must have a board with the modules
    already present with the same reference designators as the CSV 'ref'
    column.
"""

from __future__ import annotations

import csv
import os
import sys


def mm_to_nm(mm: float) -> int:
    # pcbnew uses nanometers internally in recent KiCad python API
    return int(mm * 1e6)


def apply_from_csv(board_path: str, csv_path: str) -> None:
    import pcbnew

    if not os.path.exists(board_path):
        raise FileNotFoundError(board_path)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    board = pcbnew.LoadBoard(board_path)

    refs_updated = 0
    with open(csv_path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            ref = row["ref"]
            x_mm = float(row["x_mm"]) if row.get("x_mm") else 0.0
            y_mm = float(row["y_mm"]) if row.get("y_mm") else 0.0
            rotation = float(row.get("rotation") or 0.0)

            mod = board.FindModuleByReference(ref)
            if not mod:
                # try find by value / footprint if ref not present
                print(f"Module {ref} not found by reference; skipping")
                continue

            pos = pcbnew.VECTOR2I(mm_to_nm(x_mm), mm_to_nm(y_mm))
            mod.SetPosition(pos)
            # rotation is degrees in CSV; pcbnew expects 10*n degrees in older
            # API or can use SetOrientation in KiCad 6+; use RotationDegrees
            # method if present
            try:
                if hasattr(mod, "SetOrientation"):
                    mod.SetOrientation(int(rotation * 10))
                elif hasattr(mod, "SetRotation"):
                    mod.SetRotation(int(rotation * 10))
                else:
                    mod.SetOrientation(int(rotation * 10))
            except Exception:
                # best effort; continue
                pass

            refs_updated += 1

    pcbnew.SaveBoard(board_path, board)
    print(f"Updated {refs_updated} modules in board {board_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: kicad_place_from_csv.py <board.kicad_pcb> <placements.csv>")
        raise SystemExit(2)
    apply_from_csv(sys.argv[1], sys.argv[2])
