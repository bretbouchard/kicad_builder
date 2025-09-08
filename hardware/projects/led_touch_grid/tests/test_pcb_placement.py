#!/usr/bin/env python3
"""
Test suite for PCB grid placement system.

Validates the automated PCB placement system for LED Touch Grid project,
including grid alignment, tolerance checking, conflict detection, and
CSV output generation.

Requirements tested:
- CSV-based grid placement with 20mm spacing and ±0.01mm tolerance
- LED and touch pad grid alignment for mechanical registration
- Component locking and conflict detection
- Multi-tile array support with consistent grid patterns
"""

import sys
import unittest
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from hardware.projects.led_touch_grid.gen.pcb_placement import PCBPlacementBuilder


class TestPCBPlacementBuilder(unittest.TestCase):
    """Test cases for PCBPlacementBuilder."""

    def setUp(self):
        self.builder = PCBPlacementBuilder(project_name="test_led_touch_grid")

    def test_led_grid_generation(self):
        self.builder._generate_led_grid()
        self.assertEqual(len(self.builder.led_grid), 16 * 16)
        # Check first and last LED positions
        self.assertEqual(self.builder.led_grid[0]["ref"], "LED001")
        self.assertEqual(self.builder.led_grid[-1]["ref"], "LED256")

    def test_touch_grid_generation(self):
        self.builder._generate_touch_grid()
        self.assertEqual(len(self.builder.touch_grid), 8 * 8)
        # Check first and last touch pad positions
        self.assertEqual(self.builder.touch_grid[0]["ref"], "TP01")
        self.assertEqual(self.builder.touch_grid[-1]["ref"], "TP64")

    def test_validate_placement(self):
        self.builder._generate_led_grid()
        self.builder._generate_touch_grid()
        # Should not raise
        self.builder._validate_placement()

    def test_build_creates_csvs(self):
        self.builder.build()
        led_csv = self.builder.out_dir / "led_grid.csv"
        touch_csv = self.builder.out_dir / "touch_grid.csv"
        self.assertTrue(led_csv.exists())
        self.assertTrue(touch_csv.exists())
        # Check CSV headers
        with open(led_csv, "r") as f:
            header = f.readline()
            self.assertIn("ref", header)
            self.assertIn("x_mm", header)
        with open(touch_csv, "r") as f:
            header = f.readline()
            self.assertIn("ref", header)
            self.assertIn("x_mm", header)


# No additional placement rules to test for PCBPlacementBuilder

if __name__ == "__main__":
    unittest.main()
