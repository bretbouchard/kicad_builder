"""snapmagic: local parts search + ingest utility

Usage:
  python tools/snapmagic.py --from-bom projects/button_bar/bom.csv
  python tools/snapmagic.py APA-102-2020-256-8 SN74HC4051

Behavior:
 - Searches `inbox/` for matching part folders/files (.kicad_mod, .kicad_sym).
 - Copies found files into `projects/button_bar/components/footprints/` and
   `projects/button_bar/components/symbols/` respectively.
 - If a part is not found, fabricates a minimal placeholder footprint and
   symbol and marks the mapping source as "fabricated".
 - Emits a mapping JSON at
   `projects/button_bar/snapmagic_mapping.json` with entries for each part.

This is intentionally conservative: it won't try to be clever about
editing arbitrary schematic libraries; it will update JSON-format symbol
files (SnapEDA-style) to include a footprints entry where possible.
"""

import argparse
import csv
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "inbox"
PROJECT_FOOTPRINTS = ROOT / "projects" / "button_bar" / "components" / "footprints"
PROJECT_SYMBOLS = ROOT / "projects" / "button_bar" / "components" / "symbols"
MAPPING_FILE = ROOT / "projects" / "button_bar" / "snapmagic_mapping.json"


def read_bom(bom_path: Path) -> List[str]:
    parts: List[str] = []
    if not bom_path.exists():
        return parts
    with bom_path.open() as f:
        reader = csv.DictReader(f)
        for r in reader:
            # assume BOM has a 'part' or 'name' column
            part = r.get("part") or r.get("name") or r.get("Reference")
            if part:
                parts.append(part.strip())
    return parts


def find_in_inbox(part: str) -> Dict[str, Path]:
    """Return dict with keys 'footprint' and 'symbol' if found in inbox."""
    out: Dict[str, Path] = {}
    if not INBOX.exists():
        return out
    # naive search: look for files or folders containing the part string
    for p in INBOX.rglob("*"):
        name = p.name
        if part.lower() in name.lower():
            if p.suffix == ".kicad_mod":
                out["footprint"] = p
            if p.suffix == ".kicad_sym" or p.suffix == ".kicad_symbol":
                out["symbol"] = p
            # also accept folder with part name that contains files
            if p.is_dir():
                for f in p.iterdir():
                    if f.suffix == ".kicad_mod" and "footprint" not in out:
                        out["footprint"] = f
                    if f.suffix in (".kicad_sym", ".kicad_symbol") and "symbol" not in out:
                        out["symbol"] = f
    return out


def safe_copy(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    # if dst exists, create a .bak with incremental suffix
    if dst.exists():
        i = 1
        while True:
            bak = dst.with_suffix(dst.suffix + f".bak{i}")
            if not bak.exists():
                dst.rename(bak)
                break
            i += 1
    shutil.copy2(src, dst)
    return dst


def fabricate_footprint(part: str) -> Path:
    """Create a minimal placeholder .kicad_mod footprint for the part."""
    PROJECT_FOOTPRINTS.mkdir(parents=True, exist_ok=True)
    name = f"FAB-{part}.kicad_mod"
    p = PROJECT_FOOTPRINTS / name
    if p.exists():
        return p
    content = (
        f"(module {part} (layer F.Cu) (tedit 0)\n"
        '  (descr "Fabricated placeholder footprint - verify dimensions before production")\n'
        "  (pads)\n"
        ")\n"
    )
    p.write_text(content)
    return p


def fabricate_symbol(part: str) -> Path:
    PROJECT_SYMBOLS.mkdir(parents=True, exist_ok=True)
    name = f"FAB-{part}.kicad_sym"
    p = PROJECT_SYMBOLS / name
    if p.exists():
        return p
    # Write a tiny KiCad JSON-format symbol to be friendly to SnapEDA-style files
    symbol = {
        "kicad_symbol": {
            "footprints": [{"name": f"{part}", "description": "fabricated placeholder - set proper footprint"}],
            "pins": [],
            "properties": {"fabricated": "true"},
        }
    }
    p.write_text(json.dumps(symbol, indent=2))
    return p


def update_symbol_json(symbol_path: Path, footprint_name: str) -> bool:
    """If symbol is JSON-format, try to add/update footprints entry.
    Returns True if updated, False otherwise.
    """
    try:
        data = json.loads(symbol_path.read_text())
    except Exception:
        return False
    if not isinstance(data, dict) or "kicad_symbol" not in data:
        return False
    ks = data["kicad_symbol"]
    ks["footprints"] = [{"name": footprint_name}]
    symbol_path.write_text(json.dumps(data, indent=2))
    return True


def process_part(part: str) -> Dict[str, Optional[str]]:
    found = find_in_inbox(part)
    entry: Dict[str, Optional[str]] = {
        "part": part,
        "footprint": None,
        "symbol": None,
        "source": None,
    }
    if "footprint" in found:
        dst = safe_copy(found["footprint"], PROJECT_FOOTPRINTS)
        entry["footprint"] = str(dst.relative_to(ROOT))
        entry["source"] = "snap_inbox"
    else:
        dst = fabricate_footprint(part)
        entry["footprint"] = str(dst.relative_to(ROOT))
        entry["source"] = "fabricated"

    if "symbol" in found:
        dsts = safe_copy(found["symbol"], PROJECT_SYMBOLS)
        entry["symbol"] = str(dsts.relative_to(ROOT))
        # try safe update of JSON-format symbol to point at footprint
        try:
            fp = entry.get("footprint")
            if fp is not None:
                update_symbol_json(dsts, Path(fp).name)
        except Exception:
            pass
    else:
        dsts = fabricate_symbol(part)
        entry["symbol"] = str(dsts.relative_to(ROOT))

    return entry


def run(parts: List[str], do_write: bool = True) -> List[Dict[str, Optional[str]]]:
    mapping: List[Dict[str, Optional[str]]] = []
    for p in parts:
        entry = process_part(p)
        mapping.append(entry)
    if do_write:
        MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
        MAPPING_FILE.write_text(json.dumps(mapping, indent=2))
    return mapping


def main(argv: Optional[List[str]] = None):
    ap = argparse.ArgumentParser()
    ap.add_argument("parts", nargs="*", help="Part names to search/install")
    ap.add_argument("--from-bom", help="Path to BOM CSV to extract part names")
    ap.add_argument(
        "--no-write",
        action="store_true",
        help="Don't write mapping file (dry run)",
    )
    args = ap.parse_args(argv)

    parts: List[str] = []
    if args.from_bom:
        parts.extend(read_bom(Path(args.from_bom)))
    parts.extend(args.parts)

    if not parts:
        print("No parts supplied; either pass part names or --from-bom <path>")
        return 2

    mapping = run(parts, do_write=not args.no_write)
    print(json.dumps(mapping, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
