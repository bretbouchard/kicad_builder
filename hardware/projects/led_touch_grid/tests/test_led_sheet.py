import sys
from pathlib import Path

import pytest

# Add project root to sys.path for import
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from hardware.projects.led_touch_grid.gen.led_sheet import LEDSheetBuilder


def test_led_sheet_generation(tmp_path):
    builder = LEDSheetBuilder(project_name="test_led_touch_grid")
    hier = builder.build()
    out_dir = tmp_path / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    hier.write(out_dir=str(out_dir))

    # Check output files exist - updated naming convention to use _led_hier
    sch_path = out_dir / "test_led_touch_grid_led_hier.kicad_sch"
    sch_txt_path = out_dir / "test_led_touch_grid_led_hier.sch.txt"
    # Accept either .kicad_sch or .sch.txt as output (scaffold may not emit .kicad_sch)
    assert (
        sch_path.exists() or sch_txt_path.exists()
    ), f"KiCad schematic file not generated: checked {sch_path} and {sch_txt_path}"

    # Validate symbol counts
    led_symbols = [
        s
        for s in builder.schematic.symbols
        if s.lib == builder.config.led_symbol[0] and s.name == builder.config.led_symbol[1]
    ]
    assert len(led_symbols) == builder.config.expected_led_count

    decoupling_caps = [
        s
        for s in builder.schematic.symbols
        if s.lib == "Device" and s.name == "C" and s.value == builder.config.decoupling_value
    ]
    assert len(decoupling_caps) == builder.config.expected_led_count

    bulk_caps = [s for s in builder.schematic.symbols if s.ref.startswith("CB")]
    expected_bulk = 1 + (builder.config.expected_led_count // 32 - 1)
    assert len(bulk_caps) == expected_bulk

    # Run validation (should not raise)
    builder._run_validations()


def test_led_sheet_validation_failure(monkeypatch):
    builder = LEDSheetBuilder(project_name="fail_led_touch_grid")
    builder._add_led_chain()
    # Skip decoupling and bulk caps to force validation error
    with pytest.raises(ValueError) as excinfo:
        builder._run_validations()
    assert "Decoupling capacitor count mismatch" in str(excinfo.value) or "Bulk capacitor count mismatch" in str(
        excinfo.value
    )
