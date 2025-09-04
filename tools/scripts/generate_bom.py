"""Generate a minimal BOM from pinmap JSON files.

Produces CSV with columns:
    refdes,component,footprint,package,qty,value,part_number,manufacturer,pins_used,mapping_file

Heuristics implemented:
- RP2040 detection -> U? RP2040 footprint (QFN56 or PICO module)
- USB connector detection (USB_DP/USB_DM) -> J? USB-C
- Add decoupling caps (C?) per mapping when power nets exist

Usage: generate_bom.py --out path/to/bom.csv [--filter rp2040] [--no-common]
"""

import argparse
import json
import pathlib
import csv
import sys
from typing import Optional, Dict, Any, Iterable


def load_mappings(dir_path: pathlib.Path) -> Iterable[tuple[str, dict]]:
    for p in sorted(dir_path.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf8"))
        except Exception:
            continue
        yield p.name, data


def guess_components(mapping_name: str, data: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Return list of BOM rows (component entries) for a mapping."""
    rows: list[Dict[str, Any]] = []
    lname = mapping_name.lower()
    pkg = str(data.get("package", ""))
    sig_map = data.get("signal_to_pin") or {}

    # Main MCU
    if "rp2040" in lname:
        if "qfn" in pkg.lower() or "56" in pkg:
            footprint = "REPO-MCU-QFN56"
        else:
            footprint = "REPO-PICO-MODULE"
        rows.append(
            {
                "refdes": "U1",
                "component": "RP2040",
                "footprint": footprint,
                "package": pkg,
                "qty": 1,
                "pins_used": len(sig_map),
                "mapping_file": mapping_name,
            }
        )

    # USB connector if USB signals present
    if any(s.startswith("USB_") or s in ("USB_DP", "USB_DM", "USB_VDD") for s in sig_map.keys()):
        rows.append(
            {
                "refdes": "J1",
                "component": "USB-C-RECEPTACLE",
                "footprint": "USB-C",
                "package": "USB-C",
                "qty": 1,
                "pins_used": 0,
                "mapping_file": mapping_name,
            }
        )

    # Common decoupling caps heuristic: one per power rail
    # (IOVDD/DVDD/ADC_AVDD/USB_VDD)
    power_nets = [n for n in ("IOVDD", "DVDD", "ADC_AVDD", "USB_VDD") if n in sig_map.keys()]
    if power_nets:
        # individual caps per rail, suggest 0.1uF 0603
        for i, net in enumerate(power_nets, start=1):
            rows.append(
                {
                    "refdes": f"C{i}",
                    "component": "CAP_0.1uF",
                    "footprint": "0603",
                    "package": "CAP_0603",
                    "qty": 1,
                    "value": "0.1uF",
                    "pins_used": 0,
                    "mapping_file": mapping_name,
                }
            )
        # a single bulk cap if VREG_VIN present
        if "VREG_VIN" in sig_map.keys() or "VREG_VIN" in data.get("pin_to_signal", {}).values():
            rows.append(
                {
                    "refdes": f"C{len(power_nets)+1}",
                    "component": "CAP_10uF",
                    "footprint": "1206",
                    "package": "CAP_1206",
                    "qty": 1,
                    "value": "10uF",
                    "pins_used": 0,
                    "mapping_file": mapping_name,
                }
            )

    # RUN pull-up resistor heuristic
    if "RUN" in sig_map.keys() or "RUN" in data.get("pin_to_signal", {}).values():
        rows.append(
            {
                "refdes": "R1",
                "component": "R_PULLUP",
                "footprint": "0603",
                "package": "R_0603",
                "qty": 1,
                "value": "10k",
                "pins_used": 0,
                "mapping_file": mapping_name,
            }
        )

    return rows


def main(
    out_path: Optional[pathlib.Path] = None,
    include_filter: Optional[str] = None,
    include_common: bool = True,
) -> None:
    # Compute repository root by searching upward from this file's
    # directory for a marker (a 'tools' subdirectory or pyproject.toml).
    # This is robust when the script is executed from different CWDs or
    # inside pre-commit/temporary environments.
    repo_root = None
    this_file = pathlib.Path(__file__).resolve()
    for p in [this_file] + list(this_file.parents):
        if (p / "tools").exists() or (p / "pyproject.toml").exists() or (p / ".git").exists():
            repo_root = p
            break
    if repo_root is None:
        # last-resort: fall back to the previous heuristic
        repo_root = pathlib.Path(__file__).resolve().parents[2]
    mapping_dir = repo_root / "tools" / "vendor_symbols" / "mappings"
    if not mapping_dir.exists():
        print(f"No mappings dir at {mapping_dir}", file=sys.stderr)
        raise SystemExit(1)

    all_rows: list[Dict[str, Any]] = []
    for name, data in load_mappings(mapping_dir):
        if include_filter and include_filter.lower() not in name.lower():
            continue
        comps = guess_components(name, data)
        if not include_common:
            # filter out common parts (CAP_0.1uF, USB_CONNECTOR)
            comps = [c for c in comps if c.get("component") not in ("CAP_0.1uF", "USB_CONNECTOR")]
        all_rows.extend(comps)

    if out_path is None:
        out_path = repo_root / "tools" / "output" / "bom.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure unique refdes across all mappings by reassigning
    # sequential designators
    counters: dict[str, int] = {}

    def prefix_for(component_name: str) -> str:
        cn = (component_name or "").upper()
        if cn.startswith("RP2040") or cn.startswith("U"):
            return "U"
        if "USB" in cn or cn.startswith("J"):
            return "J"
        if cn.startswith("CAP") or cn.startswith("C"):
            return "C"
        if cn.startswith("R") or "RESISTOR" in cn:
            return "R"
        if cn.startswith("TP"):
            return "TP"
        return "P"

    for r in all_rows:
        pref = prefix_for(r.get("component", ""))
        n = counters.get(pref, 0) + 1
        counters[pref] = n
        r["refdes"] = f"{pref}{n}"

    fieldnames = [
        "refdes",
        "component",
        "footprint",
        "package",
        "qty",
        "value",
        "part_number",
        "manufacturer",
        "pins_used",
        "mapping_file",
    ]
    # Group identical passives into single BOM lines with qty and refdes ranges
    grouped: list[dict] = []
    seen: Dict[tuple, Dict[str, Any]] = {}
    for r in all_rows:
        key = (r.get("component"), r.get("value"), r.get("footprint"))
        if key in seen:
            entry = seen[key]
            entry["qty"] = int(entry.get("qty", 1)) + int(r.get("qty", 1))
            # maintain list of refdes for later formatting
            entry.setdefault("refdes_list", [])
            entry["refdes_list"].append(r.get("refdes"))
        else:
            # shallow copy
            entry = dict(r)
            entry["qty"] = int(entry.get("qty", 1))
            # start refdes_list with the current refdes
            entry["refdes_list"] = [r.get("refdes")]
            seen[key] = entry
            grouped.append(entry)

    # Simple parts database heuristics
    for e in grouped:
        comp = (e.get("component") or "").upper()
        if comp == "CAP_0.1UF" or comp.startswith("CAP_0.1") or comp.startswith("CAP_0.1U"):
            e.setdefault("part_number", "CC0603KRX7R9BB104")
            e.setdefault("manufacturer", "Murata")
        elif comp == "CAP_10UF" or comp.startswith("CAP_10"):
            e.setdefault("part_number", "GRM31CR61E106KA12L")
            e.setdefault("manufacturer", "Murata")
        elif comp == "R_PULLUP" or "PULLUP" in comp:
            e.setdefault("part_number", "RC0603FR-0710KL")
            e.setdefault("manufacturer", "Yageo")

    def _format_refdes_list(refs: list[str]) -> str:
        """Convert a list like ['C1','C2','C3','C5'] into 'C1-C3,C5'."""
        # normalize and sort by numeric suffix
        by_prefix: dict[str, list[int]] = {}
        for r in refs:
            if not r:
                continue
            # split prefix letters from number suffix
            prefix = "".join([c for c in r if not c.isdigit()])
            num_s = "".join([c for c in r if c.isdigit()])
            try:
                num = int(num_s)
            except Exception:
                # fallback: keep as-is
                by_prefix.setdefault(r, []).append(None)  # type: ignore
                continue
            by_prefix.setdefault(prefix, []).append(num)

        parts: list[str] = []
        for prefix, nums in by_prefix.items():
            nums = sorted(set(n for n in nums if n is not None))  # type: ignore
            if not nums:
                continue
            # compress consecutive ranges
            start = prev = nums[0]
            ranges: list[tuple[int, int]] = []
            for n in nums[1:]:
                if n == prev + 1:
                    prev = n
                    continue
                ranges.append((start, prev))
                start = prev = n
            ranges.append((start, prev))
            for a, b in ranges:
                if a == b:
                    parts.append(f"{prefix}{a}")
                else:
                    parts.append(f"{prefix}{a}-{prefix}{b}")

        return ",".join(parts)

    with out_path.open("w", newline="", encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in grouped:
            # fill optional fields to avoid missing-key errors
            r.setdefault("value", "")
            r.setdefault("part_number", "")
            r.setdefault("manufacturer", "")
            # format refdes list into compact ranges for readability
            ref_list = r.pop("refdes_list", None)
            if ref_list:
                r["refdes"] = _format_refdes_list(ref_list)
            writer.writerow(r)

    print(f"Wrote BOM to {out_path}")


def cli(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Generate BOM from mapping JSONs")
    p.add_argument(
        "--out",
        type=pathlib.Path,
        help="output CSV path",
    )
    p.add_argument(
        "--filter",
        dest="filter",
        help="substring filter for mapping filenames",
    )
    p.add_argument(
        "--no-common",
        dest="no_common",
        action="store_true",
        help="exclude common parts like caps/connectors",
    )
    args = p.parse_args(argv)
    main(
        out_path=args.out,
        include_filter=args.filter,
        include_common=not args.no_common,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
