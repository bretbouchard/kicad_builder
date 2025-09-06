"""
Create a new KiCad PCB file and populate it with modules from a placements CSV.

Usage (inside KiCad's Python console):

  from tools.kicad_create_board_from_csv import create_board_from_csv
  create_board_from_csv('new_board.kicad_pcb', 'projects/button_bar/placements/grid_placements.csv')

Notes:
- This script must be run where `pcbnew` is available (KiCad's Python).
- The CSV must contain columns: ref, footprint, x_mm, y_mm, rotation.
- `footprint` entries should be in the form 'LIB:FOOTPRINT' where the
  footprint library is available to KiCad. If footprints are stored in
  project-local .kicad_mod files, you may need to install or point KiCad's
  library tables to those paths before running.

This is a convenience helper to create a board skeleton you can then open
in KiCad for routing and final adjustments.
"""

from __future__ import annotations

import csv
import os
import sys


def _read_dotenv(dotenv_path: str) -> dict:
    """Very small .env parser: returns dict of KEY->VALUE for simple KEY=VALUE lines."""
    out = {}
    try:
        with open(dotenv_path, "r", encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln or ln.startswith("#"):
                    continue
                if "=" not in ln:
                    continue
                k, v = ln.split("=", 1)
                v = v.strip().strip('"').strip("'")
                out[k.strip()] = v
    except Exception:
        pass
    return out


def _get_footprint_dir() -> str:
    """Return footprint directory from env or .env or default project path."""
    # priority: KICAD_FOOTPRINTS_DIR env var, .env in repo root, then default
    env_val = os.environ.get("KICAD_FOOTPRINTS_DIR")
    if env_val:
        return env_val

    dotenv = os.path.join(os.getcwd(), ".env")
    vals = _read_dotenv(dotenv)
    if "KICAD_FOOTPRINTS_DIR" in vals:
        return vals["KICAD_FOOTPRINTS_DIR"]

    # default to the project-local footprints folder
    return os.path.join("projects", "button_bar", "footprints.pretty")


def mm_to_nm(mm: float) -> int:
    return int(mm * 1e6)


def create_board_from_csv(out_board: str, csv_path: str) -> None:
    """Create a new KiCad board and add footprint modules based on CSV."""
    try:
        import pcbnew
    except Exception as e:
        raise RuntimeError("This script must be run inside KiCad (pcbnew available)") from e

    # Ensure a wx App exists for GUI-related pcbnew calls (needed when running
    # KiCad's python from command line on macOS)
    try:
        import wx

        if not wx.GetApp():
            _app = wx.App(False)
    except Exception:
        # If wx is not present or fails, continue; pcbnew may still work.
        pass

    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    board = pcbnew.BOARD()  # create empty board object

    placed = 0
    with open(csv_path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            ref = row.get("ref")
            footprint = row.get("footprint") or ""
            x_mm = float(row.get("x_mm") or 0.0)
            y_mm = float(row.get("y_mm") or 0.0)
            rotation = float(row.get("rotation") or 0.0)

            # Expect footprint like 'LIB:NAME' — split if possible
            if ":" in footprint:
                lib, name = footprint.split(":", 1)
            else:
                lib = ""
                name = footprint

            module = None
            # First try normal FootprintLoad (library table must know lib)
            try:
                module = pcbnew.FootprintLoad(lib, name)
            except Exception:
                module = None

            # Fallback: search project footprints.pretty for a matching .kicad_mod
            if module is None:
                try:
                    proj_fp_dir = _get_footprint_dir()
                    for root, _, files in os.walk(proj_fp_dir):
                        for fn in files:
                            if not fn.lower().endswith(".kicad_mod"):
                                continue
                            candidate = os.path.join(root, fn)
                            file_base = os.path.splitext(fn)[0]
                            # Try a few common FootprintLoad argument patterns
                            for lib_arg, fp_arg in (
                                (file_base, file_base),
                                (root, file_base),
                                (candidate, file_base),
                                (root, name),
                                (candidate, name),
                            ):
                                try:
                                    module = pcbnew.FootprintLoad(lib_arg, fp_arg)
                                    if module is not None:
                                        break
                                except Exception:
                                    module = None
                            if module is not None:
                                break

                            # Last-resort: parse the .kicad_mod to find the declared footprint name
                            try:
                                with open(candidate, "r", encoding="utf-8", errors="ignore") as ff:
                                    data = ff.read()
                                import re

                                m = re.search(r"\(footprint\s+([^\s\)]+)", data)
                                if m:
                                    declared = m.group(1)
                                    try:
                                        module = pcbnew.FootprintLoad(candidate, declared)
                                    except Exception:
                                        module = None
                            except Exception:
                                module = None

                            if module is not None:
                                break
                        if module is not None:
                            break
                except Exception:
                    module = None

            if module is None:
                print(f"Failed to load footprint {footprint}; skipping {ref}")
                continue

            # Set reference and position
            try:
                module.SetReference(ref)
            except Exception:
                pass

            module.SetPosition(pcbnew.VECTOR2I(mm_to_nm(x_mm), mm_to_nm(y_mm)))
            try:
                # rotation API differs across versions; SetOrientation expects 10*deg
                if hasattr(module, "SetOrientation"):
                    module.SetOrientation(int(rotation * 10))
                else:
                    module.SetRotation(int(rotation * 10))
            except Exception:
                pass

            board.Add(module)
            placed += 1

    # Save board to file
    pcbnew.SaveBoard(out_board, board)
    print(f"Created board {out_board} with {placed} modules")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: kicad_create_board_from_csv.py <out.kicad_pcb> <placements.csv>")
        raise SystemExit(2)
    create_board_from_csv(sys.argv[1], sys.argv[2])
