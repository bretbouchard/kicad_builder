import pytest
from tools.lib_map import (
    resolve_symbol_footprint,
    validate_library_completeness,
    validate_symbol_library_legacy,
)


def test_resolve_symbol_footprint():
    # Test known component
    result = resolve_symbol_footprint("RP2040")
    assert result["symbol"] == "RP2040:RP2040"
    assert result["footprint"] == "MCU_QFN56.pretty:RP2040-QFN56"

    # Test unknown component
    result = resolve_symbol_footprint("INVALID_PART")
    assert result["symbol"] is None
    assert result["footprint"] is None


def test_validate_library_completeness():
    required = ["RP2040", "APA102", "USB-C"]
    assert validate_library_completeness(required) is True

    with pytest.raises(ValueError) as excinfo:
        validate_library_completeness(["RP2040", "MISSING_PART"])
    assert "Missing symbol/footprint mapping for: ['MISSING_PART']" in str(excinfo.value)


def test_validate_symbol_library():
    # Test component name validation
    components = ["RP2040", "LED", "MISSING_PART"]
    missing = validate_symbol_library_legacy(components)
    assert missing == ["MISSING_PART"], "Should identify missing components"
