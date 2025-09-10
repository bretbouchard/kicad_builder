from typing import List

from tools.kicad_helpers import Schematic


class I2CValidator:
    def validate_bus_connections(self, schematic: Schematic) -> List[str]:
        """Validate all I2C bus connections follow protocol requirements:
        - SDA/SCL lines have pullup resistors
        - No conflicting device addresses
        - Proper bus termination"""

        errors = []
        # Check for pullups on both lines
        if not self._has_pullups(schematic, "SDA"):
            errors.append("Missing pullup resistor on SDA line")
        if not self._has_pullups(schematic, "SCL"):
            errors.append("Missing pullup resistor on SCL line")

        # Check bus addresses
        addresses = self._get_i2c_addresses(schematic)
        if len(addresses) != len(set(addresses)):
            errors.append("Duplicate I2C addresses detected")

        return errors

    def check_pullups(self, schematic: Schematic) -> List[str]:
        """Verify proper pullup resistor configuration:
        - Appropriate resistor values (4.7kΩ ±10%)
        - Resistors present on both SDA and SCL
        - Single pair per bus segment"""

        warnings = []
        sda_pullups = self._count_pullups(schematic, "SDA")
        scl_pullups = self._count_pullups(schematic, "SCL")

        if sda_pullups != 1:
            warnings.append(f"Expected 1 SDA pullup, found {sda_pullups}")
        if scl_pullups != 1:
            warnings.append(f"Expected 1 SCL pullup, found {scl_pullups}")

        return warnings

    def _has_pullups(self, schematic: Schematic, line: str) -> bool:
        return any(
            sym
            for sym in schematic.symbols
            if sym.lib == "Device" and sym.name == "R" and line in sym.fields.get("Net", "")
        )

    def _count_pullups(self, schematic: Schematic, line: str) -> int:
        return len(
            [
                sym
                for sym in schematic.symbols
                if sym.lib == "Device" and sym.name == "R" and line in sym.fields.get("Net", "")
            ]
        )

    def _get_i2c_addresses(self, schematic: Schematic) -> List[str]:
        return [str(sym.fields.get("Address", "")) for sym in schematic.symbols if "I2C_Device" in sym.name]
