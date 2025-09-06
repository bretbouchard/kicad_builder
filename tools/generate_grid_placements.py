#!/usr/bin/env python3
"""
Generate placement CSV and BOM for an array of tiles, each containing a grid of pads with LEDs.

Output files (by default):
- projects/button_bar/placements/grid_placements.csv
- projects/button_bar/placements/generated_bom.csv
- projects/button_bar/placements/ref_mapping.json

This is a deterministic generator that assigns reference designators and XY positions
in millimeters. It does NOT modify any KiCad files. Use the companion script
`kicad_place_from_csv.py` to apply placements into a KiCad board (run inside KiCad's
Python environment or with kicad-cli if you have KiCad's Python available).

Usage:
  python tools/generate_grid_placements.py --help

Assumptions (reasonable defaults):
- Each "tile" contains a grid of touch pads (default 8x8 => 64 pads) and 4 LEDs per pad
  arranged 2x2 (=> 256 LEDs per tile).
- Spacing and offsets are configurable in mm.

"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from typing import List, Tuple

OUT_DIR = "projects/button_bar/placements"


@dataclass
class LEDPlacement:
    ref: str
    footprint: str
    x_mm: float
    y_mm: float
    rotation: float = 0.0
    layer: str = "F.Cu"


def ensure_outdir():
    os.makedirs(OUT_DIR, exist_ok=True)


def generate_tile(
    tile_idx: int,
    tile_origin_x: float,
    tile_origin_y: float,
    pads_x: int,
    pads_y: int,
    pad_pitch: float,
    leds_per_pad: int,
    led_pattern: Tuple[int, int],
    led_spacing: float,
    led_footprint: str,
    start_led_index: int,
) -> Tuple[List[LEDPlacement], int]:
    """Return placements for one tile and the next start index."""
    placements: List[LEDPlacement] = []
    pad_cols = pads_x
    pad_rows = pads_y
    # leds_per_pad assumed to equal led_pattern[0]*led_pattern[1]
    led_cols, led_rows = led_pattern

    idx = start_led_index
    for py in range(pad_rows):
        for px in range(pad_cols):
            pad_center_x = tile_origin_x + px * pad_pitch
            pad_center_y = tile_origin_y + py * pad_pitch
            # arrange leds in small grid centered on pad_center
            total_w = (led_cols - 1) * led_spacing
            total_h = (led_rows - 1) * led_spacing
            origin_x = pad_center_x - total_w / 2.0
            origin_y = pad_center_y - total_h / 2.0

            for ly in range(led_rows):
                for lx in range(led_cols):
                    x = origin_x + lx * led_spacing
                    y = origin_y + ly * led_spacing
                    ref = f"LED{idx}"
                    placements.append(
                        LEDPlacement(ref=ref, footprint=led_footprint, x_mm=round(x, 3), y_mm=round(y, 3))
                    )
                    idx += 1

    return placements, idx


def generate_grid(
    out_csv: str | None = None,
    out_bom: str | None = None,
    out_map: str | None = None,
    tiles_x: int = 1,
    tiles_y: int = 1,
    tile_spacing_x: float = 100.0,
    tile_spacing_y: float = 100.0,
    pads_x: int = 8,
    pads_y: int = 8,
    pad_pitch: float = 20.0,
    leds_per_pad: int = 4,
    led_pattern: Tuple[int, int] = (2, 2),
    led_spacing: float = 3.5,
    led_footprint: str = "LED_APA-102-2020-256-8:APA102_5050",
):
    ensure_outdir()
    out_csv = out_csv or os.path.join(OUT_DIR, "grid_placements.csv")
    out_bom = out_bom or os.path.join(OUT_DIR, "generated_bom.csv")
    out_map = out_map or os.path.join(OUT_DIR, "ref_mapping.json")

    placements: List[LEDPlacement] = []
    ref_idx = 1
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            origin_x = tx * tile_spacing_x
            origin_y = ty * tile_spacing_y
            tile_places, ref_idx = generate_tile(
                tile_idx=ty * tiles_x + tx,
                tile_origin_x=origin_x,
                tile_origin_y=origin_y,
                pads_x=pads_x,
                pads_y=pads_y,
                pad_pitch=pad_pitch,
                leds_per_pad=leds_per_pad,
                led_pattern=led_pattern,
                led_spacing=led_spacing,
                led_footprint=led_footprint,
                start_led_index=ref_idx,
            )
            placements.extend(tile_places)

    # Write placements CSV
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "ref",
                "footprint",
                "x_mm",
                "y_mm",
                "rotation",
                "layer",
            ]
        )
        for p in placements:
            w.writerow(
                [
                    p.ref,
                    p.footprint,
                    p.x_mm,
                    p.y_mm,
                    p.rotation,
                    p.layer,
                ]
            )

    # Minimal BOM (counts footprint types)
    counts: dict[str, int] = {}
    for p in placements:
        counts[p.footprint] = counts.get(p.footprint, 0) + 1

    with open(out_bom, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["footprint", "quantity"])
        for fp, q in sorted(counts.items()):
            w.writerow([fp, q])

    # Write ref mapping JSON
    mapping: dict[str, dict[str, object]] = {
        p.ref: {
            "footprint": p.footprint,
            "x_mm": p.x_mm,
            "y_mm": p.y_mm,
            "rotation": p.rotation,
        }
        for p in placements
    }
    with open(out_map, "w") as f:
        json.dump(mapping, f, indent=2)

    print(f"Wrote placements CSV: {out_csv}")
    print(f"Wrote BOM summary: {out_bom}")
    print(f"Wrote ref mapping JSON: {out_map}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=("Generate grid placements for LED/tile arrays"))
    parser.add_argument("--tiles-x", type=int, default=1)
    parser.add_argument("--tiles-y", type=int, default=1)
    parser.add_argument("--tile-spacing-x", type=float, default=100.0)
    parser.add_argument("--tile-spacing-y", type=float, default=100.0)
    parser.add_argument("--pads-x", type=int, default=8)
    parser.add_argument("--pads-y", type=int, default=8)
    parser.add_argument("--pad-pitch", type=float, default=20.0)
    parser.add_argument("--led-spacing", type=float, default=3.5)
    parser.add_argument(
        "--led-pattern",
        type=int,
        nargs=2,
        default=(2, 2),
        help="cols rows per pad",
    )
    parser.add_argument(
        "--led-footprint",
        type=str,
        default=("LED_APA-102-2020-256-8:APA102_5050"),
    )
    parser.add_argument("--out-csv", type=str)
    parser.add_argument("--out-bom", type=str)
    parser.add_argument("--out-map", type=str)

    args = parser.parse_args()
    generate_grid(
        out_csv=args.out_csv,
        out_bom=args.out_bom,
        out_map=args.out_map,
        tiles_x=args.tiles_x,
        tiles_y=args.tiles_y,
        tile_spacing_x=args.tile_spacing_x,
        tile_spacing_y=args.tile_spacing_y,
        pads_x=args.pads_x,
        pads_y=args.pads_y,
        pad_pitch=args.pad_pitch,
        leds_per_pad=args.led_pattern[0] * args.led_pattern[1],
        led_pattern=tuple(args.led_pattern),
        led_spacing=args.led_spacing,
        led_footprint=args.led_footprint,
    )
