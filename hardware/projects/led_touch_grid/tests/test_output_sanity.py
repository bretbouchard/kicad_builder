#!/usr/bin/env python3
"""
Sanity check for generated schematic/netlist content.
"""

import json
from pathlib import Path


def test_schematic_symbol_counts():
    """
    Check that the generated touch schematic contains 64 pads,
    and the MCU schematic contains 2 RP2040 MCUs.
    """
    # Touch schematic summary
    touch_summary = Path("out/led_touch_grid/touch/led_touch_grid_touch_summary.json")
    assert touch_summary.exists(), "Touch schematic summary not found"
    touch_data = json.loads(touch_summary.read_text())
    pad_syms = [s for s in touch_data["symbols"] if s["name"] == "PAD"]
    assert len(pad_syms) == 64, f"Expected 64 touch pads, found {len(pad_syms)}"

    # MCU schematic summary
    mcu_summary = Path("out/led_touch_grid/mcu/led_touch_grid_mcu_summary.json")
    assert mcu_summary.exists(), "MCU schematic summary not found"
    mcu_data = json.loads(mcu_summary.read_text())
    mcu_syms = [s for s in mcu_data["symbols"] if "RP2040" in s["name"]]
    assert len(mcu_syms) == 2, f"Expected 2 RP2040 MCUs, found {len(mcu_syms)}"


def test_led_count_in_led_schematic():
    """
    Check that the generated LED schematic contains 256 APA102 LEDs.
    """
    led_summary = Path("out/led_touch_grid/led/led_touch_grid_led_summary.json")
    assert led_summary.exists(), "LED schematic summary not found"
    led_data = json.loads(led_summary.read_text())
    led_syms = [s for s in led_data["symbols"] if "APA102" in s["name"]]
    assert len(led_syms) == 256, f"Expected 256 APA102 LEDs, found {len(led_syms)}"


# Checksum verification test
def test_generated_file_checksums():
    import hashlib

    with open("tests/reference/led_grid.sha256") as f:
        expected = f.read().strip()
    actual = hashlib.sha256(open("out/led_touch_grid/placement/led_grid.csv", "rb").read()).hexdigest()
    assert actual == expected, "LED grid checksum mismatch. Expected: {expected}, Got: {actual}"
