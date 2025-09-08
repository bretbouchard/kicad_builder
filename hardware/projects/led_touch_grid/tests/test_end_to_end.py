#!/usr/bin/env python3
"""
End-to-end tests for LED Touch Grid project.

Runs the full generation pipeline and validates output artifacts.
"""

import subprocess
from pathlib import Path


def test_run_pcb_placement():
    """Run PCB placement generator and check output CSVs."""
    result = subprocess.run(
        ["python3", "hardware/projects/led_touch_grid/gen/pcb_placement.py"], capture_output=True, text=True
    )
    assert result.returncode == 0, f"pcb_placement.py failed: {result.stderr}"
    led_csv = Path("out/led_touch_grid/placement/led_grid.csv")
    touch_csv = Path("out/led_touch_grid/placement/touch_grid.csv")
    assert led_csv.exists(), "LED grid CSV not generated"
    assert touch_csv.exists(), "Touch grid CSV not generated"


def test_run_touch_simulation():
    """Run touch simulation and check for successful execution."""
    result = subprocess.run(
        ["python3", "hardware/projects/led_touch_grid/gen/touch_simulation.py"], capture_output=True, text=True
    )
    assert result.returncode == 0, f"touch_simulation.py failed: {result.stderr}"


def test_run_all_generators():
    """Run all sheet generators and check for output files."""
    generators = [
        ("power_sheet.py", "out/led_touch_grid/power/led_touch_grid_power_hier.kicad_sch"),
        ("mcu_sheet.py", "out/led_touch_grid/mcu/led_touch_grid_mcu_hier.kicad_sch"),
        ("touch_sheet.py", "out/led_touch_grid/touch/led_touch_grid_touch_hier.kicad_sch"),
        ("led_sheet.py", "out/led_touch_grid/led/led_touch_grid_led_hier.kicad_sch"),
        ("io_sheet.py", "out/led_touch_grid/io/led_touch_grid_io_hier.kicad_sch"),
        ("root_schematic.py", "out/led_touch_grid/root/led_touch_grid_root.kicad_sch"),
    ]
    for script, output in generators:
        result = subprocess.run(
            ["python3", f"hardware/projects/led_touch_grid/gen/{script}"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"{script} failed: {result.stderr}"
        assert Path(output).exists(), f"{output} not generated"
