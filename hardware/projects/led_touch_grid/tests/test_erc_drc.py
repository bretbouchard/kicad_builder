#!/usr/bin/env python3
"""
Test for ERC/DRC error handling in the generator pipeline.
"""

import subprocess
from pathlib import Path


def test_missing_decoupling_cap_raises_error(tmp_path):
    """
    Remove a required decoupling capacitor from the MCU sheet and verify ERC fails.
    """
    # Copy the mcu_sheet.py to a temp file and patch it to remove decoupling caps
    orig = Path("hardware/projects/led_touch_grid/gen/mcu_sheet.py")
    test_file = tmp_path / "mcu_sheet_nodecap.py"
    content = orig.read_text()
    # Remove all lines that add 100nF decoupling caps
    patched = []
    for line in content.splitlines():
        if "100nF 50V" in line:
            continue
        patched.append(line)
    test_file.write_text("\n".join(patched))

    # Run the patched generator
    result = subprocess.run(["python3", str(test_file)], capture_output=True, text=True)
    # Should fail with a decoupling error
    assert result.returncode != 0, "ERC should fail when decoupling caps are missing"
    assert (
        "decoupling" in result.stderr.lower() or "decoupling" in result.stdout.lower()
    ), "Missing decoupling error not reported"
