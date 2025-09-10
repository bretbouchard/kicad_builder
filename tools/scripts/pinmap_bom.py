"""Simple pinmap/BOM runner.

Scans tools/vendor_symbols/mappings/*.json and writes a CSV summary to stdout.
"""

import csv
import json
import pathlib
import sys


def load_mappings(dir_path: pathlib.Path):
    for p in sorted(dir_path.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf8"))
        except Exception:
            continue
        yield p.name, data


def summarize(mapping_name, data):
    package = data.get("package", "")
    notes = data.get("notes", "")
    signal_to_pin = data.get("signal_to_pin") or {}
    for signal, pins in signal_to_pin.items():
        yield {
            "mapping": mapping_name,
            "package": package,
            "signal": signal,
            "pins": ",".join(map(str, pins)),
            "notes": notes,
        }


def main():
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    mapping_dir = repo_root / "tools" / "vendor_symbols" / "mappings"
    if not mapping_dir.exists():
        print(f"No mappings dir found at {mapping_dir}", file=sys.stderr)
        raise SystemExit(1)

    writer = csv.DictWriter(sys.stdout, fieldnames=["mapping", "package", "signal", "pins", "notes"])
    writer.writeheader()
    for name, data in load_mappings(mapping_dir):
        for row in summarize(name, data):
            writer.writerow(row)


if __name__ == "__main__":
    main()
