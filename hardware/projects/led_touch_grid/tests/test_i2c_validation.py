import pytest

from hardware.projects.led_touch_grid.validation.i2c.core import I2CValidator
from tools.kicad_helpers import Schematic, Symbol


@pytest.fixture
def validator() -> I2CValidator:
    return I2CValidator()


@pytest.fixture
def valid_schematic() -> Schematic:
    """Schematic with valid pullups and unique addresses"""
    s = Schematic("valid_i2c_schematic")
    s.add_symbol(Symbol(lib="Device", name="R", ref="R1", value="4.7k", fields={"Net": "SDA"}))
    s.add_symbol(Symbol(lib="Device", name="R", ref="R2", value="4.7k", fields={"Net": "SCL"}))
    s.add_symbol(
        Symbol(
            lib="MCU",
            name="I2C_Device",
            ref="U1",
            value="I2C_Controller",
            fields={"Address": "0x42"},
        )
    )
    # Connect the nets properly
    s.add_net("SDA", ["R1.Net", "U1.SDA"])
    s.add_net("SCL", ["R2.Net", "U1.SCL"])
    s.add_net("3V3", ["R1.2", "R2.2"])
    return s


@pytest.fixture
def invalid_schematic() -> Schematic:
    """Schematic missing pullups with duplicate addresses"""
    s = Schematic("invalid_i2c_schematic")
    s.add_symbol(Symbol(lib="MCU", name="I2C_Device", ref="U1", value="Controller", fields={"Address": "0x42"}))
    s.add_symbol(Symbol(lib="MCU", name="I2C_Device", ref="U2", value="Peripheral", fields={"Address": "0x42"}))
    # Create explicit but invalid connections
    s.add_net("SDA", ["U1.SDA", "U2.SDA"])
    s.add_net("SCL", ["U1.SCL", "U2.SCL"])
    return s


def test_valid_i2c_bus(validator: I2CValidator, valid_schematic: Schematic) -> None:
    errors = validator.validate_bus_connections(valid_schematic)
    assert not errors


def test_missing_pullups(validator: I2CValidator, invalid_schematic: Schematic) -> None:
    errors = validator.validate_bus_connections(invalid_schematic)
    assert "Missing pullup resistor on SDA line" in errors
    assert "Missing pullup resistor on SCL line" in errors


def test_duplicate_addresses(validator: I2CValidator, invalid_schematic: Schematic) -> None:
    errors = validator.validate_bus_connections(invalid_schematic)
    assert "Duplicate I2C addresses detected" in errors


def test_pullup_warnings(validator: I2CValidator) -> None:
    s = Schematic()
    s.add_symbol(Symbol(lib="Device", name="R", ref="R1", value="4.7k", fields={"Net": "SDA"}))
    s.add_symbol(Symbol(lib="Device", name="R", ref="R2", value="4.7k", fields={"Net": "SCL"}))
    s.add_symbol(Symbol(lib="Device", name="R", ref="R3", value="4.7k", fields={"Net": "SDA"}))

    warnings = validator.check_pullups(s)
    assert any("Expected 1 SDA pullup, found 2" in w for w in warnings)
    assert not any("SCL pullup" in w for w in warnings)
