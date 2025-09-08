#!/usr/bin/env python3
"""
Smoke test for all generator CLI entrypoints.
"""

import subprocess


def test_all_generators_cli_smoke():
    """Run each generator script directly and check for successful execution."""
    scripts = [
        "power_sheet.py",
        "mcu_sheet.py",
        "touch_sheet.py",
        "led_sheet.py",
        "io_sheet.py",
        "root_schematic.py",
        "netlist.py",
        "pcb_placement.py",
        "touch_simulation.py",
    ]
    for script in scripts:
        result = subprocess.run(
            ["python3", f"hardware/projects/led_touch_grid/gen/{script}"], capture_output=True, text=True
        )
        assert result.returncode == 0, f"{script} CLI failed: {result.stderr}"
