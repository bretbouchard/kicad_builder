"""Generate hierarchical KiCad schematic for button grid project."""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import os
from skidl import Part, config  # type: ignore[import]
from typing import Optional

# SKiDL configuration


def create_power_sheet() -> Optional[str]:
    """Generate power distribution sheet with PWR_FLAG"""
    try:
        # Configure symbol library from vendor directory
        # Configure library path to vendor directory
        lib_dir = Path("/Users/bretbouchard/apps/buttons/tools/vendor_symbols")
        symbol_table = lib_dir / "sym-lib-table"

        # Print debug information
        print(f"Loading symbols from: {lib_dir}")
        print(f"Symbol table exists: {symbol_table.exists()}")
        print(f"Symbol table contents: {symbol_table.read_text()}")

        # For KiCad 9 compatibility
        config.lib_search_paths = [
            str(lib_dir),
            os.getenv("KICAD9_SYMBOL_DIR"),
        ]

        Part(
            lib="REPO-Device",  # Matches actual library name in sym-lib-table
            name="PWR_FLAG",
            libpath=("/Users/bretbouchard/apps/buttons/tools/vendor_symbols/" "REPO-Device.lib"),
            footprint="",
        )
        # generate_netlist expects a board or list of parts; return a string
        # placeholder path for the sheet. Keeping simple to avoid runtime-only
        # interactions in test environments.
        return "(sheet pwr_flag)"
    except Exception as e:
        print(f"Error creating power sheet: {e}")
        return None


def generate_schematic() -> Optional[str]:  # Correct return type
    """Main schematic generation workflow with DAID metadata"""
    # Create schematic structure
    power_sheet = create_power_sheet()
    if not power_sheet:
        return None  # Explicit return on error

    # Build main schematic
    schematic = f"""(kicad_sch (version 20211014) (generator skidl)
        {power_sheet}
        (sheet (at 0 0) (size 4000 3000)
            (property "Title" "Main Board" (at 0 500))
        )
    )"""

    # Write outputs
    out_dir = Path("kicad")
    out_dir.mkdir(exist_ok=True)
    (out_dir / "root.kicad_sch").write_text(schematic)

    # Generate DAID metadata
    daid = {
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),  # noqa: E501
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kicad_version": "9.0",
        "generator_version": "1.0",
    }
    (out_dir / "daid.json").write_text(json.dumps(daid, indent=2))
    return str(out_dir / "root.kicad_sch")


if __name__ == "__main__":
    generate_schematic()
