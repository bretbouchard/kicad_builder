#!/usr/bin/env python3
"""
Smoke tests for LED Touch Grid project.

Basic functionality tests to ensure the project structure and generators
are working correctly. These tests run quickly and verify the basic
infrastructure is in place.

Requirements met:
- Basic project structure validation (Req 15.1)
- Generator import and execution tests
- File creation and content validation
- Quick CI verification tests

Usage: pytest hardware/projects/led_touch_grid/tests/test_smoke.py -v
"""

import sys
from pathlib import Path

import pytest

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


class TestProjectStructure:
    """Test basic project structure and file existence."""

    def test_project_directory_exists(self):
        """Test that the project directory exists."""
        project_path = Path(".")
        assert project_path.exists(), f"Project directory {project_path} does not exist"

    def test_generator_files_exist(self):
        """Test that all generator files exist."""
        gen_dir = Path("gen")
        assert gen_dir.exists(), "Generator directory does not exist"

        expected_files = [
            "netlist.py",
            "power_sheet.py",
            "mcu_sheet.py",
            "touch_sheet.py",
            "led_sheet.py",
            "io_sheet.py",
            "root_schematic.py",
        ]

        for file_name in expected_files:
            file_path = gen_dir / file_name
            assert file_path.exists(), f"Generator file {file_path} does not exist"

    def test_test_files_exist(self):
        """Test that test files exist."""
        test_dir = Path("tests")
        assert test_dir.exists(), "Test directory does not exist"

        expected_files = [
            "test_smoke.py",
            "test_erc_suite.py",
        ]

        for file_name in expected_files:
            file_path = test_dir / file_name
            assert file_path.exists(), f"Test file {file_path} does not exist"

    def test_makefile_exists(self):
        """Test that Makefile exists."""
        makefile_path = Path("Makefile")
        assert makefile_path.exists(), "Makefile does not exist"

    def test_readme_exists(self):
        """Test that README exists."""
        readme_path = Path("README.md")
        assert readme_path.exists(), "README.md does not exist"


class TestGeneratorImports:
    """Test that all generators can be imported."""

    def test_netlist_import(self):
        """Test netlist generator import."""
        try:
            from hardware.projects.led_touch_grid.gen.netlist import generate_netlist

            assert callable(generate_netlist), "generate_netlist is not callable"
        except ImportError as e:
            pytest.fail(f"Failed to import netlist generator: {e}")

    def test_power_sheet_import(self):
        """Test power sheet generator import."""
        try:
            from hardware.projects.led_touch_grid.gen.power_sheet import (
                generate_power_sheet,
            )

            assert callable(generate_power_sheet), "generate_power_sheet is not callable"
        except ImportError as e:
            pytest.fail(f"Failed to import power sheet generator: {e}")

    def test_mcu_sheet_import(self):
        """Test MCU sheet generator import."""
        try:
            from hardware.projects.led_touch_grid.gen.mcu_sheet import (
                generate_mcu_sheet,
            )

            assert callable(generate_mcu_sheet), "generate_mcu_sheet is not callable"
        except ImportError as e:
            pytest.fail(f"Failed to import MCU sheet generator: {e}")

    def test_touch_sheet_import(self):
        """Test touch sheet generator import."""
        try:
            from hardware.projects.led_touch_grid.gen.touch_sheet import (
                generate_touch_sheet,
            )

            assert callable(generate_touch_sheet), "generate_touch_sheet is not callable"
        except ImportError as e:
            pytest.fail(f"Failed to import touch sheet generator: {e}")

    def test_led_sheet_import(self):
        """Test LED sheet generator import."""
        try:
            from hardware.projects.led_touch_grid.gen.led_sheet import (
                generate_led_sheet,
            )

            assert callable(generate_led_sheet), "generate_led_sheet is not callable"
        except ImportError as e:
            pytest.fail(f"Failed to import LED sheet generator: {e}")

    def test_io_sheet_import(self):
        """Test I/O sheet generator import."""
        try:
            from hardware.projects.led_touch_grid.gen.io_sheet import generate_io_sheet

            assert callable(generate_io_sheet), "generate_io_sheet is not callable"
        except ImportError as e:
            pytest.fail(f"Failed to import I/O sheet generator: {e}")

    def test_root_schematic_import(self):
        """Test root schematic generator import."""
        try:
            from hardware.projects.led_touch_grid.gen.root_schematic import (
                generate_root_schematic,
            )

            assert callable(generate_root_schematic), "generate_root_schematic is not callable"
        except ImportError as e:
            pytest.fail(f"Failed to import root schematic generator: {e}")


