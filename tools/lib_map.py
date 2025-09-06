from typing import TypedDict, Optional, cast, List
from dataclasses import dataclass


class PartInfo(TypedDict):
    mpn: Optional[str]
    manufacturer: Optional[str]
    supplier: Optional[str]
    supplier_pn: Optional[str]


@dataclass
class Symbol:
    """Lightweight symbol model used by tests.

    Mirrors the minimal shape expected by unit tests in
    `hardware/projects/*/tests`.
    """
    name: str
    pins: List[str]
    footprint: str


def resolve_lib_id(lib: str, name: str, use_vendor: bool = True) -> str:
    """Resolve a stable lib_id for a given library/name.

    This is a small compatibility shim used by generator scaffolding and
    tests. It supports a couple of repo-vendored library names and
    falls back to KiCad system libraries when `use_vendor` is False.
    """
    repo_map = {
        "device": "REPO-Device",
        "leds": "REPO-LEDs",
    }

    key = lib.lower()
    if key in repo_map and use_vendor:
        return f"{repo_map[key]}:{name}"
    if not use_vendor:
        # Only allow known system-library fallbacks in this mode.
        allowed_system_libs = {"device", "leds"}
        if key in allowed_system_libs:
            return f"{lib.title()}:{name}"
        raise ValueError(f"Unknown library '{lib}' and vendor lookup failed")


def validate_klc_rules(symbol: Symbol) -> List[str]:
    """Run a very small set of KLC-like checks and return human messages.

    This intentionally keeps checks minimal to support unit tests and
    can be extended later.
    """
    issues: List[str] = []
    if not symbol.footprint:
        issues.append("Missing footprint association")
    if not symbol.pins:
        issues.append("Symbol has no pins")
    return issues


def get_part_info(part_ref: str) -> PartInfo:
    """Dummy implementation - replace with real lookup logic"""
    part_map = {
        "CAP-0603": {
            "mpn": "C0603C104K5RACTU",
            "manufacturer": "Kemet",
            "supplier": "Digi-Key",
            "supplier_pn": "399-1271-1-ND",
        },
        "RES-0603": {
            "mpn": "ERJ-3EKF1002V",
            "manufacturer": "Panasonic",
            "supplier": "Mouser",
            "supplier_pn": "667-ERJ-3EKF1002V",
        },
    }
    default = PartInfo(
        mpn=None,
        manufacturer=None,
        supplier=None,
        supplier_pn=None,
    )
    return cast(PartInfo, {**default, **part_map.get(part_ref, {})})
