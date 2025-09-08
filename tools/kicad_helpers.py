"""kicad_helpers.py

Small helpers to build KiCad schematic S-expression files (starter scaffolding).

This module provides a tiny, well-documented API that generator scripts can
import while we build out a full .kicad_sch writer targeted at KiCad 9.

Note: this file is intentionally a scaffold — it makes it easy to extend the
writer to produce fully-valid KiCad 9 S-expression schematics. For now it
focuses on clear data structures and a simple `write()` placeholder.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple, Any

try:
    # When tools/ is added to sys.path (generators), this resolves as
    # a top-level module. When imported as a package, fall back to
    # relative import.
    from lib_map import resolve_lib_id
except Exception:
    from .lib_map import resolve_lib_id
import json
import os


@dataclass
class Symbol:
    lib: str
    name: str
    ref: str
    at: Tuple[float, float] = (0.0, 0.0)
    orientation: int = 0
    value: Optional[str] = None
    footprint: Optional[str] = None
    unit: int = 1
    fields: Optional[Dict[str, Any]] = None


@dataclass
class Wire:
    a: str
    b: str


@dataclass
class Net:
    name: str
    pins: List[str]


class Schematic:
    """A lightweight schematic model.

    Use this model from generator scripts. Calling `write()` will emit a
    minimal human-readable representation in `out/` and a small JSON summary.
    The full KiCad S-expression writer will be implemented iteratively.
    """

    def __init__(self, title: str = "untitled"):
        self.title = title
        self.symbols: List[Symbol] = []
        self.wires: List[Wire] = []
        self.nets: List[Net] = []
        self.power_flags: List[Dict[str, Any]] = []

    def add_symbol(self, sym: Symbol) -> None:
        self.symbols.append(sym)

    def add_wire(self, a: str, b: str) -> None:
        self.wires.append(Wire(a, b))

    def add_net(self, name: str, pins: List[str]) -> None:
        """Add a logical net consisting of named pins (e.g. ['U1.1', 'R1.2'])."""
        self.nets.append(Net(name=name, pins=pins))

    def add_power_flag(self, name: str, at: Optional[Tuple[float, float]] = None) -> None:
        self.power_flags.append({"name": name, "at": at})

    def add_gnd(self, at: Optional[Tuple[float, float]] = None) -> None:
        self.add_power_flag("GND", at=at)

    def summary(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "symbols": [asdict(s) for s in self.symbols],
            "wires": [asdict(w) for w in self.wires],
        }

    def write(self, out_dir: str = "out") -> None:
        """Write a minimal representation and JSON summary to `out/`.

        This is a scaffold: when you're ready we'll extend this to emit
        fully-valid KiCad 9 `.kicad_sch` S-expressions.
        """
        os.makedirs(out_dir, exist_ok=True)
        # human-readable dump for early inspection
        txt_path = os.path.join(out_dir, f"{self.title}.sch.txt")
        with open(txt_path, "w") as f:
            f.write(f"# Schematic: {self.title}\n")
            f.write("# Symbols:\n")
            for s in self.symbols:
                f.write(f"- {s.ref}: {s.lib}/{s.name} at {s.at} ori={s.orientation}\n")
            f.write("# Wires:\n")
            for w in self.wires:
                f.write(f"- {w.a} -> {w.b}\n")
        json_path = os.path.join(out_dir, f"{self.title}_summary.json")
        with open(json_path, "w") as f:
            json.dump(self.summary(), f, indent=2)

        # Also emit the (kicad_sch) file so generators get a single command
        # to produce both the human-readable dump and the KiCad S-expression.
        try:
            self.write_kicad_sch(out_dir=out_dir)
        except Exception:
            # Keep the simple dump even if the richer writer fails.
            pass

    def _emit_symbol_sexp(self, s: Symbol) -> str:
        # Emit a richer symbol block including lib_id, unit, value,
        # optional footprint and arbitrary fields.
        # lib may be given as 'LibName' or 'Library/Name' — normalize to a
        # placeholder lib_id format: 'Library:Name'. Generators can later
        # populate real lib_ids or vendor a symbol library.
        # Resolve a stable lib_id using the mapping layer. Generators can
        # change use_vendor in lib_map if they vendor symbol files.
        lib_id = resolve_lib_id(s.lib, s.name)

        value = s.value if s.value is not None else s.name
        footprint = f' (footprint "{s.footprint}")' if s.footprint else ""
        fields_block = ""
        if s.fields:
            for k, v in s.fields.items():
                fields_block += f'    (property "{k}" "{v}")\n'

        return (
            f'  (symbol (lib_id "{lib_id}") (ref "{s.ref}") '
            f'(unit {s.unit}) (value "{value}")\n'
            f"    (at {s.at[0]} {s.at[1]}) (orientation {s.orientation})\n"
            f"{footprint}\n"
            f"{fields_block}  )\n"
        )

    def write_kicad_sch(self, out_dir: str = "out") -> None:
        """Emit a minimal KiCad-like S-expression `.kicad_sch` file.

        This writer produces a simple, KiCad-inspired S-expression that lists
        symbols and nets. It is intentionally minimal and will be iterated on
        as we add support for full KiCad fields and properties.
        """
        os.makedirs(out_dir, exist_ok=True)
        sch_path = os.path.join(out_dir, f"{self.title}.kicad_sch")
        with open(sch_path, "w") as f:
            f.write("(kicad_sch (version 1) (generator tools.kicad_helpers))\n")
            f.write(f'(title "{self.title}")\n')
            f.write("(components\n")
            for s in self.symbols:
                f.write(self._emit_symbol_sexp(s))
            f.write(")\n")

            if self.nets:
                f.write("(nets\n")
                for n in self.nets:
                    # net name
                    f.write(f'  (net (name "{n.name}")')
                    for p in n.pins:
                        # p expected like "U1.1" or "GND". Try to emit a
                        # KiCad-style node: (node (ref U1) (pin 1)). If the
                        # pin part is not an integer, emit it as a string.
                        if "." in p:
                            ref, pin = p.split(".", 1)
                            # attempt to normalize pin to int
                            try:
                                int_pin = int(pin)
                                f.write(f' (node (ref "{ref}") (pin {int_pin}))')
                            except Exception:
                                f.write(f' (node (ref "{ref}") (pin "{pin}"))')
                        else:
                            # power symbols or named nodes
                            f.write(f' (node (ref "{p}"))')
                    f.write(")\n")
                f.write(")\n")

            if self.power_flags:
                f.write("(power_flags\n")
                for pf in self.power_flags:
                    at = pf.get("at")
                    if at:
                        f.write(("  (power_flag (name %s) (at %s %s))\n" % (pf["name"], at[0], at[1])))
                    else:
                        f.write("  (power_flag (name %s))\n" % (pf["name"]))
                f.write(")\n")

            f.write(")\n")


if __name__ == "__main__":
    # simple smoke test when run directly
    sch = Schematic("smoke_test")
    sch.add_symbol(Symbol(lib="Device", name="R", ref="R1", at=(10, 20)))
    sch.add_symbol(Symbol(lib="Device", name="C", ref="C1", at=(30, 20)))
    sch.add_wire("R1.1", "C1.1")
    sch.write(out_dir="out")


@dataclass
class HierarchicalPin:
    """A hierarchical sheet pin exposed to parent/child sheets."""

    name: str
    direction: str = "in"  # 'in', 'out', or 'inout'
    sheet_ref: Optional[str] = None

    def __post_init__(self):
        """Validate direction after initialization."""
        valid_directions = {"in", "out", "inout"}
        if self.direction not in valid_directions:
            raise ValueError(f"Invalid direction '{self.direction}'. Must be one of: {valid_directions}")


@dataclass
class Sheet:
    """Container for a child sheet and its hierarchical pins."""

    name: str
    schematic: Schematic
    hierarchical_pins: "List[HierarchicalPin]" = field(default_factory=list)

    def add_hier_pin(self, name: str, direction: str = "in") -> None:
        self.hierarchical_pins.append(HierarchicalPin(name=name, direction=direction, sheet_ref=self.name))


class HierarchicalSchematic(Schematic):
    """Extend Schematic with basic hierarchical-sheet support.

    This is a lightweight API used by generators that need to compose
    multiple child sheets and express hierarchical pin connections.
    """

    def __init__(self, title: str = "untitled"):
        super().__init__(title=title)
        # map sheet name -> Sheet
        self.sheets: Dict[str, Sheet] = {}
        # list of tuples (parent_pin, child_pin) using 'Sheet.pin' notation
        self.hier_connections: List[Tuple[str, str]] = []

    def add_sheet(self, sheet: Sheet) -> None:
        if sheet.name in self.sheets:
            raise ValueError(f"Sheet with name '{sheet.name}' already exists")
        self.sheets[sheet.name] = sheet

    def connect_hier_pins(
        self,
        parent_sheet: str,
        parent_pin: str,
        child_sheet: str,
        child_pin: str,
    ) -> None:
        """Record a hierarchical connection between a parent sheet pin
        and a child sheet pin.

        Pins are recorded as strings like 'power.V5' and 'mcu.VDD' and
        stored in the form ("parent.pin", "child.pin").
        """
        parent = f"{parent_sheet}.{parent_pin}"
        child = f"{child_sheet}.{child_pin}"
        self.hier_connections.append((parent, child))

    def _find_pin(self, sheet_name: str, pin_name: str) -> Optional[HierarchicalPin]:
        """Return the HierarchicalPin object for a given sheet and pin name.

        Returns None if the sheet or pin cannot be found.
        """
        sheet = self.sheets.get(sheet_name)
        if not sheet:
            return None
        for p in sheet.hierarchical_pins:
            if p.name == pin_name:
                return p
        return None

    def validate_hierarchy(self) -> None:
        """Validate hierarchical connections between sheets.

        Checks performed:
        - Both referenced sheets exist.
        - Both referenced hierarchical pins exist on their sheets.
        - Direction compatibility: parent pin must be able to drive ("out" or
          "inout"); child pin must be able to receive ("in" or "inout").

        Raises ValueError with an explanatory message on failure.
        """
        for parent, child in self.hier_connections:
            print(f"Validating connection: {parent} -> {child}")
            try:
                p_sheet, p_pin = parent.split(".", 1)
                c_sheet, c_pin = child.split(".", 1)
            except Exception:
                raise ValueError(f"Invalid hierarchical connection format: {parent} -> {child}")

            print(f"  Parent: {p_sheet}.{p_pin}, Child: {c_sheet}.{c_pin}")

            # Check for missing pins first (before direction validation)
            # Special case: root sheet pins need to be created dynamically
            if p_sheet == "root":
                # Create a temporary pin for root sheet validation
                p_obj = HierarchicalPin(name=p_pin, direction="out", sheet_ref=p_sheet)
                print(f"  Created root pin: {p_pin} (out)")
            else:
                p_obj = self._find_pin(p_sheet, p_pin)
                if p_obj is None:
                    raise ValueError(f"Parent pin '{p_pin}' not found on sheet '{p_sheet}'")
                print(f"  Found parent pin: {p_pin} ({p_obj.direction})")

            c_obj = self._find_pin(c_sheet, c_pin)
            if c_obj is None:
                raise ValueError(f"Child pin '{c_pin}' not found on sheet '{c_sheet}'")
            print(f"  Found child pin: {c_pin} ({c_obj.direction})")

            # direction checks: parent must be able to drive; child must be able
            # to receive
            if p_obj.direction not in ("out", "inout"):
                raise ValueError(
                    f"Parent pin '{p_pin}' on '{p_sheet}' has direction "
                    f"'{p_obj.direction}' and cannot drive '{c_sheet}.{c_pin}'"
                )
            if c_obj.direction not in ("in", "inout"):
                raise ValueError(
                    f"Child pin '{c_pin}' on '{c_sheet}' has direction "
                    f"'{c_obj.direction}' and cannot be driven by "
                    f"'{p_sheet}.{p_pin}'"
                )
            print(f"  Connection {parent} -> {child} is valid")

    def summary(self) -> Dict[str, Any]:
        base = super().summary()
        base["sheets"] = {
            n: {
                "title": s.schematic.title,
                "pins": [asdict(p) for p in s.hierarchical_pins],
            }
            for n, s in self.sheets.items()
        }
        base["hier_connections"] = self.hier_connections

        # Add ERC validation status to summary
        erc_errors = []
        erc_status = "passed"

        try:
            self.validate_hierarchy()
        except ValueError as e:
            erc_status = "failed"
            erc_errors.append(str(e))

        try:
            self.validate_power_decoupling()
        except ValueError as e:
            erc_status = "failed"
            erc_errors.append(str(e))

        try:
            self.validate_i2c_pullups()
        except ValueError as e:
            erc_status = "failed"
            erc_errors.append(str(e))

        base["erc_status"] = erc_status
        base["erc_errors"] = erc_errors

        return base

    def write(self, out_dir: str = "out") -> None:
        """Write the root schematic summary plus sheet summaries and a small
        hierarchy JSON that lists sheets and hierarchical connections.
        """
        os.makedirs(out_dir, exist_ok=True)
        # Validate connections before emitting files
        self.validate_hierarchy()

        # Write the root schematic files (human-readable + kicad_sch)
        super().write(out_dir=out_dir)

        # Write sheet summaries and a combined hierarchy JSON
        sheets_block: Dict[str, Any] = {}
        for name, sheet in self.sheets.items():
            # ensure each child sheet also writes its kicad_sch and summary
            sheet_out = os.path.join(out_dir, "sheets")
            os.makedirs(sheet_out, exist_ok=True)
            sheet.schematic.write(out_dir=sheet_out)

            sheets_block[name] = {
                "title": sheet.schematic.title,
                "file": os.path.join("sheets", f"{sheet.schematic.title}.kicad_sch"),
                "symbols": [asdict(s) for s in sheet.schematic.symbols],
                "hierarchical_pins": [asdict(p) for p in sheet.hierarchical_pins],
            }

        hier_path = os.path.join(out_dir, f"{self.title}_hierarchy.json")
        with open(hier_path, "w") as f:
            json.dump(
                {"sheets": sheets_block, "connections": self.hier_connections},
                f,
                indent=2,
            )

    def validate_power_decoupling(self) -> None:
        """Validate power decoupling across root + child sheets.

        Rules:
        - If any MCU (RP2040 / MCU / IC) present anywhere, require a 100nF cap
        - If any LED array (LED / APA102 / SK9822) present anywhere,
          require a bulk cap (>=470uF typical)
        """
        # Aggregate symbols from root and all child sheets
        all_symbols = list(self.symbols)
        for sheet in self.sheets.values():
            all_symbols.extend(sheet.schematic.symbols)

        mcu_found = any(
            ("RP2040" in s.name) or ("RP2040" in (s.value or "")) or ("MCU" in s.lib) or ("IC" in s.lib)
            for s in all_symbols
        )

        led_found = any(("LED" in s.lib) or ("APA102" in s.name) or ("SK9822" in s.name) for s in all_symbols)

        decoupling_cap_found = any(
            s.lib == "Device" and s.name == "C" and any(tag in (s.value or "") for tag in ("100nF", "0.1uF", "104"))
            for s in all_symbols
        )

        bulk_cap_found = any(
            s.lib == "Device"
            and s.name == "C"
            and any(
                tag in (s.value or "")
                for tag in ("1000µF", "1000uF", "470µF", "470uF", "220µF", "220uF", "47µF", "47uF")
            )
            for s in all_symbols
        )

        if mcu_found and not decoupling_cap_found:
            raise ValueError("Missing 100nF decoupling capacitor near VDD pins")
        if led_found and not bulk_cap_found:
            raise ValueError("Missing bulk capacitor for LED power rail")

    def validate_i2c_pullups(self) -> None:
        """Validate I2C pull-up resistor configuration (recursive across sheets).

        Rules:
        - If any I2C-related net (I2C*, SDA, SCL) exists anywhere (root or child sheets),
          each distinct net must have exactly 1 or 2 pull-up resistors (covering SDA & SCL)
        - Resistor values must be in the 1kΩ–10kΩ range (inclusive)
        - More than 2 resistors tied to the same I2C net => error (multiple pull-up sets)
        """
        # Aggregate nets from root + child sheets
        all_nets = list(self.nets)
        for sheet in self.sheets.values():
            all_nets.extend(sheet.schematic.nets)

        # Collect I2C nets
        i2c_nets: List[str] = []
        for net in all_nets:
            if isinstance(net, dict):
                net_name = net.get("name", "")
            else:
                net_name = getattr(net, "name", "")
            if any(tag in net_name for tag in ("I2C", "SDA", "SCL")):
                i2c_nets.append(net_name)

        if not i2c_nets:
            return  # No I2C context to validate

        # Aggregate symbols from root + sheets
        all_symbols = list(self.symbols)
        for sheet in self.sheets.values():
            all_symbols.extend(sheet.schematic.symbols)

        pullups = {}
        for symbol in all_symbols:
            if symbol.lib == "Device" and symbol.name == "R":
                if hasattr(symbol, "fields") and symbol.fields:
                    net_name = symbol.fields.get("Net")
                else:
                    net_name = None
                if not net_name:
                    continue
                if any(i2c in net_name for i2c in i2c_nets):
                    # Parse value into kΩ
                    raw = symbol.value or ""
                    resistance_k = 0.0
                    try:
                        if raw.endswith("k") or "kΩ" in raw:
                            resistance_k = float(raw.replace("kΩ", "").replace("k", ""))
                        elif raw.endswith("Ω"):
                            resistance_k = float(raw.replace("Ω", "")) / 1000.0
                        else:
                            resistance_k = float(raw)  # assume already in kΩ if plain
                    except ValueError:
                        resistance_k = 0.0
                    pullups.setdefault(net_name, []).append(resistance_k)

        for net_name in i2c_nets:
            vals = pullups.get(net_name, [])
            if not vals:
                raise ValueError(f"Missing pull-up resistors for I2C net '{net_name}'")
            if len(vals) > 2:
                raise ValueError(f"Multiple pull-up sets detected for I2C net '{net_name}'")
            for r in vals:
                if r < 1 or r > 10:
                    raise ValueError(f"Invalid pull-up value {r}kΩ for I2C net '{net_name}'. Must be 1-10kΩ")

    def run_full_erc(self) -> None:
        """Run complete ERC validation including all custom rules.

        This method performs all validation checks:
        1. Hierarchical connection validation
        2. Power decoupling validation
        3. I2C pull-up validation

        Raises ValueError with descriptive message if any validation fails.
        """
        errors = []

        try:
            self.validate_hierarchy()
        except ValueError as e:
            errors.append(f"Hierarchy validation failed: {e}")

        try:
            self.validate_power_decoupling()
        except ValueError as e:
            errors.append(f"Power decoupling validation failed: {e}")

        try:
            self.validate_i2c_pullups()
        except ValueError as e:
            errors.append(f"I2C pull-up validation failed: {e}")

        if errors:
            raise ValueError("\n".join(errors))
