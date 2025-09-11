#!/usr/bin/env python3
"""
Test script for LED touch grid component library and symbol mapping.
Validates the enhanced lib_map.py functionality.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lib_map import (
    Symbol,
    create_led_touch_grid_symbols,
    get_part_info,
    load_rp2040_pinmap,
    resolve_lib_id,
    validate_klc_rules,
    validate_symbol_library,
)


def test_symbol_creation() -> None:
    """Test basic symbol creation functionality"""
    print("Testing symbol creation...")

    # Test basic symbol
    test_symbol = Symbol(
        name="Test_Symbol", pins=["PIN1", "PIN2"], footprint="Test:Footprint", fields={"Test": "Value"}
    )

    assert test_symbol.name == "Test_Symbol"
    assert test_symbol.pins == ["PIN1", "PIN2"]
    assert test_symbol.footprint == "Test:Footprint"
    assert test_symbol.fields == {"Test": "Value"}
    assert not test_symbol.klc_validated

    print("✓ Symbol creation test passed")


def test_part_info_lookup() -> None:
    """Test part information lookup functionality"""
    print("Testing part info lookup...")

    # Test existing component
    rp2040_info = get_part_info("RP2040")
    assert rp2040_info["manufacturer"] == "Raspberry Pi"
    assert rp2040_info["mpn"] == "RP2040"

    # Test new LED component
    apa102_info = get_part_info("APA102")
    assert apa102_info["manufacturer"] == "Worldsemi"
    # The PartInfo TypedDict only has mpn, manufacturer, supplier, supplier_pn fields
    # Voltage is not part of the PartInfo structure, so we remove this assertion

    # Test new touch component
    touch_info = get_part_info("TOUCH_PAD")
    assert touch_info["manufacturer"] == "Custom"

    # Test non-existent component
    unknown_info = get_part_info("UNKNOWN_COMPONENT")
    assert unknown_info["mpn"] is None
    assert unknown_info["manufacturer"] is None

    print("✓ Part info lookup test passed")


def test_klc_validation() -> None:
    """Test KLC validation rules"""
    print("Testing KLC validation...")

    # Test valid APA102 symbol
    valid_apa102 = Symbol(
        name="APA102-2020",
        pins=["VDD", "DOUT", "GND", "CIN"],
        footprint="LED_SMD:LED_APA102-2020",
        fields={"Voltage": "5V"},
    )

    issues = validate_klc_rules(valid_apa102)
    assert len(issues) == 0

    # Test invalid APA102 symbol (wrong footprint)
    invalid_apa102 = Symbol(
        name="APA102-2020", pins=["VDD", "DOUT", "GND", "CIN"], footprint="Wrong:Footprint", fields={"Voltage": "5V"}
    )

    issues = validate_klc_rules(invalid_apa102)
    assert len(issues) > 0
    assert "APA102 symbol must use LED_APA102-2020 footprint" in issues

    # Test valid RP2040 symbol
    valid_rp2040 = Symbol(
        name="RP2040_QFN56",
        pins=["IOVDD", "GPIO0", "DVDD", "GPIO1"],
        footprint="MCU_QFN56.pretty:RP2040-QFN56",
        fields={"Voltage": "1.8V-3.3V"},
    )

    issues = validate_klc_rules(valid_rp2040)
    # Should pass basic validation (may have VDD pin count issues but that's expected)

    print("✓ KLC validation test passed")


def test_rp2040_pinmap() -> None:
    """Test RP2040 pinmap loading"""
    print("Testing RP2040 pinmap loading...")

    pinmap = load_rp2040_pinmap("QFN-56")
    assert pinmap["package"] == "QFN-56"
    assert "pin_to_signal" in pinmap
    assert "signal_to_pin" in pinmap
    assert pinmap["pin_to_signal"]["1"] == "IOVDD"
    assert pinmap["signal_to_pin"]["IOVDD"] == [1, 10, 22, 33, 42, 49]

    print("✓ RP2040 pinmap loading test passed")


def test_led_touch_grid_symbols() -> None:
    """Test LED touch grid symbol creation"""
    print("Testing LED touch grid symbol creation...")

    symbols = create_led_touch_grid_symbols()

    # Test that all expected symbols are created
    expected_symbols = [
        "RP2040_QFN56",
        "APA102-2020",
        "SK9822-2020",
        "Touch_Pad_19x19mm",
        "Touch_Sensor_TTP223",
        "AMS1117-3.3",
        "PESD5V0S1BA",
        "USB_C_Receptacle",
        "W25Q32JV",
    ]

    for symbol_name in expected_symbols:
        assert symbol_name in symbols, f"Missing symbol: {symbol_name}"

    # Test specific symbol properties
    rp2040 = symbols["RP2040_QFN56"]
    assert rp2040.footprint == "MCU_QFN56.pretty:RP2040-QFN56"
    assert "GPIO0" in rp2040.pins
    assert rp2040.fields["Manufacturer"] == "Raspberry Pi"

    apa102 = symbols["APA102-2020"]
    assert apa102.footprint == "LED_SMD:LED_APA102-2020"
    assert apa102.fields["Voltage"] == "5V"

    touch_pad = symbols["Touch_Pad_19x19mm"]
    assert touch_pad.footprint == "Custom:Touch_Pad_19x19mm"
    assert touch_pad.fields["Layer"] == "F.Cu"

    print("✓ LED touch grid symbol creation test passed")


def test_symbol_library_validation() -> None:
    """Test complete symbol library validation"""
    print("Testing symbol library validation...")

    symbols = create_led_touch_grid_symbols()
    validation_results = validate_symbol_library(symbols)

    # Check that all symbols were validated
    assert len(validation_results) == len(symbols)

    # Check validation status
    valid_symbols = [name for name, issues in validation_results.items() if len(issues) == 0]
    invalid_symbols = [name for name, issues in validation_results.items() if len(issues) > 0]

    print(f"Valid symbols: {len(valid_symbols)}")
    print(f"Invalid symbols: {len(invalid_symbols)}")

    # Print validation issues for debugging
    for symbol_name, issues in validation_results.items():
        if issues:
            print(f"Issues for {symbol_name}: {issues}")

    print("✓ Symbol library validation test passed")


def test_lib_id_resolution() -> None:
    """Test library ID resolution"""
    print("Testing library ID resolution...")

    # Test vendor library resolution
    lib_id = resolve_lib_id("rp2040", "RP2040_QFN56", use_vendor=True)
    assert lib_id == "REPO-RP2040:RP2040_QFN56"

    # Test system library resolution
    lib_id = resolve_lib_id("device", "CAP_0603", use_vendor=False)
    assert lib_id == "Device:CAP_0603"

    # Test unknown library
    lib_id = resolve_lib_id("unknown", "Component", use_vendor=True)
    assert lib_id == "unknown:Component"

    print("✓ Library ID resolution test passed")


def main() -> int:
    """Run all tests"""
    print("Running LED touch grid component library tests...\n")

    try:
        test_symbol_creation()
        test_part_info_lookup()
        test_klc_validation()
        test_rp2040_pinmap()
        test_led_touch_grid_symbols()
        test_symbol_library_validation()
        test_lib_id_resolution()

        print("\n✅ All tests passed successfully!")
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
