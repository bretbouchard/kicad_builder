#!/usr/bin/env python3
"""
Test for netlist generation and output validation.
"""

import subprocess
from pathlib import Path


def test_run_netlist_generator():
    """Run netlist generator and check output files."""
    result = subprocess.run(
        ["python3", "hardware/projects/led_touch_grid/gen/netlist.py"], capture_output=True, text=True
    )
    assert result.returncode == 0, f"netlist.py failed: {result.stderr}"
    netlist_file = Path("out/led_touch_grid/netlist/led_touch_grid.net")
    stats_file = Path("out/led_touch_grid/netlist/led_touch_grid_stats.txt")
    assert netlist_file.exists(), "Netlist file not generated"
    assert stats_file.exists(), "Netlist stats file not generated"

    # Optionally, check for expected content in stats file
    stats_content = stats_file.read_text()
    assert "Netlist Statistics for led_touch_grid" in stats_content
    assert "Power nets:" in stats_content
    assert "GPIO nets:" in stats_content
    assert "SPI nets:" in stats_content
    assert "I2C nets:" in stats_content
    assert "Control nets:" in stats_content
    assert "Total components:" in stats_content
    assert "Total nets:" in stats_content