class TestBasicFunctionality:
    """Test basic functionality of generators."""

    def test_makefile_targets(self):
        """Test that Makefile has expected targets."""
        makefile_path = Path("Makefile")
        content = makefile_path.read_text()

        expected_targets = [
            "all",
            "gen",
            "gen-power",
            "gen-mcu",
            "gen-touch",
            "gen-led",
            "gen-io",
            "gen-root",
            "clean",
            "test",
            "verify",
            "lint",
            "format",
            "help",
        ]

        for target in expected_targets:
            assert f"{target}:" in content, f"Makefile target {target} not found"

    def test_readme_content(self):
        """Test that README has expected content."""
        readme_path = Path("README.md")
        content = readme_path.read_text()

        expected_sections = [
            "LED Touch Grid Project",
            "Overview",
            "Architecture",
            "Build Instructions",
            "Project Structure",
            "Technical Specifications",
            "Design Goals",
        ]

        for section in expected_sections:
            assert section in content, f"README section {section} not found"

    def test_kicad_helpers_import(self):
        """Test that kicad_helpers can be imported."""
        try:
            from tools.kicad_helpers import (
                Schematic,
            )

            # Test basic instantiation
            sch = Schematic("test")
            assert sch.title == "test"
        except ImportError as e:
            pytest.fail(f"Failed to import kicad_helpers: {e}")


class TestConfiguration:
    """Test project configuration and constants."""

    def test_grid_constants(self):
        """Test that grid constants are properly defined."""
        from hardware.projects.led_touch_grid.gen.touch_sheet import (
            GRID_SIZE,
            PAD_SIZE_MM,
        )

        assert GRID_SIZE == (8, 8), f"Expected GRID_SIZE=(8,8), got {GRID_SIZE}"
        assert PAD_SIZE_MM == (19.0, 19.0), f"Expected PAD_SIZE_MM=(19.0,19.0), got {PAD_SIZE_MM}"

    def test_led_constants(self):
        """Test that LED constants are properly defined."""
        from hardware.projects.led_touch_grid.gen.led_sheet import (
            CONFIG_CHAINED,
            CONFIG_PARALLEL,
            GRID_SIZE,
            LEDS_PER_PAD,
            TOTAL_LEDS,
        )

        assert GRID_SIZE == (8, 8), f"Expected GRID_SIZE=(8,8), got {GRID_SIZE}"
        assert LEDS_PER_PAD == 4, f"Expected LEDS_PER_PAD=4, got {LEDS_PER_PAD}"
        assert TOTAL_LEDS == 256, f"Expected TOTAL_LEDS=256, got {TOTAL_LEDS}"
        assert CONFIG_PARALLEL == "parallel", f"Expected CONFIG_PARALLEL='parallel', got {CONFIG_PARALLEL}"
        assert CONFIG_CHAINED == "chained", f"Expected CONFIG_CHAINED='chained', got {CONFIG_CHAINED}"

    def test_power_constants(self):
        """Test that power constants are properly defined."""
        from hardware.projects.led_touch_grid.gen.power_sheet import LDO_AT, V5_INPUT_AT

        assert V5_INPUT_AT == (50.0, 50.0), f"Expected V5_INPUT_AT=(50.0,50.0), got {V5_INPUT_AT}"
        assert LDO_AT == (100.0, 50.0), f"Expected LDO_AT=(100.0,50.0), got {LDO_AT}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
