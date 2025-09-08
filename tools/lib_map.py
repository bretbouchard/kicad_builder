# Symbol/footprint mapping for LED Touch Grid

SYMBOL_FOOTPRINT_MAP = {
    "RP2040": {"symbol": "RP2040:RP2040", "footprint": "MCU_QFN56.pretty:RP2040-QFN56"},
    "APA102": {"symbol": "LED_Programmable:APA102", "footprint": "LED_SMD:LED_RGB_PLCC4_5.0x5.0mm"},
    "SK9822": {"symbol": "LED_Programmable:SK9822", "footprint": "LED_SMD:LED_RGB_PLCC4_5.0x5.0mm"},
    "Touch_Pad_19x19mm": {"symbol": "Custom:Touch_Pad", "footprint": "Custom:Touch_Pad_19x19mm"},
    "USB-C": {"symbol": "Connector_USB:USB_C_Receptacle", "footprint": "Connector_USB:CUSB-B-RA_SMD"},
    "SWD": {
        "symbol": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    },
    "LED": {"symbol": "LED:LED", "footprint": "LED_SMD:LED_RGB_PLCC4_5.0x5.0mm"},
    "Connector": {
        "symbol": "Connector_Generic:Conn_01x04",
        "footprint": "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical",
    },
    # Add more as needed
}


def resolve_symbol_footprint(component_name):
    """Return symbol and footprint for a given component name."""
    return SYMBOL_FOOTPRINT_MAP.get(component_name, {"symbol": None, "footprint": None})


def validate_library_completeness(required_components):
    """Check that all required components have symbol/footprint mappings."""
    missing = [c for c in required_components if c not in SYMBOL_FOOTPRINT_MAP]
    if missing:
        raise ValueError(f"Missing symbol/footprint mapping for: {missing}")
    return True


# Stubs for compatibility
class Symbol:
    """Stub Symbol class for import compatibility."""

    def __init__(self, *args, **kwargs):
        pass


def resolve_lib_id(lib, name):
    """Stub resolver for library IDs. Returns 'lib:name'."""
    return f"{lib}:{name}"


def validate_klc_rules(*args, **kwargs):
    """Stub for KLC rule validation."""
    return True
