"""Simple library mapping/resolution for schematic generators.

This module implements a tiny mapping layer so generators can either
(1) reference vendored/in-repo libraries or (2) map to the user's local
KiCad symbol libraries. The goal is to make emitted `lib_id`s deterministic
and easily switchable.

The mapping here is deliberately minimal — extend it with real mappings
or a metadata file if you vendor real KiCad .lib files into the repo.
"""

from typing import Dict, Optional
import os

# If you vendor symbol files into the repo, you can prefix lib_ids with
# a stable vendor tag. Generators can pass use_vendor=True to prefer
# the vendored names.
DEFAULT_VENDOR_PREFIX = "REPO"
# Toggle to prefer vendored-style lib_ids. Change to False to emit local
# Library:SymbolName style lib_ids.
USE_VENDOR = True

# Simple logical -> library mapping. Keys are logical lib names used by
# generators (e.g. "MCU", "Power", "LEDs"), values are physical KiCad
# library names (without symbol name) to use when resolving lib_id.
MAPPING: Dict[str, str] = {
    "MCU": "MCU",
    "Power": "Power",
    "Device": "Device",
    "LEDs": "LEDs",
}

# Default RP2040 symbol variant. Can be overridden by environment variable
# SYMBOL_VARIANT=QFN or SYMBOL_VARIANT=PICO
SYMBOL_VARIANT = os.environ.get("SYMBOL_VARIANT", "QFN").upper()


def resolve_lib_id(lib: str, symbol_name: str, use_vendor: Optional[bool] = None) -> str:
    """Return a lib_id for the given logical library and symbol name.

    If use_vendor is True, the function returns a vendor-prefixed lib_id
    (format "{lib}:{symbol}"). If False, it returns a mapping to the local
    KiCad library name (same format here; adjust if you use full lib paths).
    """
    # If caller didn't pass an explicit preference, use module-level toggle.
    effective_vendor = USE_VENDOR if use_vendor is None else use_vendor

    lib_physical = MAPPING.get(lib, lib)
    if effective_vendor:
        # Vendor-style lib_id: REPO-Library:SymbolName — map to a vendored
        # library filename (e.g. 'REPO-MCU') that we place under
        # tools/vendor_symbols/. Users can add these to their sym-lib-table.
        vendored_lib = f"{DEFAULT_VENDOR_PREFIX}-{lib_physical}"
        # Allow override for MCU logical lib to choose a specific symbol
        if lib_physical == "MCU" and SYMBOL_VARIANT == "PICO":
            return f"{vendored_lib}:RP2040-PICO-Module"
        return f"{vendored_lib}:{symbol_name}"

    # Local fallback: standard Library:SymbolName
    return f"{lib_physical}:{symbol_name}"
