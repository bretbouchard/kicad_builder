#!/usr/bin/env python3
"""
Test for variant/template generation (e.g., 8x16 grid).
"""

import subprocess
from pathlib import Path


def test_generate_8x16_variant():
    """Run generators for the 8x16 variant and check outputs."""
    project_name = "example_variant_8x16"
    # Run the main generators with the variant project name
    scripts = [
        "power_sheet.py",
        "mcu_sheet.py",
        "touch_sheet.py",
        "led_sheet.py",
        "io_sheet.py",
        "root_schematic.py",
    ]
    for script in scripts:
        result = subprocess.run(
            ["python3", f"hardware/projects/led_touch_grid/gen/{script}", project_name], capture_output=True, text=True
        )
        assert result.returncode == 0, f"{script} failed for {project_name}: {result.stderr}"

    # Check for expected output files for the variant
    expected_files = [
        f"out/{project_name}/power/{project_name}_power_hier.kicad_sch",
        f"out/{project_name}/mcu/{project_name}_mcu_hier.kicad_sch",
        f"out/{project_name}/touch/{project_name}_touch_hier.kicad_sch",
        f"out/{project_name}/led/{project_name}_led_hier.kicad_sch",
        f"out/{project_name}/io/{project_name}_io_hier.kicad_sch",
        f"out/{project_name}/root/{project_name}_root.kicad_sch",
    ]
    for path in expected_files:
        assert Path(path).exists(), f"{path} not generated for variant"
