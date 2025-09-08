"""Compatibility adapter for SKiDL's kicad8 parser used in tests.

This module provides a small runtime shim that patches
`skidl.tools.kicad8.lib.parse_lib_part` to be more permissive when
symbol fixtures use nested units with pins. It attempts to populate
`part.unit` and pins when the upstream parser didn't for some reason
in the current environment.

This is a non-invasive, test-time shim intended to live in the repo
so we don't have to edit site-packages permanently.
"""

from typing import Any, List, Optional, Tuple, Dict


def install() -> None:
    """Install the repo-local kicad8 adapter shim.

    This attempts to make SKiDL's kicad8 symbol parsing more permissive
    for the repo's test fixtures by loading missing symbol definitions
    from disk and creating units/pins as a best-effort fallback.
    """
    try:
        from simp_sexp import Sexp
        from skidl.pin import pin_types
        from skidl import Pin
        from skidl.utilities import num_to_chars, to_list
        import skidl.tools.kicad8.lib as _kicad8_lib
        import skidl.tools as _skidl_tools
    except Exception:
        # Environment doesn't have SKiDL or Sexp; nothing to do.
        return

    _orig = getattr(_kicad8_lib, "parse_lib_part", None)
    if _orig is None:
        return

    pin_io_type_translation: Dict[str, Any] = {
        "input": pin_types.INPUT,
        "output": pin_types.OUTPUT,
        "bidirectional": pin_types.BIDIR,
        "tri_state": pin_types.TRISTATE,
        "passive": pin_types.PASSIVE,
        "free": pin_types.FREE,
        "unspecified": pin_types.UNSPEC,
        "power_in": pin_types.PWRIN,
        "power_out": pin_types.PWROUT,
        "open_collector": pin_types.OPENCOLL,
        "open_emitter": pin_types.OPENEMIT,
        "no_connect": pin_types.NOCONNECT,
    }

    def _parse_pins_and_make_units(part: Any, part_defn_arg: Optional[Any] = None) -> Optional[List[Tuple[int, Any]]]:
        """Inspect part.part_defn (Sexp) and create units/pins when missing.

        This is a permissive, best-effort parser that expects nested
        `symbol` nodes whose names end with '_<major>_<minor>' and that
        contain `pin` child nodes.
        """
        try:
            part_defn = part_defn_arg if part_defn_arg is not None else getattr(part, "part_defn", None)
            if not part_defn:
                return None

            # Ensure we have an Sexp wrapper so indexing/searching works.
            try:
                if not isinstance(part_defn, Sexp):
                    part_defn = Sexp(part_defn)
            except Exception:
                return None

            # Find nested 'symbol' entries.
            units = []
            for u in part_defn:
                if isinstance(u, list) and u and str(u[0]).lower() == "symbol":
                    units.append(u)
            if not units:
                return None

            unit_nums: List[int] = []

            for unit in units:
                try:
                    unit_name = unit[1]
                    # Expect something like 'RP2040_0_0' -> take last two parts
                    parts = str(unit_name).split("_")
                    if len(parts) < 2:
                        continue
                    major = int(parts[-2])
                except Exception:
                    continue

                # Collect immediate child 'pin' entries
                pins = []
                for item in unit:
                    if isinstance(item, list) and item and isinstance(item[0], str) and item[0].lower() == "pin":
                        pins.append(item)
                if not pins and major == 0:
                    # Skip global unit without pins
                    continue

                unit_nums.append(major)

                for pin in pins:
                    try:
                        if len(pin) > 1:
                            pin_func_key = str(pin[1]).lower()
                        else:
                            pin_func_key = "unspecified"
                        pin_func = pin_io_type_translation.get(pin_func_key, pin_types.UNSPEC)
                        pin_name = ""
                        pin_number = None
                        pin_x = pin_y = pin_angle = 0
                        pin_length = None
                        for item in pin:
                            item = to_list(item)
                            if not item:
                                continue
                            token_name = str(item[0]).lower()
                            if token_name == "name":
                                pin_name = item[1]
                            elif token_name == "number":
                                pin_number = item[1]
                            elif token_name == "at":
                                try:
                                    pin_x, pin_y, pin_angle = item[1:4]
                                except Exception:
                                    pass
                            elif token_name == "length":
                                pin_length = item[1]

                        part.add_pins(
                            Pin(
                                name=pin_name,
                                num=pin_number,
                                func=pin_func,
                                unit=major,
                                x=pin_x,
                                y=pin_y,
                                length=pin_length,
                                rotation=pin_angle,
                                orientation=pin_angle,
                            )
                        )
                    except Exception:
                        continue

            # Create units for discovered unit numbers.
            created: List[Tuple[int, Any]] = []
            for num in sorted(set(unit_nums)):
                try:
                    label = "u" + num_to_chars(num)
                    u = part.make_unit(label, unit=num)
                    created.append((num, u))
                except Exception:
                    continue

            return created
        except Exception:
            return None

    def _wrapped_parse_lib_part(part: Any, partial_parse: Any) -> None:
        # Try to ensure part.part_defn exists so the original parser can run.
        try:
            if not getattr(part, "part_defn", None):
                lib = getattr(part, "lib", None)
                if lib:
                    try:
                        tmpl = lib.get_parts_by_name(part._name, allow_failure=True)
                        if tmpl:
                            if isinstance(tmpl, list):
                                tmpl_part = tmpl[0]
                            else:
                                tmpl_part = tmpl
                            if getattr(tmpl_part, "part_defn", None):
                                part.part_defn = tmpl_part.part_defn
                                try:
                                    if not isinstance(part.part_defn, Sexp):
                                        part.part_defn = Sexp(part.part_defn)
                                except Exception:
                                    pass
                    except Exception:
                        pass

                # If still missing, search symbol files in common env dirs.
                if not getattr(part, "part_defn", None):
                    import os
                    from glob import glob

                    envvars = (
                        "KICAD8_SYMBOL_DIR",
                        "KICAD_SYMBOL_DIR",
                        "KICAD6_SYMBOL_DIR",
                    )

                    candidates = []
                    for envvar in envvars:
                        p = os.environ.get(envvar)
                        if p:
                            candidates.append(p)
                    candidates.append(".")

                    search_path = "/kicad_symbol_lib/symbol"
                    for base in candidates:
                        try:
                            fname = part._name + "*.kicad_sym"
                            pattern = os.path.join(base, fname)
                            for path in glob(pattern):
                                try:
                                    enc = "utf-8"
                                    with open(path, "r", encoding=enc) as fh:
                                        txt = fh.read()
                                except Exception:
                                    try:
                                        enc = "latin-1"
                                        with open(path, "r", encoding=enc) as fh:
                                            txt = fh.read()
                                    except Exception:
                                        continue
                                try:
                                    sexp = Sexp(txt)
                                except Exception:
                                    continue
                                sp = search_path
                                for sym in sexp.search(sp, ignore_case=True):
                                    try:
                                        if str(sym[1]) == part._name:
                                            if not isinstance(sym, Sexp):
                                                sym = Sexp(sym)
                                            part.part_defn = sym
                                            break
                                    except Exception:
                                        continue
                                if getattr(part, "part_defn", None):
                                    break
                        except Exception:
                            continue
        except Exception:
            pass

            # Preserve a copy of the current part_defn so we can do a fallback
            # parse after the original parser runs (it may clear part.part_defn).
            saved_part_defn: Optional[Any] = getattr(part, "part_defn", None)

            # Call original parser; ignore errors and attempt a fallback parse.
            try:
                _orig(part, partial_parse)
            except Exception:
                pass

            # If units/pins are still missing, attempt best-effort creation using
            # the saved part_defn (since the original parser may have cleared it).
            try:
                if not getattr(part, "unit", None) or len(part.unit) == 0:
                    _parse_pins_and_make_units(part, part_defn_arg=saved_part_defn)
            except Exception:
                pass

    # Install wrapper into kicad8 loader and tool_modules.
    try:
        _kicad8_lib.parse_lib_part = _wrapped_parse_lib_part
    except Exception:
        pass
    try:
        if getattr(_skidl_tools, "tool_modules", None) and _skidl_tools.tool_modules.get("kicad8"):
            _skidl_tools.tool_modules["kicad8"].parse_lib_part = _wrapped_parse_lib_part
    except Exception:
        pass

    # Patch SchLib.get_parts_by_name to load part_defn for template parts.
    try:
        from skidl.schlib import SchLib as _SchLib

        _orig_get_parts_by_name = _SchLib.get_parts_by_name

        def _patched_get_parts_by_name(self: Any, name: Any, *args: Any, **kwargs: Any) -> Any:
            parts = _orig_get_parts_by_name(self, name, *args, **kwargs)
            if isinstance(parts, list):
                parts_list = parts
            elif parts:
                parts_list = [parts]
            else:
                parts_list = []
            for prt in parts_list:
                try:
                    if not getattr(prt, "part_defn", None):
                        import os
                        from glob import glob

                        candidates = []
                        for envvar in (
                            "KICAD8_SYMBOL_DIR",
                            "KICAD_SYMBOL_DIR",
                            "KICAD6_SYMBOL_DIR",
                        ):
                            p = os.environ.get(envvar)
                            if p:
                                candidates.append(p)
                        candidates.append(".")

                        for base in candidates:
                            try:
                                fname = prt._name + "*.kicad_sym"
                                pattern = os.path.join(base, fname)
                                for path in glob(pattern):
                                    try:
                                        enc = "utf-8"
                                        with open(path, "r", encoding=enc) as fh:
                                            txt = fh.read()
                                    except Exception:
                                        try:
                                            enc = "latin-1"
                                            with open(path, "r", encoding=enc) as fh:
                                                txt = fh.read()
                                        except Exception:
                                            continue
                                    try:
                                        sexp = Sexp(txt)
                                    except Exception:
                                        continue
                                    sp = "/kicad_symbol_lib/symbol"
                                    for sym in sexp.search(sp, ignore_case=True):
                                        try:
                                            if str(sym[1]) == prt._name:
                                                if not isinstance(sym, Sexp):
                                                    sym = Sexp(sym)
                                                prt.part_defn = sym
                                                break
                                        except Exception:
                                            continue
                                    if getattr(prt, "part_defn", None):
                                        break
                            except Exception:
                                continue
                except Exception:
                    continue
            return parts

        _SchLib.get_parts_by_name = _patched_get_parts_by_name
    except Exception:
        pass
