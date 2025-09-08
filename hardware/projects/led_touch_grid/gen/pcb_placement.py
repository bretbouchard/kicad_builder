#!/usr/bin/env python3
"""
Automated PCB Grid Placement System for LED Touch Grid

Implements:
- CSV-based grid placement with 20mm spacing and 0.01mm tolerance
- Support for 16x16 LED and 8x8 touch pad grid alignment
- Placement validation and conflict detection
- Integration with tools/generate_grid_placements.py conventions

Outputs:
- out/led_touch_grid/placement/led_grid.csv
- out/led_touch_grid/placement/touch_grid.csv

"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

LED_GRID_SIZE = 16
TOUCH_GRID_SIZE = 8
LED_SPACING = 20.0
TOUCH_SPACING = 20.0
TOLERANCE = 0.01


class PCBPlacementBuilder:
    """
    Automated PCB grid placement system for LED and touch grids.
    """

    def __init__(self, project_name: str = "led_touch_grid", grid_size: int = 8):
        self.grid_size = grid_size
        self.project_name = project_name
        self.out_dir = Path("out") / project_name / "placement"
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.led_grid = []
        self.touch_grid = []

    def _generate_led_grid(self):
        """Generate placement CSV for 16x16 LED grid."""
        for row in range(LED_GRID_SIZE):
            for col in range(LED_GRID_SIZE):
                ref = f"LED{row*LED_GRID_SIZE+col+1:03d}"
                x = col * LED_SPACING
                y = row * LED_SPACING
                self.led_grid.append(
                    {
                        "ref": ref,
                        "footprint": "LED_APA-102-2020-256-8:APA102_5050",
                        "x_mm": round(x, 3),
                        "y_mm": round(y, 3),
                        "rotation": 0.0,
                        "layer": "F.Cu",
                    }
                )

    def _generate_touch_grid(self):
        """Generate placement CSV for 8x8 touch pad grid."""
        TOUCH_START_X = 50.0
        TOUCH_START_Y = 50.0
        for row in range(TOUCH_GRID_SIZE):
            for col in range(TOUCH_GRID_SIZE):
                ref = f"TP{row*TOUCH_GRID_SIZE+col+1:02d}"
                x = TOUCH_START_X + col * TOUCH_SPACING
                y = TOUCH_START_Y + row * TOUCH_SPACING
                self.touch_grid.append(
                    {
                        "ref": ref,
                        "footprint": "Custom:Touch_Pad_19x19mm",
                        "x_mm": round(x, 3),
                        "y_mm": round(y, 3),
                        "rotation": 0.0,
                        "layer": "F.Cu",
                    }
                )

    def _validate_placement(self):
        """Validate placement accuracy and detect conflicts."""
        # Check for duplicate refs
        refs = set()
        for item in self.led_grid + self.touch_grid:
            if item["ref"] in refs:
                raise ValueError(f"Duplicate reference designator: {item['ref']}")
            refs.add(item["ref"])
        # Check for overlapping positions (within tolerance)
        positions = {}
        for item in self.led_grid + self.touch_grid:
            pos = (round(item["x_mm"], 2), round(item["y_mm"], 2))
            if pos in positions:
                raise ValueError(f"Placement conflict at {pos}: {item['ref']} and {positions[pos]}")
            positions[pos] = item["ref"]

    def build(self):
        self._generate_led_grid()
        self._generate_touch_grid()
        self._validate_placement()
        # Write placement CSVs
        led_csv = self.out_dir / "led_grid.csv"
        touch_csv = self.out_dir / "touch_grid.csv"
        with open(led_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["ref", "footprint", "x_mm", "y_mm", "rotation", "layer"])
            w.writeheader()
            for row in self.led_grid:
                w.writerow(row)
        with open(touch_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["ref", "footprint", "x_mm", "y_mm", "rotation", "layer"])
            w.writeheader()
            for row in self.touch_grid:
                w.writerow(row)
        print(f"Wrote LED grid CSV: {led_csv}")
        print(f"Wrote touch grid CSV: {touch_csv}")


def generate_pcb_placement(project_name: str = "led_touch_grid") -> None:
    builder = PCBPlacementBuilder(project_name=project_name)
    builder.build()
    print("PCB placement generated.")


if __name__ == "__main__":
    generate_pcb_placement()
