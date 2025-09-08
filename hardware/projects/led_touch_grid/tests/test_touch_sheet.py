#!/usr/bin/env python3
"""
Tests for the touch sheet generator (gen/touch_sheet.py).

Covers:
- Successful generation with expected sheet + 64 pad symbols
- Hierarchical pins presence
- Pad count validation failure (simulate missing pad)
"""

from pathlib import Path
import json
import sys
import pytest

# Add project root for imports (tools/)
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools.kicad_helpers import (  # noqa: E402
    Schematic,
    Symbol,
)
from hardware.projects.led_touch_grid.gen.touch_sheet import (  # noqa: E402
    generate_touch_sheet,
    validate_touch_pad_count,
    EXPECTED_PAD_COUNT,
)


def load_hierarchy(project_name: str):
    """Load the hierarchy JSON emitted by generate_touch_sheet."""
    out_dir = Path("out") / project_name / "touch"
    title = f"{project_name}_touch_hier"
    hierarchy_path = out_dir / f"{title}_hierarchy.json"
    missing_msg = f"Hierarchy JSON missing: {hierarchy_path}"
    assert hierarchy_path.exists(), missing_msg
    return json.loads(hierarchy_path.read_text())


class TestTouchSheetGeneratorSuccess:
    def test_generate_touch_sheet_success(self):
        project_name = "led_touch_grid_touch_test"
        generate_touch_sheet(project_name=project_name)

        hierarchy = load_hierarchy(project_name)
        sheets = hierarchy["sheets"]
        assert "touch" in sheets, "Touch sheet missing in hierarchy export"

        touch_symbols = sheets["touch"]["symbols"]
        pads = [s for s in touch_symbols if s.get("name") == "PAD" and (s.get("ref") or "").startswith("P")]
        assert len(pads) == EXPECTED_PAD_COUNT, f"Expected {EXPECTED_PAD_COUNT} pads, found {len(pads)}"

        # Hierarchical pins
        pins = sheets["touch"]["hierarchical_pins"]
        pin_names = {p["name"] for p in pins}
        expected = {"TOUCH_GRID_BUS", "3.3V_IN", "GND"}
        missing = expected - pin_names
        assert not missing, f"Missing hierarchical pins: {missing}"

    def test_validate_pad_count_passes(self):
        sch = Schematic("touch_ok")
        # Add dummy 64 pad symbols
        for i in range(1, EXPECTED_PAD_COUNT + 1):
            sch.add_symbol(
                Symbol(
                    lib="Device",
                    name="PAD",
                    ref=f"P{i}",
                    value="TouchPad",
                )
            )
        # Should not raise
        validate_touch_pad_count(sch)


class TestTouchSheetFailureCases:
    def test_validate_pad_count_failure(self):
        sch = Schematic("touch_missing")
        # Intentionally add one fewer pad
        for i in range(1, EXPECTED_PAD_COUNT):
            sch.add_symbol(
                Symbol(
                    lib="Device",
                    name="PAD",
                    ref=f"P{i}",
                    value="TouchPad",
                )
            )
        with pytest.raises(ValueError, match="Touch pad count mismatch"):
            validate_touch_pad_count(sch)


# Run directly
if __name__ == "__main__":
    pytest.main([__file__, "-q"])
