"""kicad_helpers.py

Small helpers to build KiCad schematic S-expression files (starter scaffolding).

This module provides a tiny, well-documented API that generator scripts can
import while we build out a full .kicad_sch writer targeted at KiCad 9.

Note: this file is intentionally a scaffold — it makes it easy to extend the
writer to produce fully-valid KiCad 9 S-expression schematics. For now it
focuses on clear data structures and a simple `write()` placeholder.
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
try:
    # When tools/ is added to sys.path (generators), this resolves as
    # a top-level module. When imported as a package, fall back to
    # relative import.
    from lib_map import resolve_lib_id  # type: ignore
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

    def summary(self) -> dict:
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
        footprint = (
            f" (footprint \"{s.footprint}\")" if s.footprint else ""
        )
        fields_block = ""
        if s.fields:
            for k, v in s.fields.items():
                fields_block += f"    (property \"{k}\" \"{v}\")\n"

        return (
            (
                f"  (symbol (lib_id \"{lib_id}\") (ref \"{s.ref}\") "
                f"(unit {s.unit}) (value \"{value}\")\n"
                f"    (at {s.at[0]} {s.at[1]}) (orientation {s.orientation})\n"
                f"{footprint}\n"
                f"{fields_block}  )\n"
            )
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
            f.write(f"(title \"{self.title}\")\n")
            f.write("(components\n")
            for s in self.symbols:
                f.write(self._emit_symbol_sexp(s))
            f.write(")\n")

            if self.nets:
                f.write("(nets\n")
                for n in self.nets:
                    # net name
                    f.write(f"  (net (name \"{n.name}\")")
                    for p in n.pins:
                        # p expected like "U1.1" or "GND". Try to emit a
                        # KiCad-style node: (node (ref U1) (pin 1)). If the
                        # pin part is not an integer, emit it as a string.
                        if "." in p:
                            ref, pin = p.split('.', 1)
                            # attempt to normalize pin to int
                            try:
                                int_pin = int(pin)
                                f.write(
                                    f" (node (ref \"{ref}\") (pin {int_pin}))"
                                )
                            except Exception:
                                f.write(
                                    f" (node (ref \"{ref}\") (pin \"{pin}\"))"
                                )
                        else:
                            # power symbols or named nodes
                            f.write(f" (node (ref \"{p}\"))")
                    f.write(")\n")
                f.write(")\n")

            if self.power_flags:
                f.write("(power_flags\n")
                for p in self.power_flags:
                    at = p.get("at")
                    if at:
                        f.write(f"  (power_flag (name {p['name']}) (at {at[0]} {at[1]}))\n")
                    else:
                        f.write(f"  (power_flag (name {p['name']}))\n")
                f.write(")\n")

            f.write(")\n")



if __name__ == "__main__":
    # simple smoke test when run directly
    sch = Schematic("smoke_test")
    sch.add_symbol(Symbol(lib="Device", name="R", ref="R1", at=(10, 20)))
    sch.add_symbol(Symbol(lib="Device", name="C", ref="C1", at=(30, 20)))
    sch.add_wire("R1.1", "C1.1")
    sch.write(out_dir="out")
