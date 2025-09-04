"""Placeholder pick-and-place generator.

Reads BOM CSV and emits placement CSV with placeholder coordinates.
"""

import csv
import pathlib
import tempfile
import os


def main(bom_path: pathlib.Path, out_path: pathlib.Path):
    rows = []
    with bom_path.open("r", encoding="utf8") as f:
        reader = list(csv.DictReader(f))

    # Simple board placement heuristics
    # - place a single MCU near board center
    # - place connectors along bottom edge
    # - place passives (C/R) in a grid at top-right
    width = 100.0
    height = 60.0
    center_x = width / 2
    center_y = height / 2

    # categorize parts
    from typing import Any, Dict

    def _is_mcu(r: Dict[str, Any]) -> bool:
        comp = (r.get("component") or "").upper()
        ref = (r.get("refdes") or "").upper()
        return comp.startswith("RP2040") or ref.startswith("U")

    mcus = [r for r in reader if _is_mcu(r)]

    def _is_connector(r: Dict[str, Any]) -> bool:
        comp = (r.get("component") or "").upper()
        ref = (r.get("refdes") or "").upper()
        return "USB" in comp or ref.startswith("J")

    connectors = [r for r in reader if _is_connector(r)]

    def _is_passive(r: Dict[str, Any]) -> bool:
        comp = (r.get("component") or "").upper()
        return comp.startswith(("CAP", "C", "R"))

    passives = [r for r in reader if _is_passive(r)]

    others = [r for r in reader if r not in mcus and r not in connectors and r not in passives]

    # place MCUs
    for i, r in enumerate(mcus, start=1):
        rows.append(
            {
                "refdes": r.get("refdes"),
                "x": f"{center_x + (i-1)*5.0:.2f}",
                "y": f"{center_y + (i-1)*5.0:.2f}",
                "rotation": "0",
                "footprint": r.get("footprint", ""),
                "value": r.get("value", ""),
            }
        )

    # place connectors along bottom edge spaced evenly
    if connectors:
        span = width - 10
        step = span / max(1, len(connectors))
        for i, r in enumerate(connectors, start=0):
            x = 5 + i * step
            rows.append(
                {
                    "refdes": r.get("refdes"),
                    "x": f"{x:.2f}",
                    "y": f"{5.0:.2f}",
                    "rotation": "0",
                    "footprint": r.get("footprint", ""),
                    "value": r.get("value", ""),
                }
            )

    # passives in grid at top-right
    grid_x0 = width * 0.6
    grid_y0 = height * 0.7
    cols = 6
    spacing_x = 6.0
    spacing_y = 5.0
    for idx, r in enumerate(passives):
        col = idx % cols
        row = idx // cols
        x = grid_x0 + col * spacing_x
        y = grid_y0 + row * spacing_y
        rows.append(
            {
                "refdes": r.get("refdes"),
                "x": f"{x:.2f}",
                "y": f"{y:.2f}",
                "rotation": "0",
                "footprint": r.get("footprint", ""),
                "value": r.get("value", ""),
            }
        )

    # remaining parts along left edge
    for i, r in enumerate(others, start=1):
        rows.append(
            {
                "refdes": r.get("refdes"),
                "x": f"{5.0:.2f}",
                "y": f"{10.0 * i:.2f}",
                "rotation": "0",
                "footprint": r.get("footprint", ""),
                "value": r.get("value", ""),
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # write atomically to avoid races where other hooks read a partial file
    fd, tmp_path = tempfile.mkstemp(
        prefix="placement-",
        dir=str(out_path.parent),
    )
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "refdes",
                    "x",
                    "y",
                    "rotation",
                    "footprint",
                    "value",
                ],
            )
            writer.writeheader()
            for r in rows:
                r.setdefault("value", "")
                writer.writerow(r)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, out_path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
    print(f"Wrote placement to {out_path}")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(
        description="Generate placement CSV from BOM CSV",
    )
    p.add_argument(
        "--bom",
        type=pathlib.Path,
        help="input BOM CSV path",
        default=None,
    )
    p.add_argument(
        "--out",
        type=pathlib.Path,
        help="output placement CSV path",
        default=None,
    )
    args = p.parse_args()

    repo_root = pathlib.Path(__file__).resolve().parents[2]
    if args.bom is None:
        bom = repo_root / "tools" / "output" / "bom.csv"
    else:
        bom = args.bom
    if args.out is None:
        out = repo_root / "tools" / "output" / "placement.csv"
    else:
        out = args.out
    main(bom, out)
