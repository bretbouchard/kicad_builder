"""
BOM Generator (US-9 Implementation)
Generates normalized BOM with manufacturer/supplier data from lib_map
"""

import csv
from pathlib import Path
from typing import List, Dict, Optional, TypedDict

import sys

# When this script is executed directly (e.g. via subprocess in tests), Python
# doesn't automatically add the repository root to sys.path which makes
# absolute imports like `from tools.lib_map import ...` fail. Insert the repo
# root at the front of sys.path so `tools` can be imported reliably. Keep
# this manipulation near the top so import machinery behaves predictably.
try:
    # Normal import path when running inside the project environment.
    from tools.lib_map import get_part_info  # Absolute import path
except Exception:  # pragma: no cover - fallback for script execution in tests
    _REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    from tools.lib_map import get_part_info


class Component(TypedDict):
    Ref: str
    Value: str
    Footprint: str
    Part: str


class ComponentGroup(TypedDict):
    refs: List[str]
    value: str
    footprint: str
    mpn: Optional[str]
    manufacturer: Optional[str]
    supplier: Optional[str]
    supplier_pn: Optional[str]


def generate_bom(netlist_path: str, output_dir: str = "out") -> str:
    """Main BOM generation function meeting US-9 requirements"""
    components = parse_netlist(netlist_path)
    normalized = normalize_components(components)
    return write_bom_csv(normalized, output_dir)


def parse_netlist(netlist_path: str) -> List[Component]:
    """Parse KiCad netlist into structured components"""
    components = []
    current: Dict[str, str] = {}

    with open(netlist_path) as f:
        for line in f:
            line = line.strip()
            if line == "$COMPONENT":
                current = {}
            elif line == "$ENDCOMPONENT":
                components.append(
                    Component(
                        Ref=current.get("Ref", ""),
                        Value=current.get("Value", ""),
                        Footprint=current.get("Footprint", ""),
                        Part=current.get("Part", ""),
                    )
                )
            else:
                if " " in line:
                    key, value = line.split(" ", 1)
                    current[key] = value
    return components


def normalize_components(components: List[Component]) -> Dict[str, ComponentGroup]:
    """Group and enrich components with library data"""
    groups: Dict[str, ComponentGroup] = {}

    for comp in components:
        part_info = get_part_info(comp["Part"]) if comp.get("Part") else None
        # Use a string key derived from value and footprint to keep dict keys
        # simple and mypy-friendly.
        key = f"{comp.get('Value','')}|{comp.get('Footprint','')}"

        if key not in groups:
            groups[key] = ComponentGroup(
                refs=[],
                value=comp.get("Value", ""),
                footprint=comp.get("Footprint", ""),
                mpn=(part_info.get("mpn") if part_info else None),
                manufacturer=(part_info.get("manufacturer") if part_info else None),
                supplier=(part_info.get("supplier") if part_info else None),
                supplier_pn=(part_info.get("supplier_pn") if part_info else None),
            )

        groups[key]["refs"].append(comp.get("Ref", ""))

    return groups


def write_bom_csv(groups: Dict[str, ComponentGroup], output_dir: str) -> str:
    """Write normalized BOM data to CSV file"""
    output_path = Path(output_dir) / "bom.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Reference",
                "Quantity",
                "Value",
                "Footprint",
                "MPN",
                "Manufacturer",
                "Supplier",
                "Supplier PN",
            ],
        )
        writer.writeheader()

        for group in groups.values():
            writer.writerow(
                {
                    "Reference": ",".join(group["refs"]),
                    "Quantity": len(group["refs"]),
                    "Value": group["value"],
                    "Footprint": group["footprint"],
                    "MPN": group.get("mpn", ""),
                    "Manufacturer": group.get("manufacturer", ""),
                    "Supplier": group.get("supplier", ""),
                    "Supplier PN": group.get("supplier_pn", ""),
                }
            )

    return str(output_path)


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="generate_bom.py",
        description="Generate a normalized BOM from a KiCad netlist",
    )
    parser.add_argument(
        "netlist",
        nargs="?",
        help="Path to the KiCad netlist file",
    )
    # Backwards-compatible positional output directory/file. Tests and some
    # callers pass the output directory as the second positional argument.
    parser.add_argument(
        "out_pos",
        nargs="?",
        help="Output directory or CSV file path for BOM (optional)",
    )
    parser.add_argument(
        "--out",
        dest="out",
        help="Output directory for BOM (default: out)",
    )

    args = parser.parse_args()

    # If netlist not provided, attempt to find a generated netlist in the
    # repository. Common locations include: out/*.net and
    # hardware/projects/*/out/*.net.
    repo_root = Path(__file__).resolve().parents[2]
    if not args.netlist:
        candidates = list(repo_root.glob("**/*.net"))
        if candidates:
            args.netlist = str(candidates[0])
        else:
            parser.print_usage()
            print("Either provide a netlist path or generate a netlist first.")
            sys.exit(1)

    # Decide output target. Prefer positional `out_pos` if provided
    # (keeps backwards compatibility with tests). Otherwise fall back to
    # the --out flag or default to "out".
    out_target = args.out_pos or args.out or "out"
    if out_target.endswith(".csv"):
        # caller provided a file; ensure parent dir exists and use filename
        out_dir = str(Path(out_target).parent)
        bom_file_parent = out_dir
    else:
        out_dir = out_target

    bom_path = generate_bom(args.netlist, out_dir)

    # If caller asked for a specific CSV file path, move the generated file
    # into that exact location.
    generated = Path(bom_path)
    if out_target.endswith(".csv"):
        dest = Path(out_target)
        dest.parent.mkdir(parents=True, exist_ok=True)
        generated.replace(dest)
        bom_path = str(dest)
    print(f"Generated BOM at: {bom_path}")
