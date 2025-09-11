#!/usr/bin/env python3
"""generate_pinmap.py

Convert a CSV (pin,signal) into a canonical pinmap JSON or
pretty-print/validate an existing JSON.

Usage:
  python3 generate_pinmap.py input.csv --out out.json --package RP2040
  python3 generate_pinmap.py mapping.json --out out.json

The script accepts '-' as input to read from stdin. If input has a
.csv or .tsv suffix it will be parsed as CSV, otherwise it is treated
as JSON and validated for a `pin_to_signal` mapping.
`pin_to_signal` mapping.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict


def csv_to_pinmap(path: Path, package: str = "") -> Dict[str, Any]:
    pin_to_signal: Dict[str, str] = {}
    with path.open() as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            if row[0].strip().lower().startswith("pin"):
                continue
            pin = row[0].strip()
            sig = row[1].strip() if len(row) > 1 else ""
            pin_to_signal[pin] = sig
    return {
        "package": package or "unknown",
        "description": f"Generated from {path.name}",
        "pin_to_signal": pin_to_signal,
        "signal_to_pin": {},
    }


def json_validate(path: Path) -> Dict[str, Any]:
    try:
        data_raw = json.loads(path.read_text())
        # Narrow the raw JSON to the expected mapping shape for type checkers
        data: Dict[str, Any] = data_raw
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON in {path}: {e}")
    if "pin_to_signal" not in data:
        raise SystemExit("JSON missing pin_to_signal key")
    return data


def build_reverse(map_obj: Dict[str, str]) -> Dict[str, list[object]]:
    rev: Dict[str, list[object]] = {}
    for p, s in map_obj.items():
        if p.isdigit():
            val: object = int(p)
        else:
            val = p
        rev.setdefault(s, []).append(val)
    return rev


def main() -> None:
    parser = argparse.ArgumentParser(description=("Generate or validate a canonical pinmap JSON"))
    parser.add_argument(
        "input",
        help="Input CSV/JSON file path or '-' for stdin",
    )
    parser.add_argument(
        "--package",
        help="Package name to set when generating from CSV",
    )
    parser.add_argument(
        "--out",
        help="Output JSON file (defaults to stdout)",
    )
    args = parser.parse_args()

    inp = args.input
    if inp == "-":
        # write stdin to a temp file so we can reuse existing functions
        data = sys.stdin.read()
        if not data.strip():
            raise SystemExit("No data on stdin")
        # infer if JSON or CSV by first non-space char
        first = data.lstrip()[0]
        tmp = Path("/tmp/generate_pinmap_stdin.tmp")
        tmp.write_text(data)
        p = tmp
        is_csv = first.isdigit() or first.isalpha() or first == "p"
    else:
        p = Path(inp)
        if not p.exists():
            raise SystemExit(f"File not found: {p}")
        if not p.is_file():
            raise SystemExit(f"Input is not a file: {p}")
        is_csv = p.suffix.lower() in (".csv", ".tsv")

    if is_csv:
        out_obj = csv_to_pinmap(p, package=args.package or "")
        out_obj["signal_to_pin"] = build_reverse(out_obj["pin_to_signal"])
    else:
        out_obj = json_validate(p)
        if "signal_to_pin" not in out_obj or not out_obj["signal_to_pin"]:
            out_obj["signal_to_pin"] = build_reverse(out_obj["pin_to_signal"])

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(out_obj, indent=2))
        print(f"Wrote {args.out}")
    else:
        print(json.dumps(out_obj, indent=2))


if __name__ == "__main__":
    main()
